#!/usr/bin/env python3
"""Agent instruction-block injector - deterministic create / insert / refresh.

Sister to `sync_skills.py` (skill registration) and `sync_library.py` (library
reconciliation). Where those keep the skill directories and the library in sync
with reality, this rite keeps the marked Grimoire routing block in each
automatic agent instruction file (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`,
...) in sync with the canonical template.

It handles the mechanical majority deterministically and leaves only genuinely
ambiguous files to a human/AI judgment edit:

  * absent file    -> create it with `# <title>` and the canonical block
  * file, no block -> insert the canonical block
  * one clean marked region -> refresh it in place (idempotent: a block that
    already matches the template is left untouched)
  * legacy heading-only block (no BEGIN/END markers) -> reported present,
    left as-is (upgrading it has no marker boundary, so it is judgment work)
  * duplicate or malformed markers -> reported ambiguous and skipped, for the
    `/grm-sync agentfile` (or `/arc-sync agentfile`) judgment edit

The canonical block text and the BEGIN/END/heading sentinels are single-sourced
from `summon_core`, so this detector and the install-time injector can never
disagree. Writes are UTF-8 without BOM and LF line endings.

Mutation profile: plan_apply. The default mode plans (reports per-target
actions without writing); `--apply` performs the deterministic create/insert/
refresh actions.

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
HEADING_SENTINEL = summon_core.HEADING_SENTINEL

# Actions that write to disk under --apply.
WRITING_ACTIONS = ("create", "insert", "replace")


class _QuietLog:
    """No-op logger so the reused summon_core injector stays silent here.

    This rite renders its own per-target lines from the structured results; the
    underlying summon_core.inject_agent_file only calls .info/.ok.
    """

    def info(self, msg: str) -> None:  # noqa: D401 - logger surface
        pass

    def ok(self, msg: str) -> None:
        pass

    def warn(self, msg: str) -> None:
        pass

    def err(self, msg: str) -> None:
        pass

    def line(self, text: str) -> None:
        pass


def canonical_marked_block() -> str:
    """Return the canonical BEGIN..END block with no surrounding blank lines."""
    return summon_core.GRIMOIRE_BLOCK.strip()


def plan_block(content: str | None) -> tuple[str, str]:
    """Classify the action one target needs. Returns (action, reason).

    `content` is the file text, or None when the file does not exist. `action`
    is one of: create, insert, replace, present, ambiguous.
    """
    if content is None:
        return "create", "file absent"

    has_begin = BEGIN_SENTINEL in content
    has_end = END_SENTINEL in content
    has_heading = HEADING_SENTINEL in content

    if not has_begin and not has_end:
        if has_heading:
            return "present", "legacy heading-only block"
        return "insert", "no Grimoire block"

    if content.count(BEGIN_SENTINEL) == 1 and content.count(END_SENTINEL) == 1:
        begin = content.find(BEGIN_SENTINEL)
        end = content.find(END_SENTINEL)
        if begin < end:
            region = content[begin : end + len(END_SENTINEL)]
            if region == canonical_marked_block():
                return "present", "canonical block present"
            return "replace", "refresh marked block"

    return "ambiguous", "duplicate or malformed Grimoire markers"


def _refresh_marked_region(content: str) -> str:
    """Replace the single clean BEGIN..END region with the canonical block."""
    begin = content.find(BEGIN_SENTINEL)
    end = content.find(END_SENTINEL) + len(END_SENTINEL)
    return content[:begin] + canonical_marked_block() + content[end:]


def apply_block(path: Path, title: str, *, apply: bool) -> dict[str, Any]:
    """Plan, and under `apply` perform, the block action for one target.

    Returns {"path", "action", "reason", "status"}. `status` is "planned" in
    plan mode; in apply mode it is "ok" (wrote), "noop" (already present), or
    "skipped" (ambiguous - left for the judgment edit).
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

    if action in ("create", "insert"):
        # summon_core.inject_agent_file creates an absent file with `# <title>`
        # and inserts the canonical block, or inserts into a block-less file.
        summon_core.inject_agent_file(_QuietLog(), path, title)
        result["status"] = "ok"
    elif action == "replace":
        path.write_text(_refresh_marked_region(content), encoding="utf-8", newline="\n")
        result["status"] = "ok"
    elif action == "ambiguous":
        result["status"] = "skipped"
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
            reporter.mutation(action, path=path, detail=f"{action} Grimoire block in {tid}")
        else:
            reporter.message("info", f"would {action} Grimoire block in {tid} ({path})", path=path)
    elif action == "ambiguous":
        reporter.message(
            "warning",
            f"{tid}: {result['reason']} - left for the agentfile judgment edit ({path})",
            path=path,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent instruction-block injector")
    parser.add_argument(
        "--agent",
        default="all",
        help="Agent instruction target id from rites/data/agent_targets.json (default: all)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create, insert, or refresh the Grimoire block (default: plan only)",
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
        print("  Agent Instruction Block Injector")
        print("  --------------------------------")
        if not args.apply:
            print("  [INFO]  Plan mode - no files will be written")
        print()

    if not targets:
        if human:
            print(f"  [WARN]  No automatic instruction target matched --agent {args.agent!r}")
            print()
        else:
            reporter.message("warning", f"no automatic instruction target matched --agent {args.agent!r}")
            reporter.emit(args.format, summary={"created": 0, "inserted": 0, "refreshed": 0,
                                                "present": 0, "ambiguous": 0})
        return 0

    counts = {"create": 0, "insert": 0, "replace": 0, "present": 0, "ambiguous": 0}
    for target in targets:
        result = apply_block(Path(target["path"]), target.get("title") or Path(target["path"]).name,
                             apply=args.apply)
        counts[result["action"]] = counts.get(result["action"], 0) + 1
        _record(reporter, target, result, args.apply)
        if human:
            verb = {
                "create": "would create" if not args.apply else "created",
                "insert": "would insert into" if not args.apply else "inserted into",
                "replace": "would refresh" if not args.apply else "refreshed",
                "present": "present (no change)",
                "ambiguous": "ambiguous - needs the agentfile judgment edit",
            }[result["action"]]
            print(f"  [{ 'OK' if result['status'] in ('ok', 'noop') else 'WARN' }]    "
                  f"{target.get('id')}: {verb} ({target.get('path')})")

    summary = {
        "created": counts["create"],
        "inserted": counts["insert"],
        "refreshed": counts["replace"],
        "present": counts["present"],
        "ambiguous": counts["ambiguous"],
    }

    if human:
        print()
        if args.apply:
            print(f"  Created {counts['create']}, inserted {counts['insert']}, "
                  f"refreshed {counts['replace']}, present {counts['present']}, "
                  f"ambiguous {counts['ambiguous']}.")
        else:
            print(f"  Plan: create {counts['create']}, insert {counts['insert']}, "
                  f"refresh {counts['replace']}, present {counts['present']}, "
                  f"ambiguous {counts['ambiguous']}.")
        if counts["ambiguous"]:
            print("  Ambiguous targets keep existing content; refresh them with the "
                  "agentfile judgment edit.")
        print()
    else:
        reporter.emit(args.format, summary=summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())
