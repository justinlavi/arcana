#!/usr/bin/env python3
"""Agent routing-block injector - deterministic create / refresh, judgment for the rest.

Sister to `sync_skills.py` (skill registration) and `sync_library.py` (library
reconciliation). This rite keeps the Grimoire routing block - the region between
`<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->` and `<!-- END GRIMOIRE KNOWLEDGE BASE -->` -
current in each agent instruction file (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`).

The BEGIN/END markers are the sole contract. Everything between them is
Arcana-owned and the user never edits it; everything outside is the user's. The
rite does only what is unambiguous from those markers:

  * absent file                 -> create it with a heading and the block
  * exactly one clean BEGIN..END -> refresh it in place (idempotent: a block that
                                    already matches the template is left alone)
  * anything else               -> report `review` and write nothing

`review` covers every delicate case: a file with no block, a block with
duplicate or malformed markers, or a pre-marker block from an old install. These
are not mechanical decisions - the agentfile judgment edit (in the /grm-sync and
/arc-sync invocations) reads the file, finds or upgrades the block caring only
about the marked region, and preserves all user content outside it. The rite
never guesses and never duplicates.

The block text and markers are single-sourced from `summon_core`. Writes are
UTF-8 without BOM and LF line endings.

Mutation profile: plan_apply. The default plans; `--apply` performs the
deterministic create/refresh.

Usage:
    python3 inject_agent_file.py [--agent all|TARGET] [--apply] [--arcana-root PATH]

Exit codes: 0 = plan or apply completed, 2 = argparse invalid arguments.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import summon_core
from agent_targets import automatic_instruction_targets
from diagnostics import ResultReporter, add_output_format_arg

BEGIN_SENTINEL = summon_core.BEGIN_SENTINEL
END_SENTINEL = summon_core.END_SENTINEL

# Actions that write to disk under --apply.
WRITING_ACTIONS = ("create", "insert", "refresh")

REASONS = {
    "create": "file absent",
    "present": "routing block present and current",
    "refresh": "routing block out of date",
    "insert": "no routing block - safe to add",
    "review": "block-like but not one clean BEGIN..END region",
}


def canonical_marked_block() -> str:
    """Return the canonical BEGIN..END block with no surrounding blank lines."""
    return summon_core.canonical_routing_block()


def plan_block(content: str | None) -> tuple[str, str]:
    """Classify the action one target needs (shared classifier in summon_core)."""
    action = summon_core.classify_routing_block(content)
    return action, REASONS[action]


def apply_block(path: Path, title: str, *, apply: bool) -> dict[str, Any]:
    """Plan, and under `apply` perform, the block action for one target.

    Returns {"path", "action", "reason", "status"}. `status` is "planned" in
    plan mode; in apply mode it is "ok" (wrote), "noop" (already current), or
    "review" (handed to the judgment edit - the rite wrote nothing). The rite
    never appends over a block-like file, so it can never create a duplicate.
    """
    path = Path(path)
    content = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else None
    action, reason = plan_block(content)
    result = {
        "path": str(path),
        "action": action,
        "reason": reason,
        "status": "planned" if not apply else "noop",
    }
    if not apply:
        return result

    if action == "create":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {title}\n" + summon_core.GRIMOIRE_BLOCK, encoding="utf-8", newline="\n")
        result["status"] = "ok"
    elif action == "insert":
        if content.startswith(f"# {title}"):
            cut = content.index("\n") + 1 if "\n" in content else len(content)
            new = content[:cut] + summon_core.GRIMOIRE_BLOCK + content[cut:]
        else:
            new = content + summon_core.GRIMOIRE_BLOCK
        path.write_text(new, encoding="utf-8", newline="\n")
        result["status"] = "ok"
    elif action == "refresh":
        begin = content.find(BEGIN_SENTINEL)
        end = content.find(END_SENTINEL) + len(END_SENTINEL)
        path.write_text(content[:begin] + canonical_marked_block() + content[end:],
                        encoding="utf-8", newline="\n")
        result["status"] = "ok"
    elif action == "review":
        result["status"] = "review"
    return result


def resolve_targets(arcana_root: Path, agent: str) -> list[dict[str, Any]]:
    """Return the automatic instruction targets, optionally filtered by agent id."""
    targets = automatic_instruction_targets(arcana_root)
    if agent and agent != "all":
        targets = [t for t in targets if t.get("id") == agent]
    return targets


def _record(reporter: ResultReporter, target: dict[str, Any], result: dict[str, Any], apply: bool) -> None:
    """Record one target's result on the structured reporter."""
    tid = target.get("id") or "?"
    path = target.get("path")
    action = result["action"]
    if action in WRITING_ACTIONS:
        if apply:
            reporter.mutation(action, path=path, detail=f"{action} routing block in {tid}")
        else:
            reporter.message("info", f"would {action} routing block in {tid} ({path})", path=path)
    elif action == "review":
        reporter.message(
            "warning",
            f"{tid}: {result['reason']} - handed to the agentfile judgment edit ({path})",
            path=path,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent routing-block injector")
    parser.add_argument(
        "--agent",
        default="all",
        help="Agent instruction target id from rites/data/agent_targets.json (default: all)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create or refresh the routing block (default: plan only)",
    )
    parser.add_argument(
        "--arcana-root",
        dest="arcana_root",
        default=None,
        help="Override Arcana root (default: detected)",
    )
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"

    arcana_root = (
        Path(args.arcana_root).expanduser().resolve()
        if args.arcana_root else summon_core.REPO_ROOT
    )
    reporter = ResultReporter("inject_agent_file", mode="apply" if args.apply else "plan")
    targets = resolve_targets(arcana_root, args.agent)

    if human:
        print()
        print("  Agent Routing-Block Injector")
        print("  ----------------------------")
        if not args.apply:
            print("  [INFO]  Plan mode - no files will be written")
        print()

    if not targets:
        message = f"no automatic instruction target matched --agent {args.agent!r}"
        if human:
            print(f"  [WARN]  {message}")
            print()
        else:
            reporter.message("warning", message)
            reporter.emit(args.format, summary={"created": 0, "inserted": 0, "refreshed": 0,
                                                "present": 0, "review": 0})
        return 0

    counts = {"create": 0, "insert": 0, "refresh": 0, "present": 0, "review": 0}
    for target in targets:
        result = apply_block(Path(target["path"]), target.get("title") or Path(target["path"]).name,
                             apply=args.apply)
        counts[result["action"]] = counts.get(result["action"], 0) + 1
        _record(reporter, target, result, args.apply)
        if human:
            verb = {
                "create": "would create" if not args.apply else "created",
                "insert": "would insert into" if not args.apply else "inserted into",
                "refresh": "would refresh" if not args.apply else "refreshed",
                "present": "present (no change)",
                "review": f"needs the agentfile judgment edit - {result['reason']}",
            }[result["action"]]
            tag = "OK" if result["status"] in ("ok", "noop", "planned") and result["action"] != "review" else "WARN"
            print(f"  [{tag}]    {target.get('id')}: {verb} ({target.get('path')})")

    summary = {
        "created": counts["create"],
        "inserted": counts["insert"],
        "refreshed": counts["refresh"],
        "present": counts["present"],
        "review": counts["review"],
    }

    if human:
        print()
        prefix = "Plan:" if not args.apply else "Done:"
        print(f"  {prefix} create {counts['create']}, insert {counts['insert']}, "
              f"refresh {counts['refresh']}, present {counts['present']}, review {counts['review']}.")
        if counts["review"]:
            print("  Review targets keep their content unchanged; resolve them with the "
                  "agentfile judgment edit (/grm-sync agentfile).")
        print()
    else:
        reporter.emit(args.format, summary=summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())
