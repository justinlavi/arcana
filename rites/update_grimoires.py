#!/usr/bin/env python3
"""Bring every grimoire in the library current, then heal only the current ones.

This is the network- and branch-aware half of the Update process (`UPDATE.md`).
`summon_state.py` stays deliberately offline; this module owns the fetch/pull and
the gated heal, composed by `summon.py --update [--apply]`.

Per grimoire it runs a read-only classification ladder, fast-forwards a clean
branch that is behind its upstream, and then heals ONLY the grimoires it
confirmed current. The load-bearing invariant is `heal_eligible`: a grimoire that
could not be brought current (dirty, diverged, detached, no upstream, or a pull
that failed on a private host's auth) is never validated-and-modified - healing a
stale tree would re-derive work that already exists upstream and cause divergence,
which is the field bug this rite repairs.

Auth/host nuance: each grimoire is pulled from whatever remote it tracks, public
or private; grimoires often live on a private host (e.g. a self-hosted GitLab)
that needs a token. A per-grimoire fetch/pull failure never aborts the run - it is classified
(auth_failed / offline / fetch_error), collected into `needs_manual_pull`, and the
run continues so a team of many can update the grimoires they can reach.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import summon_core
import sync_library
from diagnostics import ResultReporter, add_output_format_arg
from sync_skills import resolve_grimoire_path
from scaffold_contract import load_scaffold_contract, managed_scaffold_files

# A grimoire is eligible for healing only when it is confirmed current with its
# upstream. Everything else is reported and skipped untouched.
HEAL_ELIGIBLE = frozenset({"up_to_date", "fast_forwarded", "ahead"})

# Statuses that need the user to pull by hand (private-host auth, offline, etc.).
NEEDS_MANUAL_PULL = frozenset({"auth_failed", "offline", "fetch_error", "behind_blocked", "diverged"})

# README update-block markers.
UPDATE_BEGIN = "<!-- BEGIN ARCANA UPDATE -->"
UPDATE_END = "<!-- END ARCANA UPDATE -->"

_AUTH_MARKERS = (
    "403", "insufficient_scope", "authentication failed", "could not read username",
    "permission denied", "fatal: authentication", "access denied", "401",
)
_OFFLINE_MARKERS = (
    "could not resolve host", "connection timed out", "timed out", "network is unreachable",
    "could not connect", "ssl", "unable to access",
)


# ---------------------------------------------------------------------------
# Classification ladder (read-only)
# ---------------------------------------------------------------------------


def _host(online_path: str | None) -> str:
    if not online_path:
        return ""
    return urlparse(online_path).hostname or ""


def classify_fetch_error(stderr: str) -> str:
    """Map a failed fetch's stderr to auth_failed / offline / fetch_error."""
    low = (stderr or "").lower()
    if any(m in low for m in _AUTH_MARKERS):
        return "auth_failed"
    if any(m in low for m in _OFFLINE_MARKERS):
        return "offline"
    return "fetch_error"


def _parse_ahead_behind(out: str) -> tuple[int, int]:
    """`rev-list --left-right --count @{u}...HEAD` -> (behind, ahead)."""
    parts = out.split()
    if len(parts) != 2:
        return 0, 0
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return 0, 0


def classify_grimoire(
    local_path: Path,
    *,
    fetch: bool,
    git: Callable = summon_core.git_capture,
    credential_probe: Callable = summon_core.git_credential_token,
    host: str = "",
) -> dict[str, Any]:
    """Read-only ladder: resolve repo state and (optionally) fetch to learn currency.

    Never pulls or heals. Returns a partial grimoire record with `status`,
    `branch`, `upstream`, `ahead`, `behind`, and `creds_present`/`reason` when
    relevant. `fetch=False` keeps it fully offline (the `--check` snapshot).
    """
    rec: dict[str, Any] = {
        "branch": None, "upstream": None, "ahead": 0, "behind": 0,
        "status": None, "reason": None, "creds_present": None,
    }
    g = str(local_path)

    if not local_path.is_dir():
        rec["status"] = "missing_local"
        rec["reason"] = "no directory at local_path (clone it via the summon rite)"
        return rec
    if not (local_path / ".git").exists():
        rec["status"] = "not_a_repo"
        rec["reason"] = "directory is not a git repository"
        return rec

    rc, branch, _ = git("-C", g, "symbolic-ref", "--quiet", "--short", "HEAD")
    if rc != 0 or not branch:
        rec["status"] = "detached"
        rec["reason"] = "detached HEAD; check out a branch first"
        return rec
    rec["branch"] = branch

    rc, upstream, _ = git("-C", g, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if rc != 0 or not upstream:
        rec["status"] = "no_upstream"
        rec["reason"] = f"branch '{branch}' has no upstream; git branch --set-upstream-to"
        return rec
    rec["upstream"] = upstream
    remote = upstream.split("/", 1)[0]

    rc, dirty, _ = git("-C", g, "status", "--porcelain")
    if rc == 0 and dirty.strip():
        rec["status"] = "dirty"
        rec["reason"] = "uncommitted changes; commit/stash/discard before updating (never auto-discarded)"
        return rec

    if fetch:
        rc, _, err = git("-C", g, "fetch", "--prune", remote)
        if rc != 0:
            rec["status"] = classify_fetch_error(err)
            rec["reason"] = (err or "fetch failed").splitlines()[0][:200] if err else "fetch failed"
            if rec["status"] == "auth_failed" and host:
                rec["creds_present"] = bool(credential_probe(host))
            return rec

    rc, ab, _ = git("-C", g, "rev-list", "--left-right", "--count", "@{u}...HEAD")
    behind, ahead = _parse_ahead_behind(ab) if rc == 0 else (0, 0)
    rec["behind"], rec["ahead"] = behind, ahead
    if behind == 0 and ahead == 0:
        rec["status"] = "up_to_date"
    elif behind > 0 and ahead == 0:
        rec["status"] = "behind"  # fast-forwardable; bring_current resolves it
    elif ahead > 0 and behind == 0:
        rec["status"] = "ahead"
        rec["reason"] = f"{ahead} local commit(s) not pushed"
    else:
        rec["status"] = "diverged"
        rec["reason"] = f"{ahead} ahead / {behind} behind; reconcile by hand (rebase/merge)"
    return rec


def bring_current(local_path: Path, rec: dict[str, Any], *, git: Callable = summon_core.git_capture) -> None:
    """Fast-forward a clean, behind branch. Mutates `rec` in place."""
    if rec["status"] != "behind":
        return
    rc, _, err = git("-C", str(local_path), "pull", "--ff-only")
    if rc == 0:
        rec["status"] = "fast_forwarded"
        rec["behind"] = 0
    else:
        rec["status"] = "behind_blocked"
        rec["reason"] = (err or "fast-forward refused").splitlines()[0][:200] if err else "fast-forward refused"


# ---------------------------------------------------------------------------
# Heal (only ever called for a heal-eligible, confirmed-current grimoire)
# ---------------------------------------------------------------------------


def _formula_update_block(arcana_root: Path) -> str | None:
    """Extract the marked update block from the grimoire formula README."""
    path = arcana_root / "formulae" / "grimoire" / "README.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    start = text.find(UPDATE_BEGIN)
    end = text.find(UPDATE_END)
    if start == -1 or end == -1:
        return None
    return text[start:end + len(UPDATE_END)]


def _replace_readme_block(text: str, block: str) -> str:
    """Return README text with the update block present exactly once.

    Replaces the marked block in place when present; otherwise inserts it before
    the first second-level heading (or appends). Idempotent. The injector knows
    only the current update markers - new grimoires are born with the block from
    the formula, so there is no legacy form to convert.
    """
    s = text.find(UPDATE_BEGIN)
    e = text.find(UPDATE_END)
    if s != -1 and e != -1 and e > s:
        return text[:s] + block + text[e + len(UPDATE_END):]

    first = text.find("\n## ")
    if first != -1:
        return text[:first + 1] + block + "\n\n" + text[first + 1:]
    sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
    return text + sep + block + "\n"


def inject_update_readme_block(readme_path: Path, block: str) -> bool:
    """Idempotently ensure the grimoire README carries the current update block.

    Returns True if the file changed.
    """
    try:
        text = readme_path.read_text(encoding="utf-8")
    except OSError:
        return False
    new = _replace_readme_block(text, block)
    if new != text:
        readme_path.write_text(new, encoding="utf-8")
        return True
    return False


def default_heal(local_path: Path, arcana_root: Path) -> dict[str, Any]:
    """Mechanical, idempotent grimoire heal: managed scaffold, README block, links.

    Only called for a confirmed-current grimoire. Re-sync the Arcana-owned managed
    scaffold (never the customized README/hub/manifest/log), refresh the README
    update block, then promote wikilinks. Re-validation is left to the caller.
    """
    result: dict[str, Any] = {"scaffold_synced": [], "readme_block": "unchanged",
                              "links_repaired": None, "status": "ok", "messages": []}

    # 1. Managed scaffold: copy Arcana formula over the grimoire's copy (safe -
    #    managed_scaffold_files excludes README/hub/grimoire.json/log.md).
    try:
        contract = load_scaffold_contract(arcana_root)
        formula_dir = arcana_root / "formulae" / "grimoire"
        for rel in managed_scaffold_files(contract):
            src = formula_dir / rel
            dst = local_path / rel
            if not src.is_file():
                continue
            if (not dst.exists()) or dst.read_bytes() != src.read_bytes():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
                result["scaffold_synced"].append(rel)
    except Exception as exc:  # contract load / IO
        result["status"] = "error"
        result["messages"].append(f"scaffold sync failed: {exc}")

    # 2. Ensure the README carries the current update block from the formula.
    block = _formula_update_block(arcana_root)
    readme = local_path / "README.md"
    if block and readme.is_file():
        try:
            if inject_update_readme_block(readme, block):
                result["readme_block"] = "updated"
        except OSError as exc:
            result["status"] = "error"
            result["messages"].append(f"README block injection failed: {exc}")

    # 3. Promote/repair wikilinks a structural change may have broken.
    repair = _run_repair_links(arcana_root, local_path)
    result["links_repaired"] = repair.get("repaired")
    if repair.get("status") == "error":
        result["status"] = "error"
        result["messages"].append(repair.get("message", "repair_links failed"))

    return result


def _run_repair_links(arcana_root: Path, local_path: Path) -> dict[str, Any]:
    """Run repair_links.py --apply against a grimoire; report a small result."""
    script = arcana_root / "rites" / "repair_links.py"
    if not script.is_file():
        return {"status": "skipped", "message": "repair_links.py not found"}
    try:
        proc = subprocess.run(
            [summon_core.system_python(), str(script), "--grimoire", str(local_path), "--apply"],
            capture_output=True, text=True, env=summon_core._subprocess_env(),
            timeout=summon_core.GIT_TIMEOUT,
        )
    except Exception as exc:
        return {"status": "error", "message": f"repair_links failed: {exc}"}
    return {"status": "ok" if proc.returncode == 0 else "error",
            "repaired": None,
            "message": (proc.stderr or proc.stdout or "").strip()[-200:] if proc.returncode else ""}


def revalidate(arcana_root: Path, local_path: Path) -> tuple[bool, str]:
    """Re-run grimoire validation; return (ok, short detail)."""
    script = arcana_root / "rites" / "validate.py"
    if not script.is_file():
        return False, "validate.py not found"
    try:
        proc = subprocess.run(
            [summon_core.system_python(), str(script), "--grimoire", str(local_path), "--summary"],
            capture_output=True, text=True, env=summon_core._subprocess_env(),
            timeout=summon_core.GIT_TIMEOUT,
        )
    except Exception as exc:
        return False, f"validate failed: {exc}"
    return proc.returncode == 0, (proc.stdout or "")[-300:]


# ---------------------------------------------------------------------------
# Per-grimoire + library orchestration
# ---------------------------------------------------------------------------


def process_grimoire(
    key: str,
    entry: dict[str, Any],
    arcana_root: Path,
    *,
    apply: bool,
    fetch: bool = True,
    git: Callable = summon_core.git_capture,
    heal_fn: Callable = default_heal,
    revalidate_fn: Callable = revalidate,
) -> dict[str, Any]:
    """Classify, (apply) fast-forward, then (apply + eligible) heal one grimoire.

    `fetch=False` keeps it fully offline (the read-only `--check` snapshot):
    currency is read from already-fetched refs and nothing is pulled or healed.
    """
    raw = entry.get("local_path", "")
    online = entry.get("online_path")
    local_path = resolve_grimoire_path(raw)
    host = _host(online)

    rec: dict[str, Any] = {
        "key": key,
        "local_path": str(local_path),
        "host": host,
        "online_path": online,
        "pulled": False,
        "heal_eligible": False,
        "heal": None,
    }
    rec.update(classify_grimoire(local_path, fetch=fetch, git=git, host=host))

    if apply and rec["status"] == "behind":
        bring_current(local_path, rec, git=git)
        rec["pulled"] = rec["status"] == "fast_forwarded"

    rec["heal_eligible"] = rec["status"] in HEAL_ELIGIBLE
    if rec["heal_eligible"]:
        rec["suggested_command"] = None
        if apply:
            heal = heal_fn(local_path, arcana_root)
            ok, detail = revalidate_fn(arcana_root, local_path)
            heal["validate"] = "ok" if ok else "fail"
            if not ok:
                heal["status"] = "error"
                heal.setdefault("messages", []).append(detail.strip()[-200:])
            rec["heal"] = heal
        else:
            rec["heal"] = {"status": "planned"}
    else:
        rec["heal"] = {"status": "skipped", "reason": rec.get("reason")}
        if rec["status"] in NEEDS_MANUAL_PULL:
            rec["suggested_command"] = f"git -C {local_path} pull --ff-only"

    return rec


def process_all(
    home: Path,
    arcana_root: Path,
    *,
    apply: bool,
    fetch: bool = True,
    library: dict[str, Any] | None = None,
    git: Callable = summon_core.git_capture,
    heal_fn: Callable = default_heal,
    revalidate_fn: Callable = revalidate,
) -> dict[str, Any]:
    """Process every grimoire in the library; return the structured result block.

    `fetch=False` produces an offline currency snapshot (no network, no writes);
    `apply=True` fast-forwards and heals the grimoires confirmed current.
    """
    home = Path(home)
    arcana_root = Path(arcana_root)
    if library is None:
        library = sync_library.load_library(home / "library.json")
    grimoires_map = library.get("grimoires", {})

    results: list[dict[str, Any]] = []
    for key in sorted(grimoires_map):
        results.append(process_grimoire(
            key, grimoires_map[key], arcana_root,
            apply=apply, fetch=fetch, git=git, heal_fn=heal_fn, revalidate_fn=revalidate_fn,
        ))

    needs_manual = [
        {"key": r["key"], "host": r["host"], "online_path": r["online_path"],
         "status": r["status"], "creds_present": r.get("creds_present"),
         "suggested_command": r.get("suggested_command")}
        for r in results if r["status"] in NEEDS_MANUAL_PULL
    ]
    summary = {
        "total": len(results),
        "already_current": sum(1 for r in results if r["status"] == "up_to_date"),
        "brought_current": sum(1 for r in results if r["status"] == "fast_forwarded"),
        "ahead": sum(1 for r in results if r["status"] == "ahead"),
        "healed": sum(1 for r in results if (r.get("heal") or {}).get("status") == "ok"),
        "heal_skipped": sum(1 for r in results if not r["heal_eligible"]),
        "needs_manual_pull": len(needs_manual),
    }
    return {"grimoires": results, "needs_manual_pull": needs_manual, "summary": summary}


# ---------------------------------------------------------------------------
# CLI (also reachable as `summon.py --update`; see summon_state.run_state_command)
# ---------------------------------------------------------------------------


def _build_reporter(home: Path, result: dict[str, Any], *, apply: bool) -> ResultReporter:
    reporter = ResultReporter("update_grimoires", root=home, mode="apply" if apply else "plan")
    for r in result["grimoires"]:
        if r["status"] in NEEDS_MANUAL_PULL:
            reporter.message("warning", f"{r['key']}: {r['status']} - {r.get('reason') or 'pull manually'}",
                             path=r["local_path"])
        if r["pulled"]:
            reporter.mutation("pull", path=r["local_path"], detail="fast-forwarded to upstream")
        heal = r.get("heal") or {}
        if heal.get("status") == "ok" and (heal.get("scaffold_synced") or heal.get("readme_block") == "updated"):
            reporter.mutation("heal", path=r["local_path"], detail="re-synced managed scaffold / README block")
        if heal.get("status") == "error":
            reporter.message("error", f"{r['key']}: heal error", path=r["local_path"])
    return reporter


def main() -> int:
    parser = argparse.ArgumentParser(description="Pull and heal every grimoire in the library")
    parser.add_argument("--home", default=None, help="Grimoires home (default: ~/grimoires)")
    parser.add_argument("--arcana-root", default=None, help="Arcana root (default: detected)")
    parser.add_argument("--apply", action="store_true", help="Pull and heal (default: plan only)")
    add_output_format_arg(parser)
    args = parser.parse_args()

    home = Path(args.home).expanduser().resolve() if args.home else summon_core.GRIMOIRES_HOME
    arcana_root = Path(args.arcana_root).expanduser().resolve() if args.arcana_root else summon_core.REPO_ROOT

    result = process_all(home, arcana_root, apply=args.apply)
    reporter = _build_reporter(home, result, apply=args.apply)
    summary = {**result["summary"], "grimoires": result["grimoires"],
               "needs_manual_pull": result["needs_manual_pull"], "applied": args.apply}

    if args.format == "human":
        _print_human(result, apply=args.apply)
    else:
        reporter.emit(args.format, summary=summary)

    if result["needs_manual_pull"]:
        return 1
    return 0


def _print_human(result: dict[str, Any], *, apply: bool) -> None:
    s = result["summary"]
    print()
    print("  Grimoire update " + ("(apply)" if apply else "(plan)"))
    for r in result["grimoires"]:
        mark = "OK " if r["status"] in ("up_to_date", "fast_forwarded", "ahead") else "!! "
        line = f"  [{mark}] {r['key']}: {r['status']}"
        if r["behind"] or r["ahead"]:
            line += f" (behind {r['behind']}, ahead {r['ahead']})"
        print(line)
        if r.get("suggested_command"):
            print(f"          pull manually: {r['suggested_command']}")
    print(f"  current={s['already_current'] + s['brought_current'] + s['ahead']}/{s['total']}  "
          f"healed={s['healed']}  needs-manual-pull={s['needs_manual_pull']}")
    print()


if __name__ == "__main__":
    import sys
    sys.exit(main())
