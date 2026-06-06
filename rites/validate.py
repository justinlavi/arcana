#!/usr/bin/env python3
"""Unified validation orchestrator - runs Arcana or grimoire validation rites.

Usage:
    python3 rites/validate.py              # sequential (default)
    python3 rites/validate.py --parallel   # parallel execution
    python3 rites/validate.py --grimoire <path>
    python3 rites/validate.py links frontmatter
    python3 rites/validate.py --only links,frontmatter
    python3 rites/validate.py --exclude orphans
    python3 rites/validate.py --smart      # git-aware: only run validators relevant to changed files
    python3 rites/validate.py --auto       # smart + auto-execute
    python3 rites/validate.py --summary    # sequential, summary-only output

Exit codes: 0 = all passed, 1 = one or more validators failed,
2 = invalid usage (unknown selector, conflicting modes, or empty selection)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from diagnostics import add_output_format_arg, human_label, human_location

RITE_DIR = Path(__file__).resolve().parent
ARCANA_ROOT = Path(os.environ.get("ARCANA_HOME", RITE_DIR.parent))

VALIDATORS_CONTRACT = RITE_DIR / "data" / "validators.json"


def _load_validator_lists():
    """Load the canonical Arcana and grimoire validator sequences."""
    with open(VALIDATORS_CONTRACT, encoding="utf-8") as f:
        data = json.load(f)
    return data["arcana"], data["grimoire"]


ARCANA_RITES, GRIMOIRE_RITES = _load_validator_lists()

MODE_SELECTORS = {"all", "parallel", "smart", "auto", "summary"}


def run_rite(name, profile="arcana", target_root=None):
    """Run a single validation rite. Returns (name, success, report)."""
    target_root = target_root or ARCANA_ROOT
    command = [sys.executable, str(RITE_DIR / name)]
    if profile == "grimoire":
        command.extend(["--grimoire", str(target_root)])
    command.extend(["--format", "json"])

    result = subprocess.run(
        command,
        capture_output=True, text=True,
        env={**os.environ, "ARCANA_HOME": str(ARCANA_ROOT)},
    )
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        report = {
            "validator": Path(name).stem,
            "status": "fail",
            "root": str(target_root),
            "checked": {},
            "summary": {"errors": 1, "warnings": 0, "diagnostics": 1},
            "diagnostics": [
                {
                    "code": "VALIDATE_INVALID_VALIDATOR_REPORT",
                    "severity": "error",
                    "path": str(RITE_DIR / name),
                    "line": None,
                    "message": "validator did not emit a valid JSON diagnostic report",
                    "hint": (result.stdout + result.stderr)[-2000:],
                    "validator": "validate",
                    "docs_reference": "invocations/arc/validators/validators.md",
                }
            ],
        }
    report["returncode"] = result.returncode
    return name, result.returncode == 0, report


def _selector_forms(value):
    """Return normalized selector forms for a validator or user token."""
    stem = Path(value).stem
    if stem.startswith("validate_grimoire_"):
        base = stem.removeprefix("validate_grimoire_")
    elif stem.startswith("validate_"):
        base = stem.removeprefix("validate_")
    else:
        base = stem

    forms = {
        base,
        base.replace("_", "-"),
        stem,
        stem.replace("_", "-"),
    }
    return {form.lower() for form in forms if form}


def _short_selector(value):
    """Return the one canonical short selector token for a validator (e.g. 'links')."""
    stem = Path(value).stem
    for prefix in ("validate_grimoire_", "validate_"):
        if stem.startswith(prefix):
            return stem[len(prefix):].replace("_", "-")
    return stem.replace("_", "-")


def validator_selector_map(profile="arcana"):
    """Map human selector names to validator rite filenames."""
    rites = GRIMOIRE_RITES if profile == "grimoire" else ARCANA_RITES
    selectors = {}
    for rite in rites:
        for form in _selector_forms(rite):
            selectors[form] = rite
    return selectors


def split_selector_tokens(values):
    """Split comma/space separated selector arguments into normalized tokens."""
    tokens = []
    for value in values or []:
        for part in str(value).split(","):
            token = part.strip().lower().replace("_", "-")
            if token:
                tokens.append(token)
    return tokens


def apply_validator_selection(rites, profile="arcana", only=None, exclude=None):
    """Return rites filtered by selector tokens, preserving canonical order."""
    selector_map = validator_selector_map(profile)
    only_tokens = split_selector_tokens(only)
    exclude_tokens = split_selector_tokens(exclude)

    def resolve(tokens, label):
        selected = set()
        unknown = []
        for token in tokens:
            if token in {"all", "*"}:
                selected.update(rites)
                continue
            rite = selector_map.get(token)
            if rite is None:
                unknown.append(token)
            else:
                selected.add(rite)
        if unknown:
            known = ", ".join(sorted({_short_selector(r) for r in rites}))
            raise ValueError(
                f"unknown {label} selector(s): {', '.join(unknown)}. "
                f"Known selectors: all, {known}"
            )
        return selected

    selected = resolve(only_tokens, "validator") if only_tokens else set(rites)
    excluded = resolve(exclude_tokens, "excluded validator") if exclude_tokens else set()
    return [rite for rite in rites if rite in selected and rite not in excluded]


def parse_positional_selectors(selectors):
    """Separate mode words from validator selectors."""
    mode_tokens = []
    validator_tokens = []
    for token in split_selector_tokens(selectors):
        if token in MODE_SELECTORS:
            mode_tokens.append(token)
        else:
            validator_tokens.append(token)
    return mode_tokens, validator_tokens


def git_changed_files(root):
    """Return [(status, path)] for changes vs HEAD, else all tracked files.

    status is a single letter: 'A' added, 'M' modified, 'D' deleted. A rename is
    expanded into a 'D' for the old path and an 'A' for the new path so deletions
    are never lost. The `git ls-files` fallback (no diff) reports every tracked
    file as present ('M').
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-status", "HEAD"],
            capture_output=True, text=True, cwd=str(root),
        )
        if result.returncode == 0 and result.stdout.strip():
            changes = []
            for line in result.stdout.strip().splitlines():
                parts = line.split("\t")
                status = parts[0][:1]
                if status in ("R", "C") and len(parts) >= 3:
                    changes.append(("D", parts[1]))
                    changes.append(("A", parts[2]))
                elif len(parts) >= 2:
                    changes.append((status, parts[1]))
            return changes
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, cwd=str(root),
        )
        if result.returncode == 0:
            return [("M", f) for f in result.stdout.strip().splitlines() if f]
        return []
    except FileNotFoundError:
        return []


def determine_smart_rites(profile="arcana", target_root=None):
    """Determine which validators to run based on changed files."""
    target_root = target_root or ARCANA_ROOT
    changes = git_changed_files(target_root)
    if not changes:
        return list(GRIMOIRE_RITES if profile == "grimoire" else ARCANA_RITES)

    if profile == "grimoire":
        return determine_smart_grimoire_rites(changes, target_root)

    needed = set()
    # Portability and encoding scan path/content globally.
    needed.add("validate_portability.py")
    needed.add("validate_encoding.py")
    for status, f in changes:
        if status == "D":
            # A deleted file can't be read, but its removal must still trigger the
            # structure check (it may be required) and reference checks (a removed
            # page can break inbound links or orphan others).
            needed.add("validate_structure.py")
            if f.endswith(".md"):
                needed.add("validate_links.py")
                needed.add("validate_orphans.py")
            if f.startswith("skills/"):
                needed.add("validate_skill_refs.py")
            continue

        path = target_root / f
        if not path.exists():
            continue

        if re.match(r"^(docs|invocations|formulae|rites)/", f):
            needed.add("validate_structure.py")

        if f.endswith((".md", ".py")):
            needed.add("validate_naming.py")
            needed.add("validate_semantics.py")
            needed.add("validate_security.py")

        if re.match(r"^(invocations|formulae)/.+\.md$", f):
            needed.add("validate_format.py")

        if f.endswith(".md"):
            try:
                content = path.read_text(errors="replace")
                if "](" in content or "[[" in content:
                    needed.add("validate_links.py")
                if "/arc-" in content:
                    needed.add("validate_skill_refs.py")
                if content.startswith("---\n"):
                    needed.add("validate_frontmatter.py")
                    if "authority:" in content:
                        needed.add("validate_provenance.py")
            except OSError:
                pass

            # Any markdown change can affect orphan reachability.
            needed.add("validate_orphans.py")

        # Adding or removing a skill changes which references are valid.
        if f.startswith("skills/"):
            needed.add("validate_skill_refs.py")

    return [r for r in ARCANA_RITES if r in needed] if needed else list(ARCANA_RITES)


def determine_smart_grimoire_rites(changes, target_root):
    """Determine grimoire validators to run based on changed files."""
    needed = set()
    needed.add("validate_portability.py")
    needed.add("validate_encoding.py")

    for status, f in changes:
        if status == "D":
            # A deleted file still needs the structure check (it may be required)
            # and link/orphan checks (a removed page can break references).
            needed.add("validate_grimoire_structure.py")
            if f.endswith(".md"):
                needed.add("validate_links.py")
                needed.add("validate_orphans.py")
            continue

        path = target_root / f
        if not path.exists():
            continue

        if (
            f in {"grimoire.json", "README.md", "log.md"}
            or f.startswith((".obsidian/", "chapters/", "sources/", "inbox/"))
        ):
            needed.add("validate_grimoire_structure.py")

        if f.endswith(".md"):
            needed.add("validate_format.py")
            needed.add("validate_frontmatter.py")
            needed.add("validate_links.py")
            needed.add("validate_orphans.py")
            needed.add("validate_provenance.py")

        if f.startswith("sources/"):
            needed.add("validate_provenance.py")

    return [r for r in GRIMOIRE_RITES if r in needed] if needed else list(GRIMOIRE_RITES)


def render_diagnostics(report):
    for diagnostic in report.get("diagnostics", []):
        label = human_label(diagnostic.get("severity", "error"))
        location = human_location(diagnostic)
        code = diagnostic.get("code", "UNKNOWN")
        print(f"  [{label}] {code} {location}: {diagnostic.get('message', '')}")
        hint = diagnostic.get("hint")
        if hint:
            print(f"          hint: {hint}")


def empty_suite_report(rites, reports, profile, target_root):
    failed = sum(1 for report in reports if report.get("returncode", 1) != 0)
    errors = sum(report.get("summary", {}).get("errors", 0) for report in reports)
    warnings = sum(report.get("summary", {}).get("warnings", 0) for report in reports)
    diagnostics = sum(report.get("summary", {}).get("diagnostics", 0) for report in reports)
    return {
        "validator": "validate",
        "profile": profile,
        "status": "fail" if failed else "pass",
        "root": str(target_root),
        "checked": {"validators": len(rites)},
        "summary": {
            "failed_validators": failed,
            "errors": errors,
            "warnings": warnings,
            "diagnostics": diagnostics,
        },
        "reports": reports,
    }


def emit_suite_report(report, output_format):
    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    if output_format == "jsonl":
        for validator_report in report["reports"]:
            for diagnostic in validator_report.get("diagnostics", []):
                print(json.dumps(diagnostic, sort_keys=True))
        print(json.dumps({"type": "summary", **report["summary"]}, sort_keys=True))


def profile_label(profile):
    """Return a human-facing validation target label."""
    return "Grimoire" if profile == "grimoire" else "Arcana"


def run_sequential(rites, summary_only=False, output_format="human", profile="arcana", target_root=None):
    """Run rites sequentially. Returns number of failures."""
    target_root = target_root or ARCANA_ROOT
    failed = 0
    reports = []
    human = output_format == "human"

    if human and not summary_only:
        print(f"Running {profile_label(profile)} Validations")
        print("=======================================")
        print(f"Target: {target_root}")
        print()

    for rite in rites:
        if human and not summary_only:
            print(f"Running {rite}...")
            print("----------------------------------------")

        name, ok, report = run_rite(rite, profile=profile, target_root=target_root)
        reports.append(report)

        if human and not summary_only:
            render_diagnostics(report)
        else:
            if human:
                if ok:
                    print(f"  {rite}")
                else:
                    print(f"  {rite} FAILED")

        if not ok:
            failed += 1

    suite_report = empty_suite_report(rites, reports, profile, target_root)
    if not human:
        emit_suite_report(suite_report, output_format)

    if human and not summary_only:
        print()
        print("=======================================")

    return failed


def run_parallel(rites, output_format="human", profile="arcana", target_root=None):
    """Run rites in parallel. Returns number of failures."""
    target_root = target_root or ARCANA_ROOT
    failed = 0
    reports = []
    human = output_format == "human"

    if human:
        print(f"Running {profile_label(profile)} Validations in Parallel")
        print("==========================================")
        print(f"Target: {target_root}")
        print()

    results_dir = RITE_DIR / ".artifacts"
    results_dir.mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(run_rite, r, profile, target_root): r
            for r in rites
        }
        for future in as_completed(futures):
            name, ok, report = future.result()
            reports.append(report)

            log_path = results_dir / f"{Path(name).stem}.log"
            log_path.write_text(json.dumps(report, indent=2, sort_keys=True))

            if human:
                if ok:
                    print(f"  {name}")
                else:
                    print(f"  {name} FAILED")
                    render_diagnostics(report)
            if not ok:
                failed += 1

    # Reports arrive in completion order; sort for deterministic output.
    reports.sort(key=lambda report: report.get("validator", ""))
    suite_report = empty_suite_report(rites, reports, profile, target_root)
    if not human:
        emit_suite_report(suite_report, output_format)

    if human:
        print()
        print("==========================================")
    return failed


def _resolve_selection(rite_list, *, profile, only, exclude, explicit):
    """Apply a selector filter to a validator list.

    Returns ``(rites, error)``. ``error`` is a stderr-ready message (and ``rites``
    is None) when a selector is unknown or an explicit selection resolves to no
    validators; otherwise ``error`` is None.
    """
    try:
        selected = apply_validator_selection(
            rite_list, profile=profile, only=only, exclude=exclude
        )
    except ValueError as exc:
        return None, str(exc)
    if explicit and not selected:
        return None, "selection resolved to zero validators"
    return selected, None


def main():
    parser = argparse.ArgumentParser(description="Unified Arcana and grimoire validation orchestrator")
    parser.add_argument(
        "selectors",
        nargs="*",
        help=(
            "Optional validator or mode selectors, e.g. links frontmatter, "
            "smart, auto, summary, parallel, or all"
        ),
    )
    parser.add_argument(
        "--grimoire",
        type=Path,
        help="Validate a grimoire root with the grimoire validator profile",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Comma-separated validator selectors to run, e.g. links,frontmatter",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Comma-separated validator selectors to skip, e.g. orphans",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--parallel", action="store_true", help="Run validators in parallel")
    group.add_argument("--smart", action="store_true", help="Show which validators are relevant")
    group.add_argument("--auto", action="store_true", help="Smart + auto-execute")
    group.add_argument("--summary", action="store_true", help="Summary-only output")
    add_output_format_arg(parser)
    args = parser.parse_args()
    profile = "grimoire" if args.grimoire else "arcana"
    target_root = args.grimoire.expanduser().resolve() if args.grimoire else ARCANA_ROOT
    rites = GRIMOIRE_RITES if profile == "grimoire" else ARCANA_RITES
    mode_tokens, selector_tokens = parse_positional_selectors(args.selectors)

    explicit_modes = [
        name
        for name, enabled in {
            "parallel": args.parallel,
            "smart": args.smart,
            "auto": args.auto,
            "summary": args.summary,
        }.items()
        if enabled
    ]
    requested_modes = [mode for mode in mode_tokens if mode != "all"]
    all_modes = explicit_modes + requested_modes
    if len(set(all_modes)) > 1:
        print(f"Conflicting validation modes: {', '.join(all_modes)}", file=sys.stderr)
        return 2
    if requested_modes:
        selected_mode = requested_modes[0]
        args.parallel = selected_mode == "parallel"
        args.smart = selected_mode == "smart"
        args.auto = selected_mode == "auto"
        args.summary = selected_mode == "summary"

    explicit_selection = bool(args.only or args.exclude or selector_tokens)
    only = [*args.only, *selector_tokens]
    if not (args.smart or args.auto):
        rites, error = _resolve_selection(
            rites, profile=profile, only=only, exclude=args.exclude, explicit=explicit_selection
        )
        if error:
            print(error, file=sys.stderr)
            return 2

    if args.smart:
        smart = determine_smart_rites(profile, target_root)
        smart, error = _resolve_selection(
            smart, profile=profile, only=only, exclude=args.exclude, explicit=explicit_selection
        )
        if error:
            print(error, file=sys.stderr)
            return 2
        if args.format == "human":
            print("Smart Validation - Recommended:")
            for r in smart:
                print(f"  {r}")
            print()
            print("Run with --auto to execute, or individually: python3 rites/<name>.py")
        else:
            report = {
                "validator": "validate",
                "profile": profile,
                "status": "pass",
                "root": str(target_root),
                "checked": {"selected_validators": len(smart)},
                "summary": {
                    "failed_validators": 0,
                    "errors": 0,
                    "warnings": 0,
                    "diagnostics": 0,
                },
                "selected_validators": smart,
                "reports": [],
            }
            emit_suite_report(report, args.format)
        return 0

    if args.auto:
        smart = determine_smart_rites(profile, target_root)
        smart, error = _resolve_selection(
            smart, profile=profile, only=only, exclude=args.exclude, explicit=explicit_selection
        )
        if error:
            print(error, file=sys.stderr)
            return 2
        if args.format == "human":
            print(f"Smart Validation - Running {len(smart)} relevant validator(s)")
            print()
        failed = run_sequential(smart, output_format=args.format, profile=profile, target_root=target_root)
    elif args.parallel:
        failed = run_parallel(rites, output_format=args.format, profile=profile, target_root=target_root)
    elif args.summary:
        failed = run_sequential(rites, summary_only=True, output_format=args.format, profile=profile, target_root=target_root)
    else:
        failed = run_sequential(rites, output_format=args.format, profile=profile, target_root=target_root)

    if failed == 0:
        if args.format == "human":
            print("All validations passed")
        return 0
    else:
        if args.format == "human":
            print(f"{failed} validation(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
