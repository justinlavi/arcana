#!/usr/bin/env python3
"""Restructure grimoire content - move/rename or remove a page or chapter.

The mechanical, deterministic core of content reorganization. It does exactly
two things and does them safely:

  --move SRC DST   Rename or move a page or a whole chapter under `chapters/`,
                   rewriting every full-path wikilink that targets the moved
                   file(s) to their new location. Moving a chapter folder also
                   renames its folder-named hub so the hub convention holds.

  --remove PATH    Delete a page or chapter under `chapters/` and report every
                   inbound wikilink that would break, so the caller can repair
                   or reconsider.

What stays judgment (handled by the /grm-move and /grm-remove invocations, not
here): wiring the destination chapter hub, dropping the pointer from a parent
hub, deciding what to do with broken inbound references, appending the activity
log, and re-validating. This rite never edits hubs or guesses intent; it moves
or deletes files and rewrites the links it can resolve exactly.

Mutation profile: plan_apply. The default prints the plan (moves, link
rewrites, or inbound breaks) without writing; `--apply` performs it.

Usage:
    python3 restructure_grimoire.py --grimoire ROOT --move SRC DST [--apply]
    python3 restructure_grimoire.py --grimoire ROOT --remove PATH [--apply]

Exit codes: 0 = plan or apply completed, 1 = refused (invalid target) or error,
2 = argparse invalid arguments.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from _lib import (
    CODE_FENCE_RE,
    WIKILINK_RE,
    add_grimoire_arg,
    err,
    info,
    is_skipped,
    ok,
    resolve_grimoire_arg,
    warn,
    wikilink_target_body,
)
from diagnostics import ResultReporter, add_output_format_arg

INLINE_CODE_RE = re.compile(r"`[^`]*`")

# Directories whose Markdown is not part of the routable chapter graph; their
# wikilinks are left untouched and they are never move/remove targets.
SKIP_DIRS = {"sources", "inbox", "tests", ".git", ".obsidian"}


def rel_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def under_chapters(rel: str) -> bool:
    return rel == "chapters" or rel.startswith("chapters/")


def normalize_rel(root: Path, raw: str) -> str:
    """Return a grimoire-relative POSIX path for a user-supplied target."""
    candidate = (root / raw).resolve()
    try:
        return candidate.relative_to(root.resolve()).as_posix()
    except ValueError:
        return raw.strip().strip("/")


def strip_md(target: str) -> str:
    return target[:-3] if target.endswith(".md") else target


def build_move_map(root: Path, src_rel: str, dst_rel: str) -> dict[str, str]:
    """Map every moved file's old grimoire-relative path to its new path.

    For a chapter folder, the folder-named hub (`<src>/<src>.md`) is remapped to
    `<dst>/<dst>.md` so the hub convention survives a rename; every other file
    keeps its name and only its path prefix changes.
    """
    src_abs = root / src_rel
    move: dict[str, str] = {}
    if src_abs.is_dir():
        src_name = src_rel.split("/")[-1]
        dst_name = dst_rel.split("/")[-1]
        for file in sorted(src_abs.rglob("*.md")):
            old = rel_posix(file, root)
            move[old] = dst_rel + old[len(src_rel):]
        hub_old = f"{src_rel}/{src_name}.md"
        if hub_old in move:
            move[hub_old] = f"{dst_rel}/{dst_name}.md"
    else:
        move[src_rel] = dst_rel
    return move


def target_remap(move: dict[str, str]) -> dict[str, str]:
    """Old -> new wikilink target bodies (paths without the .md suffix)."""
    return {strip_md(old): strip_md(new) for old, new in move.items()}


def rebuild_target(target: str, new_body: str) -> str:
    """Swap the path body of a wikilink target, preserving #section and |label."""
    left, _, label = target.partition("|")
    section = ""
    if "#" in left:
        section = "#" + left.split("#", 1)[1]
    suffix = f"|{label}" if label else ""
    return f"{new_body}{section}{suffix}"


def rewrite_links_in_text(text: str, remap: dict[str, str]) -> tuple[str, int]:
    """Rewrite wikilink bodies found in `remap`, skipping code fences/inline code."""
    out: list[str] = []
    count = 0
    in_fence = False
    for line in text.splitlines(keepends=True):
        if CODE_FENCE_RE.match(line.rstrip("\r\n")):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        scan = INLINE_CODE_RE.sub(lambda m: " " * len(m.group()), line)
        edits = []
        for match in WIKILINK_RE.finditer(scan):
            body = wikilink_target_body(match.group(1))
            if body in remap:
                edits.append((match.start(), match.end(),
                              f"[[{rebuild_target(match.group(1), remap[body])}]]"))
        if not edits:
            out.append(line)
            continue
        new_line = line
        for start, end, replacement in sorted(edits, key=lambda e: e[0], reverse=True):
            new_line = new_line[:start] + replacement + new_line[end:]
        count += len(edits)
        out.append(new_line)
    return "".join(out), count


def iter_markdown(root: Path):
    """Yield every routable Markdown file (the link graph the move/remove edits)."""
    for path in sorted(root.rglob("*.md")):
        rel = rel_posix(path, root)
        if is_skipped(rel, SKIP_DIRS):
            continue
        yield path


def find_inbound_links(root: Path, bodies: set[str], exclude: set[str]) -> list[tuple[str, int, str]]:
    """Return (file_rel, line_no, target) for wikilinks pointing at `bodies`."""
    hits: list[tuple[str, int, str]] = []
    for path in iter_markdown(root):
        rel = rel_posix(path, root)
        if rel in exclude:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        in_fence = False
        for line_no, line in enumerate(text.splitlines(), start=1):
            if CODE_FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            scan = INLINE_CODE_RE.sub(lambda m: " " * len(m.group()), line)
            for match in WIKILINK_RE.finditer(scan):
                if wikilink_target_body(match.group(1)) in bodies:
                    hits.append((rel, line_no, match.group(1)))
    return hits


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def refuse(reporter: ResultReporter, human: bool, message: str) -> int:
    reporter.message("error", message)
    if human:
        err(message)
        print()
    return 1


def validate_target(root: Path, rel: str, *, must_exist: bool) -> str | None:
    """Return an error string if `rel` is not a legal move/remove target."""
    if not under_chapters(rel) or rel == "chapters":
        return f"{rel} is not under chapters/ - this rite reorganizes chapter content only"
    abs_path = root / rel
    if must_exist and not abs_path.exists():
        return f"{rel} does not exist"
    return None


def is_folder_hub(root: Path, rel: str) -> bool:
    """True when rel is a folder-named hub file (chapters/<c>/<c>.md)."""
    path = Path(rel)
    return path.suffix == ".md" and path.stem == path.parent.name and path.parent.name != "chapters"


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------


def do_move(root: Path, src: str, dst: str, *, apply: bool, reporter: ResultReporter,
            human: bool, fmt: str) -> int:
    src_rel = normalize_rel(root, src)
    dst_rel = normalize_rel(root, dst)

    for rel, must in ((src_rel, True), (dst_rel, False)):
        error = validate_target(root, rel, must_exist=must)
        if error:
            return refuse(reporter, human, error)
    if (root / dst_rel).exists():
        return refuse(reporter, human, f"{dst_rel} already exists - choose a destination that does not exist")
    if dst_rel == src_rel or dst_rel.startswith(src_rel + "/") or src_rel.startswith(dst_rel + "/"):
        return refuse(reporter, human,
                      f"cannot move {src_rel} into itself or its own subpath ({dst_rel})")
    dst_parent = (root / dst_rel).parent
    if dst_parent.exists() and not dst_parent.is_dir():
        return refuse(reporter, human,
                      f"{Path(dst_rel).parent.as_posix()} exists but is not a directory")
    src_abs = root / src_rel
    if src_abs.is_file() and is_folder_hub(root, src_rel):
        return refuse(reporter, human,
                      f"{src_rel} is a chapter hub - move the whole chapter folder "
                      f"({Path(src_rel).parent.as_posix()}) instead of the hub file alone")

    move = build_move_map(root, src_rel, dst_rel)
    remap = target_remap(move)

    # Apply moves the files first, then retargets every wikilink across the
    # post-move tree, so a failed rename can never leave links rewritten for a
    # move that did not happen. Plan mode counts the same rewrites without writing
    # (file content is identical before and after the rename), so the plan
    # predicts the apply.
    if apply:
        was_dir = src_abs.is_dir()
        dst_abs = root / dst_rel
        dst_abs.parent.mkdir(parents=True, exist_ok=True)
        src_abs.rename(dst_abs)
        if was_dir:
            src_name = src_rel.split("/")[-1]
            dst_name = dst_rel.split("/")[-1]
            if src_name != dst_name:
                old_hub = dst_abs / f"{src_name}.md"
                if old_hub.is_file():
                    old_hub.rename(dst_abs / f"{dst_name}.md")
        for old, new in sorted(move.items()):
            reporter.mutation("move", path=new, detail=f"{old} -> {new}")

    rewrites: list[tuple[str, int]] = []
    for path in iter_markdown(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        new_text, n = rewrite_links_in_text(text, remap)
        if n:
            rewrites.append((rel_posix(path, root), n))
            if apply:
                path.write_text(new_text, encoding="utf-8", newline="\n")
                reporter.mutation("repair", path=rel_posix(path, root),
                                  detail=f"{n} wikilink(s) retargeted")

    total_rewrites = sum(n for _, n in rewrites)
    if human:
        verb = "Moved" if apply else "Would move"
        print(f"  {verb} {len(move)} file(s):")
        for old, new in sorted(move.items()):
            print(f"    {old} -> {new}")
        link_verb = "Rewrote" if apply else "Would rewrite"
        print(f"  {link_verb} {total_rewrites} wikilink(s) across {len(rewrites)} file(s).")
        if not apply:
            print("  Re-run with --apply to perform the move.")
        print()
    if not human:
        reporter.emit(fmt,
                      summary={"moved": len(move), "link_rewrites": total_rewrites,
                               "files_relinked": len(rewrites), "applied": apply})
    return 0


def do_remove(root: Path, target: str, *, apply: bool, reporter: ResultReporter,
              human: bool, fmt: str) -> int:
    rel = normalize_rel(root, target)
    error = validate_target(root, rel, must_exist=True)
    if error:
        return refuse(reporter, human, error)
    if is_folder_hub(root, rel):
        return refuse(reporter, human,
                      f"{rel} is a chapter hub - remove the whole chapter folder "
                      f"({Path(rel).parent.as_posix()}) instead of the hub file alone")

    abs_path = root / rel
    removed_files = (
        [rel_posix(f, root) for f in sorted(abs_path.rglob("*.md"))]
        if abs_path.is_dir() else [rel]
    )
    bodies = {strip_md(f) for f in removed_files}
    inbound = find_inbound_links(root, bodies, exclude=set(removed_files))

    for src_rel, line_no, tgt in inbound:
        reporter.message("warning",
                         f"{src_rel}:{line_no}: [[{tgt}]] points at content being removed",
                         path=src_rel)
    if apply:
        if abs_path.is_dir():
            shutil.rmtree(abs_path)
        else:
            abs_path.unlink()
        reporter.mutation("remove", path=rel, detail=f"removed {len(removed_files)} page(s)")

    if human:
        verb = "Removed" if apply else "Would remove"
        print(f"  {verb} {rel} ({len(removed_files)} page(s)).")
        if inbound:
            print(f"  {len(inbound)} inbound wikilink(s) point at removed content "
                  f"and will break - repair or reconsider:")
            for src_rel, line_no, tgt in inbound:
                print(f"    {src_rel}:{line_no}: [[{tgt}]]")
        else:
            print("  No inbound wikilinks point at the removed content.")
        if not apply:
            print("  Re-run with --apply to perform the removal.")
        print()
    if not human:
        reporter.emit(fmt,
                      summary={"removed_pages": len(removed_files),
                               "inbound_breaks": len(inbound), "applied": apply})
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Restructure grimoire content (move/remove)")
    add_grimoire_arg(parser)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--move", nargs=2, metavar=("SRC", "DST"),
                       help="Move or rename a page or chapter under chapters/")
    group.add_argument("--remove", metavar="PATH",
                       help="Delete a page or chapter under chapters/")
    parser.add_argument("--apply", action="store_true",
                        help="Perform the change (default: plan only)")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"
    root = resolve_grimoire_arg(args.grimoire)

    reporter = ResultReporter(
        "restructure_grimoire", root=root, mode="apply" if args.apply else "plan"
    )

    if human:
        print()
        print("  Restructure Grimoire")
        print("  ----------------------------")
        print(f"  Grimoire: {root}")
        print(f"  Mode:     {'apply' if args.apply else 'plan (use --apply to write)'}")
        print()

    if args.move:
        return do_move(root, args.move[0], args.move[1], apply=args.apply,
                       reporter=reporter, human=human, fmt=args.format)
    return do_remove(root, args.remove, apply=args.apply, reporter=reporter,
                     human=human, fmt=args.format)


if __name__ == "__main__":
    sys.exit(main())
