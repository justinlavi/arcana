#!/usr/bin/env python3
"""Agent-legible state surface for the Summoning Rite.

Sister module to `summon_core.py` (the interactive install engine). Where
`summon_core` talks to a human via tagged stdout, this module gives an
orchestrator a machine-readable view of an installation: a read-only
`--check` that reports drift, a `--reconcile` that repairs the offline,
deterministic subset of `RECOVERY.md`, and a durable transcript
(`~/.cache/grimoire/summon-last.json`) so the outcome of any summon-family
operation can be diffed against intent without parsing prose.

Design rules (mirrors the deferred-fragility and autonomy boundaries):

* Pure stdlib. Every entry point is root-parameterized - it takes `home` and
  `arcana_root` explicitly and never reads `summon_core`'s import-time
  `Path.home()` constants for logic (those serve only as production defaults
  in `run_state_command`). Instruction/skill target paths resolve through
  `agent_targets`, which reads `Path.home()` at call time, so they are passed
  in as a seam too.
* `--check` is read-only apart from the owned cache transcript it writes.
* `--reconcile --apply` repairs the library (additively) and re-registers
  skills. It refuses on a base that fails `validate.py` (no repair on a broken
  tree), never deletes a library entry unless `--prune` is given, and never
  rewrites agent instruction blocks (the BEGIN/END vs heading sentinel
  mismatch makes that non-deterministic - it is reported, not performed).
* Network pull is out of scope: updating Arcana itself is the human/RED step
  from `RECOVERY.md`.
"""

from __future__ import annotations

import argparse
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import summon_core
import sync_library
from agent_targets import automatic_instruction_targets, skill_registration_targets
from diagnostics import ResultReporter, add_output_format_arg

SCHEMA_VERSION = 1

# Two idempotency sentinels coexist in the wild: `inject_agent_file` keys off
# the heading, while the template / RECOVERY.md / `/arc-agent-update` use the
# BEGIN/END markers. A block written by either path is "present"; reporting
# only one would mislabel the other as drift and invite a double-injection.
HEADING_SENTINEL = "## Grimoire Knowledge Base"
BEGIN_SENTINEL = "<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->"

NETWORK_PULL_NOTE = "skipped (human-gated; see RECOVERY.md step 2)"


# ---------------------------------------------------------------------------
# Time / identity seams (injectable so transcripts are deterministic in tests)
# ---------------------------------------------------------------------------


def _real_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def default_transcript_path() -> Path:
    """Owned cache location for the last summon-family transcript."""
    return Path.home() / ".cache" / "grimoire" / "summon-last.json"


# ---------------------------------------------------------------------------
# Inspection (read-only)
# ---------------------------------------------------------------------------


def _detect_block_marker(content: str) -> str:
    """Classify how an agent instruction file carries the Grimoire block."""
    has_heading = HEADING_SENTINEL in content
    has_markers = BEGIN_SENTINEL in content
    if has_heading and has_markers:
        return "both"
    if has_heading:
        return "heading"
    if has_markers:
        return "markers"
    return "none"


def _instruction_targets(arcana_root: Path, override: Any) -> list[dict[str, Any]]:
    if override is not None:
        return list(override)
    return automatic_instruction_targets(arcana_root)


def _skill_targets(arcana_root: Path, override: Any) -> list[dict[str, Any]]:
    if override is not None:
        return list(override)
    targets = []
    for tid, config in skill_registration_targets(arcana_root).items():
        targets.append({"id": tid, "label": config["label"], "path": config["path"]})
    return targets


def inspect_install(
    home: Path,
    arcana_root: Path,
    *,
    instruction_targets: list | None = None,
    skill_targets: list | None = None,
    git_fn: Callable | None = None,
) -> dict[str, Any]:
    """Return a read-only snapshot of an installation's state.

    `instruction_targets` / `skill_targets` default to the resolved registry
    targets; tests pass explicit lists of ``{"id","label","path"}`` so the
    snapshot never reaches the real home directory.
    """
    home = Path(home)
    arcana_root = Path(arcana_root)
    git_fn = git_fn or summon_core.git

    # Arcana itself
    is_git_repo = (arcana_root / ".git").is_dir()
    populated = summon_core.working_tree_populated(arcana_root) if arcana_root.is_dir() else False
    toplevel = None
    if is_git_repo:
        ok, out = git_fn("-C", str(arcana_root), "rev-parse", "--show-toplevel")
        toplevel = out if ok and out else None
    arcana_state = {
        "root": str(arcana_root),
        "present": arcana_root.is_dir(),
        "git_repo": is_git_repo,
        "working_tree_populated": populated,
        "git_toplevel": toplevel,
    }

    # Local library vs disk (reuses sync_library's drift classification)
    library_path = home / "library.json"
    scan = sync_library.scan_grimoire_home(home)
    library = sync_library.load_library(library_path)
    diff = sync_library.diff_library(scan, library, home)
    library_state = {
        "path": str(library_path),
        "in_sync": not (diff["missing"] or diff["stale"] or diff["mismatched"]),
        "missing": list(diff["missing"]),
        "stale": [{"key": s["key"], "raw_path": s["raw_path"]} for s in diff["stale"]],
        "mismatched": [
            {"key": m["key"], "raw_path": m["raw_path"], "expected_path": m["expected_path"]}
            for m in diff["mismatched"]
        ],
        "ok": list(diff["ok"]),
        "unmanaged": [p.name for p in scan["unmanaged"]],
        "on_disk": sorted(g["key"] for g in scan["grimoires"]),
        "warnings": list(scan["warnings"]),
    }

    # Agent instruction blocks
    agent_state = []
    for target in _instruction_targets(arcana_root, instruction_targets):
        path = Path(target["path"])
        exists = path.is_file()
        content = ""
        if exists:
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                content = ""
        marker = _detect_block_marker(content)
        agent_state.append({
            "id": target.get("id"),
            "label": target.get("label"),
            "path": str(path),
            "instruction_file_exists": exists,
            "block_present": marker != "none",
            "block_marker": marker,
        })

    # Registered skills per target
    skill_state = []
    for target in _skill_targets(arcana_root, skill_targets):
        path = Path(target["path"])
        skill_state.append({
            "id": target.get("id"),
            "label": target.get("label"),
            "path": str(path),
            "exists": path.is_dir(),
            "arcana_managed_count": summon_core._registered_skill_count(path),
        })

    return {
        "arcana": arcana_state,
        "library": library_state,
        "agent_targets": agent_state,
        "skills": skill_state,
        "network_pull": NETWORK_PULL_NOTE,
    }


# ---------------------------------------------------------------------------
# Drift / remediation derivation
# ---------------------------------------------------------------------------


def _library_has_fixable_drift(library: dict[str, Any]) -> bool:
    return bool(library["missing"] or library["mismatched"])


def _skills_absent(state: dict[str, Any]) -> bool:
    """True when Arcana is installed but no managed skills are registered anywhere."""
    if not state["arcana"]["working_tree_populated"]:
        return False
    return sum(s["arcana_managed_count"] for s in state["skills"]) == 0


def _missing_block_ids(state: dict[str, Any]) -> list[str]:
    return [a["id"] for a in state["agent_targets"] if a["block_marker"] == "none"]


def drift_detected(state: dict[str, Any]) -> bool:
    """Single drift predicate backing the --check exit code."""
    return (
        not state["library"]["in_sync"]
        or bool(_missing_block_ids(state))
        or _skills_absent(state)
    )


def next_actions(state: dict[str, Any], arcana_root: Path) -> list[dict[str, Any]]:
    """Structured, tier-tagged remediation - never free-text the orchestrator must parse."""
    actions: list[dict[str, Any]] = []
    lib = state["library"]

    if _library_has_fixable_drift(lib):
        keys = sorted(lib["missing"] + [m["key"] for m in lib["mismatched"]])
        actions.append({
            "kind": "library_reconcile",
            "tier": "amber",
            "command": "python3 rites/summon.py --reconcile --apply",
            "reason": f"library entries to add/correct: {', '.join(keys)}",
        })
    if lib["stale"]:
        keys = sorted(s["key"] for s in lib["stale"])
        actions.append({
            "kind": "library_prune",
            "tier": "red",
            "command": "python3 rites/summon.py --reconcile --apply --prune",
            "reason": f"stale library entries (removal deletes them): {', '.join(keys)}",
        })
    missing_blocks = _missing_block_ids(state)
    if missing_blocks:
        actions.append({
            "kind": "agent_block_update",
            "tier": "amber",
            "command": "/arc-agent-update",
            "reason": f"agent instruction block absent for: {', '.join(missing_blocks)}",
        })
    if _skills_absent(state):
        actions.append({
            "kind": "skill_register",
            "tier": "amber",
            "command": "python3 rites/register_skills.py --agent all",
            "reason": "no Arcana-managed skills registered in any agent skill directory",
        })
    if not state["arcana"]["working_tree_populated"]:
        actions.append({
            "kind": "arcana_recover",
            "tier": "red",
            "command": f"git -C {arcana_root} pull --ff-only",
            "reason": "Arcana working tree is missing or partial (network/human step)",
        })
    return actions


def residual(state: dict[str, Any], *, prune: bool) -> list[dict[str, Any]]:
    """What reconcile --apply does NOT fix - the human/RED boundary, machine-typed."""
    items: list[dict[str, Any]] = []
    if state["library"]["stale"] and not prune:
        items.append({
            "kind": "library_stale",
            "tier": "red",
            "reason": "stale library entries preserved; re-run with --prune to remove",
        })
    missing_blocks = _missing_block_ids(state)
    if missing_blocks:
        items.append({
            "kind": "agent_block",
            "tier": "amber",
            "reason": f"agent instruction block must be refreshed via /arc-agent-update for: {', '.join(missing_blocks)}",
        })
    if not state["arcana"]["working_tree_populated"]:
        items.append({
            "kind": "arcana_base",
            "tier": "red",
            "reason": "Arcana working tree not populated; reconcile cannot repair the base",
        })
    return items


# ---------------------------------------------------------------------------
# Default subprocess seams (injectable in tests)
# ---------------------------------------------------------------------------


def _default_skill_runner(register_script: Path) -> tuple[int, str]:
    result = subprocess.run(
        [summon_core.system_python(), str(register_script), "--agent", "all"],
        capture_output=True,
        text=True,
        env=summon_core._subprocess_env(),
    )
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def _default_validate_runner(arcana_root: Path) -> tuple[bool, str]:
    script = Path(arcana_root) / "rites" / "validate.py"
    if not script.is_file():
        return False, f"validate.py not found at {script}"
    result = subprocess.run(
        [summon_core.system_python(), str(script), "--summary"],
        capture_output=True,
        text=True,
        env=summon_core._subprocess_env(),
    )
    return result.returncode == 0, (result.stdout or "")[-500:]


# ---------------------------------------------------------------------------
# Reconcile (the repair engine behind --check / --reconcile)
# ---------------------------------------------------------------------------


def _reconcile_library(
    home: Path,
    diff_library: dict[str, Any],
    *,
    apply: bool,
    prune: bool,
    reporter: ResultReporter,
) -> dict[str, Any]:
    """Apply the additive library reconciliation; preserve stale unless pruning."""
    step = {"id": "library", "label": "Reconcile local library", "status": "noop",
            "mutations": [], "messages": []}
    missing = diff_library["missing"]
    mismatched = diff_library["mismatched"]
    stale = diff_library["stale"]

    if not (missing or mismatched or stale):
        return step

    for key in missing:
        text = f"library: + {key} (missing entry will be added)"
        reporter.message("info", text)
        step["messages"].append({"severity": "info", "message": text})
    for m in mismatched:
        text = f"library: ~ {m['key']} (local_path corrected)"
        reporter.message("info", text)
        step["messages"].append({"severity": "info", "message": text})
    for s in stale:
        if prune:
            text = f"library: - {s['key']} (stale entry removed)"
        else:
            text = f"library: ! {s['key']} (stale; preserved, use --prune to remove)"
        reporter.message("warning", text)
        step["messages"].append({"severity": "warning", "message": text})

    changed = bool(missing or mismatched or (prune and stale))

    if not apply:
        step["status"] = "drift" if changed or stale else "noop"
        return step

    library_path = home / "library.json"
    scan = sync_library.scan_grimoire_home(home)
    original = sync_library.load_library(library_path)
    synced = sync_library.build_synced_library(scan, original, home)

    if not prune:
        # build_synced_library drops entries that no longer resolve. Re-add every
        # dropped key from the original so reconcile never deletes a library entry
        # without --prune - a structural guarantee that does not depend on the
        # stale set matching this fresh scan. setdefault keeps disk-rebuilt
        # corrections (e.g. mismatched paths) intact.
        for key, entry in original["grimoires"].items():
            synced["grimoires"].setdefault(key, entry)
        synced["grimoires"] = dict(sorted(synced["grimoires"].items()))

    if changed:
        sync_library.write_library(synced, library_path)
        for key in missing:
            reporter.mutation("add", path=library_path, detail=f"library entry {key}")
        for m in mismatched:
            reporter.mutation("update", path=library_path, detail=f"library local_path {m['key']}")
        if prune:
            for s in stale:
                reporter.mutation("remove", path=library_path, detail=f"stale library entry {s['key']}")
        step["mutations"] = [
            {"action": "write", "path": "library.json", "detail": "reconciled library"}
        ]
        step["status"] = "ok"
    else:
        step["status"] = "noop"
    return step


def _reconcile_skills(
    arcana_root: Path,
    state: dict[str, Any],
    *,
    apply: bool,
    reporter: ResultReporter,
    skill_runner: Callable,
) -> dict[str, Any]:
    step = {"id": "skills", "label": "Re-register agent skills", "status": "noop",
            "mutations": [], "messages": []}
    register_script = Path(arcana_root) / "rites" / "register_skills.py"

    if not state["arcana"]["working_tree_populated"]:
        text = "skills: skipped - Arcana working tree not populated (run summon install / git pull first)"
        reporter.message("error", text)
        step["messages"].append({"severity": "error", "message": text})
        step["status"] = "blocked"
        return step

    if not apply:
        if _skills_absent(state):
            text = "skills: no Arcana-managed skills registered (run register_skills --agent all)"
            reporter.message("warning", text)
            step["messages"].append({"severity": "warning", "message": text})
            step["status"] = "drift"
        return step

    if not register_script.is_file():
        text = f"skills: register_skills.py not found at {register_script}"
        reporter.message("error", text)
        step["messages"].append({"severity": "error", "message": text})
        step["status"] = "blocked"
        return step

    rc, _out = skill_runner(register_script)
    if rc == 0:
        reporter.mutation("register", detail="re-registered Arcana and grimoire skills")
        step["mutations"] = [{"action": "register", "path": None, "detail": "re-registered skills"}]
        step["status"] = "ok"
    else:
        text = f"skills: register_skills.py exited {rc}"
        reporter.message("error", text)
        step["messages"].append({"severity": "error", "message": text})
        step["status"] = "error"
    return step


def _reconcile_agent_blocks(state: dict[str, Any], *, reporter: ResultReporter) -> dict[str, Any]:
    """Report-only: the BEGIN/END vs heading sentinel mismatch makes auto-write unsafe."""
    step = {"id": "agent_blocks", "label": "Agent instruction blocks", "status": "noop",
            "mutations": [], "messages": []}
    missing = _missing_block_ids(state)
    if missing:
        text = (
            f"agent_blocks: absent for {', '.join(missing)} - refresh with /arc-agent-update "
            "(not auto-written: BEGIN/END vs heading sentinels make injection non-deterministic)"
        )
        reporter.message("warning", text)
        step["messages"].append({"severity": "warning", "message": text})
        step["status"] = "drift"
    return step


def reconcile(
    home: Path,
    arcana_root: Path,
    *,
    apply: bool = False,
    prune: bool = False,
    instruction_targets: list | None = None,
    skill_targets: list | None = None,
    git_fn: Callable | None = None,
    skill_runner: Callable | None = None,
    validate_runner: Callable | None = None,
) -> dict[str, Any]:
    """Run the offline reconciliation and return reporter + steps + before/after state."""
    home = Path(home)
    arcana_root = Path(arcana_root)
    skill_runner = skill_runner or _default_skill_runner
    validate_runner = validate_runner or _default_validate_runner

    reporter = ResultReporter("summon", root=home, mode="apply" if apply else "plan")
    state_before = inspect_install(
        home, arcana_root,
        instruction_targets=instruction_targets, skill_targets=skill_targets, git_fn=git_fn,
    )
    steps: list[dict[str, Any]] = []

    # Green-base gate: never repair on a tree that fails validation.
    if apply:
        ok, detail = validate_runner(arcana_root)
        if not ok:
            text = "validate: Arcana fails validate.py - refusing to reconcile on a broken base (RECOVERY.md step 4)"
            reporter.message("error", text)
            reporter.set_status("blocked")
            steps.append({"id": "validate", "label": "Validate Arcana base", "status": "blocked",
                          "mutations": [], "messages": [{"severity": "error", "message": text,
                                                          "detail": detail}]})
            state_after = state_before
            return _reconcile_result(reporter, steps, state_before, state_after, prune, arcana_root)
        steps.append({"id": "validate", "label": "Validate Arcana base", "status": "ok",
                      "mutations": [], "messages": []})

    steps.append(_reconcile_library(home, _diff_from_state(state_before), apply=apply,
                                    prune=prune, reporter=reporter))
    steps.append(_reconcile_skills(arcana_root, state_before, apply=apply,
                                   reporter=reporter, skill_runner=skill_runner))
    steps.append(_reconcile_agent_blocks(state_before, reporter=reporter))

    # Verify against post-write reality so the transcript reflects convergence.
    state_after = inspect_install(
        home, arcana_root,
        instruction_targets=instruction_targets, skill_targets=skill_targets, git_fn=git_fn,
    ) if apply else state_before

    return _reconcile_result(reporter, steps, state_before, state_after, prune, arcana_root)


def _diff_from_state(state: dict[str, Any]) -> dict[str, Any]:
    """Re-shape the inspected library block into sync_library's diff vocabulary."""
    return {
        "missing": state["library"]["missing"],
        "mismatched": state["library"]["mismatched"],
        "stale": state["library"]["stale"],
    }


def _reconcile_result(reporter, steps, state_before, state_after, prune, arcana_root):
    return {
        "reporter": reporter,
        "steps": steps,
        "state_before": state_before,
        "state_after": state_after,
        "residual": residual(state_after, prune=prune),
        "next_actions": next_actions(state_after, arcana_root),
    }


# ---------------------------------------------------------------------------
# Transcript
# ---------------------------------------------------------------------------


def build_summary(state, *, operation, drift, res, actions, extra=None):
    summary = {
        "schema_version": SCHEMA_VERSION,
        "operation": operation,
        "drift": drift,
        "library": {
            "in_sync": state["library"]["in_sync"],
            "missing": len(state["library"]["missing"]),
            "stale": len(state["library"]["stale"]),
            "mismatched": len(state["library"]["mismatched"]),
            "ok": len(state["library"]["ok"]),
        },
        "agent_blocks_missing": _missing_block_ids(state),
        "skills_registered": sum(s["arcana_managed_count"] for s in state["skills"]),
        "next_actions": actions,
        "residual": res,
    }
    if extra:
        summary.update(extra)
    return summary


def build_transcript(reporter, *, operation, state, steps, summary, run_id, started_at, ended_at):
    """Transcript is the stdout envelope as a superset - one status/mode/summary, no nesting."""
    envelope = reporter.report(summary=summary)
    return {
        **envelope,
        "schema_version": SCHEMA_VERSION,
        "operation": operation,
        "run_id": run_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "steps": steps,
        "final_state": state,
    }


def write_transcript(path: Path, transcript: dict[str, Any]) -> None:
    summon_core.write_json_atomic(Path(path), transcript)


def record_install_transcript(
    home: Path,
    arcana_root: Path,
    installed_keys: list,
    skills_ok: bool,
    *,
    transcript_path: Path | None = None,
    git_fn: Callable | None = None,
    now: Callable | None = None,
    run_id: str | None = None,
) -> dict[str, Any] | None:
    """Best-effort: drop an `operation: install` transcript after an install.

    Wrapped by callers in try/except so a transcript failure never breaks an
    otherwise-successful install.
    """
    now = now or _real_now
    started_at = now()
    state = inspect_install(home, arcana_root, git_fn=git_fn)
    installed_keys = list(installed_keys or [])
    arcana_ok = state["arcana"]["working_tree_populated"]
    status = "ok" if (arcana_ok and skills_ok) else "error"

    reporter = ResultReporter("summon", root=Path(home), mode="apply")
    reporter.set_status(status)
    for key in installed_keys:
        reporter.mutation("clone", detail=f"grimoire {key}")
    if not arcana_ok:
        reporter.message("error", "Arcana working tree not populated after install")
    if not skills_ok:
        reporter.message("error", "skill registration reported a problem")

    steps = [
        {"id": "arcana", "label": "Install or update Arcana",
         "status": "ok" if arcana_ok else "error", "mutations": [], "messages": []},
        {"id": "grimoires", "label": "Clone selected grimoires",
         "status": "ok" if installed_keys else "noop",
         "mutations": [{"action": "clone", "path": k, "detail": None} for k in installed_keys],
         "messages": []},
        {"id": "skills", "label": "Register skills",
         "status": "ok" if skills_ok else "error", "mutations": [], "messages": []},
    ]
    summary = build_summary(
        state, operation="install", drift=drift_detected(state),
        res=residual(state, prune=False), actions=next_actions(state, arcana_root),
        extra={"installed": installed_keys, "skills_ok": bool(skills_ok)},
    )
    transcript = build_transcript(
        reporter, operation="install", state=state, steps=steps, summary=summary,
        run_id=run_id or uuid.uuid4().hex, started_at=started_at, ended_at=now(),
    )
    write_transcript(transcript_path or default_transcript_path(), transcript)
    return transcript


# ---------------------------------------------------------------------------
# Human rendering
# ---------------------------------------------------------------------------


def _print_human(operation: str, state: dict[str, Any], result_steps, drift, transcript_path):
    log = summon_core.Logger()
    print()
    print("============================================")
    print(f"  Arcana Summon - {operation}")
    print("============================================")
    arcana = state["arcana"]
    (log.ok if arcana["working_tree_populated"] else log.err)(
        f"Arcana: {'populated' if arcana['working_tree_populated'] else 'NOT populated'} at {arcana['root']}"
    )
    lib = state["library"]
    if lib["in_sync"]:
        log.ok("Library: in sync with disk")
    else:
        log.warn(
            f"Library drift: +{len(lib['missing'])} missing, "
            f"~{len(lib['mismatched'])} mismatched, !{len(lib['stale'])} stale"
        )
    for a in state["agent_targets"]:
        if a["block_marker"] == "none":
            log.warn(f"Agent block absent: {a['id']} ({a['path']})")
        else:
            log.ok(f"Agent block present ({a['block_marker']}): {a['id']}")
    total_skills = sum(s["arcana_managed_count"] for s in state["skills"])
    (log.ok if total_skills else log.warn)(f"Registered skills: {total_skills}")
    if result_steps:
        print()
        print("  Steps:")
        for step in result_steps:
            print(f"    [{step['status']:<7}] {step['id']}")
    print()
    log.ok("In sync - no action needed") if not drift else log.warn("Drift detected - see next_actions")
    print(f"  Transcript: {transcript_path}")
    print()


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------


def add_state_args(parser: argparse.ArgumentParser) -> None:
    """Register the agent-legibility flags on the summon dispatcher's parser."""
    parser.add_argument("--check", "--plan", dest="check", action="store_true",
                        help="Report installation/registry drift (read-only) and write a transcript")
    parser.add_argument("--reconcile", "--recover", dest="reconcile", action="store_true",
                        help="Repair the local library and re-register skills to match disk")
    parser.add_argument("--apply", dest="apply", action="store_true",
                        help="With --reconcile, perform changes (default: propose only)")
    parser.add_argument("--prune", dest="prune", action="store_true",
                        help="With --reconcile --apply, remove stale library entries (deletes them)")
    parser.add_argument("--home", dest="home", default=None,
                        help="Override grimoires home (default: ~/grimoires)")
    parser.add_argument("--arcana-root", dest="arcana_root", default=None,
                        help="Override Arcana root (default: detected)")
    parser.add_argument("--transcript-path", dest="transcript_path", default=None,
                        help="Override the transcript path (default: ~/.cache/grimoire/summon-last.json)")
    add_output_format_arg(parser)


def is_state_invocation(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "check", False) or getattr(args, "reconcile", False))


def run_state_command(
    args: argparse.Namespace,
    *,
    transcript_path: Path | None = None,
    instruction_targets: list | None = None,
    skill_targets: list | None = None,
    git_fn: Callable | None = None,
    skill_runner: Callable | None = None,
    validate_runner: Callable | None = None,
    now: Callable | None = None,
    run_id: str | None = None,
) -> int:
    """Drive --check / --reconcile: emit the envelope, write the transcript, set the exit code."""
    now = now or _real_now
    started_at = now()
    home = Path(args.home).expanduser().resolve() if getattr(args, "home", None) else summon_core.GRIMOIRES_HOME
    arcana_root = (
        Path(args.arcana_root).expanduser().resolve()
        if getattr(args, "arcana_root", None) else summon_core.REPO_ROOT
    )
    fmt = getattr(args, "format", "human")
    do_reconcile = bool(getattr(args, "reconcile", False))
    apply = bool(getattr(args, "reconcile", False) and getattr(args, "apply", False))
    prune = bool(getattr(args, "prune", False))
    operation = "reconcile" if do_reconcile else "check"

    outcome = reconcile(
        home, arcana_root, apply=apply, prune=prune,
        instruction_targets=instruction_targets, skill_targets=skill_targets,
        git_fn=git_fn, skill_runner=skill_runner, validate_runner=validate_runner,
    )
    reporter = outcome["reporter"]
    state = outcome["state_after"]
    drift = drift_detected(state)
    summary = build_summary(
        state, operation=operation, drift=drift,
        res=outcome["residual"], actions=outcome["next_actions"],
        extra={"applied": apply, "pruned": prune},
    )
    transcript = build_transcript(
        reporter, operation=operation, state=state, steps=outcome["steps"], summary=summary,
        run_id=run_id or uuid.uuid4().hex, started_at=started_at, ended_at=now(),
    )

    path = transcript_path
    if path is None and getattr(args, "transcript_path", None):
        path = Path(args.transcript_path).expanduser()
    if path is None:
        path = default_transcript_path()
    try:
        write_transcript(path, transcript)
    except OSError:
        path = "<unwritten>"

    if fmt == "human":
        _print_human(operation, state, outcome["steps"], drift, path)
    else:
        reporter.emit(fmt, summary=summary)

    if not apply:
        # Plan/propose - both --check and --reconcile without --apply - signal
        # actionable drift through the exit code, matching the documented table.
        return 1 if drift else 0
    status = reporter.status()
    if status in ("blocked", "error"):
        return 1
    return 1 if outcome["residual"] else 0
