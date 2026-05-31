#!/usr/bin/env python3
"""Repair filename-only wikilinks to canonical full-path form.

Scans markdown files for broken wikilinks of the form ``[[basename]]`` or
``[[basename|label]]`` (Obsidian shorthand that doesn't resolve under Arcana's
full-path rule) and rewrites them as ``[[chapters/<path>/<basename>|<label>]]``.

Resolution order, first hit wins:

  (a) sibling in the source file's own directory
  (b) unique descendant of the source file's directory
  (c) unique descendant of the source file's chapter root
  (d) globally unique match anywhere under ``chapters/``

Ambiguous and unresolvable cases are reported and skipped - never guessed.

Defaults to dry-run; pass ``--apply`` to write changes.

Exit codes: ``--apply`` returns 0 when it completes successfully - resolvable
links are written, and any remaining ambiguous/unresolvable links are reported
for human follow-up rather than treated as a failure. Dry-run returns 1 when
there is actionable work (repairs to apply, or links needing attention) and 0
when the grimoire is already clean. Placeholder-like links are reported and
skipped, never silently dropped.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

from _lib import (
    CODE_FENCE_RE,
    WIKILINK_RE,
    add_grimoire_arg,
    err,
    info,
    is_skipped,
    ok,
    resolve_grimoire_arg,
    resolve_wikilink_path,
    warn,
    wikilink_target_body,
)
from diagnostics import ResultReporter, add_output_format_arg


INLINE_CODE_RE = re.compile(r"`[^`]*`")


SKIP_DIRS = {
    "invocations/arcana/validators",
    "invocations/arcana/quality",
    "sources",
    "inbox",
    "tests",
    ".git",
    ".obsidian",
}

SKIP_FILES = {"operating_model.md"}

PLACEHOLDER_TOKENS = [
    "{", "<", "invocation_name", "chapter_name", "file_name",
    "ARCANA_HOME", "GRIMOIRE_PATH", "ARCANA_PATH",
    "Chapter Name", "Title", "Sub-topic", "filename",
    "related_page", "sub_topic", "related_chapter",
    "path/to/related", "path/url/system", "Source title",
]


def wikilink_display(target: str) -> str:
    if "|" not in target:
        return ""
    return target.split("|", 1)[1].strip()


def chapter_root_of(rel_path: Path) -> Optional[Path]:
    """For chapters/<chapter>/foo/bar.md return chapters/<chapter>; else None."""
    parts = rel_path.parts
    if len(parts) >= 2 and parts[0] == "chapters":
        return Path(parts[0]) / parts[1]
    return None


def build_basename_index(grimoire_root: Path) -> dict[str, list[Path]]:
    """Map every markdown basename (no .md) -> list of absolute paths."""
    index: dict[str, list[Path]] = {}
    chapters_dir = grimoire_root / "chapters"
    if not chapters_dir.is_dir():
        return index
    for path in chapters_dir.rglob("*.md"):
        index.setdefault(path.stem, []).append(path)
    return index


def resolve_basename(
    basename: str,
    source_abs: Path,
    grimoire_root: Path,
    index: dict[str, list[Path]],
) -> tuple[Optional[Path], list[Path]]:
    """Return (chosen, candidates). chosen=None means ambiguous or absent."""
    candidates = index.get(basename, [])
    if not candidates:
        return None, []

    src_dir = source_abs.parent
    rel_src = source_abs.relative_to(grimoire_root)
    src_chapter = chapter_root_of(rel_src)
    src_chapter_abs = (grimoire_root / src_chapter) if src_chapter else None

    # (a) sibling
    siblings = [c for c in candidates if c.parent == src_dir and c != source_abs]
    if len(siblings) == 1:
        return siblings[0], candidates
    if len(siblings) > 1:
        return None, candidates  # impossible (one dir, one basename) but be safe

    # (b) descendant of src_dir
    under_src_dir = [c for c in candidates if src_dir in c.parents]
    if len(under_src_dir) == 1:
        return under_src_dir[0], candidates

    # (c) descendant of source chapter
    if src_chapter_abs:
        under_chapter = [c for c in candidates if src_chapter_abs in c.parents or c.parent == src_chapter_abs]
        if len(under_chapter) == 1:
            return under_chapter[0], candidates

    # (d) globally unique
    if len(candidates) == 1:
        return candidates[0], candidates

    return None, candidates


def is_placeholder(text: str) -> bool:
    return any(tok in text for tok in PLACEHOLDER_TOKENS)


def repair_line(
    line: str,
    source_path: Path,
    grimoire_root: Path,
    index: dict[str, list[Path]],
    rel: str,
    line_no: int,
    reporter: ResultReporter,
    apply: bool,
) -> tuple[str, list[str], list[str], list[str], list[str]]:
    """Repair a single non-fence line.

    Returns (new_line, fixes, ambis, unresolvables, skipped_placeholders).
    Structured records (mutations/messages) are collected into ``reporter``.
    Repairs are recorded as mutations only in ``apply`` mode (when they are
    actually written to disk); in plan mode they surface via the summary counts.
    """
    # Mask inline backticks with same-length spaces so positions within this
    # line stay aligned between the scanable view and the actual line we rewrite.
    scanable = INLINE_CODE_RE.sub(lambda m: " " * len(m.group()), line)

    edits: list[tuple[int, int, str]] = []
    fixes: list[str] = []
    ambis: list[str] = []
    unresolvables: list[str] = []
    skipped: list[str] = []

    for match in WIKILINK_RE.finditer(scanable):
        target = match.group(1)
        if is_placeholder(target):
            skipped.append(
                f"  [SKIP]  {rel}:{line_no}: [[{target}]] - looks like a template "
                "placeholder; not repaired"
            )
            reporter.message(
                "info",
                f"{rel}:{line_no}: [[{target}]] looks like a template placeholder; not repaired",
                path=source_path,
            )
            continue
        if resolve_wikilink_path(wikilink_target_body(target), grimoire_root) is not None:
            continue

        body = wikilink_target_body(target)
        if "/" in body or not body:
            unresolvables.append(
                f"  [SKIP]  {rel}:{line_no}: [[{target}]] - partial path or empty, not a simple basename"
            )
            reporter.message(
                "warning",
                f"{rel}:{line_no}: [[{target}]] is a partial path or empty, not a simple basename",
                path=source_path,
            )
            continue

        basename = body
        chosen, candidates = resolve_basename(basename, source_path, grimoire_root, index)

        fallback_note = ""
        if chosen is None and not candidates:
            display = wikilink_display(target)
            if display and re.fullmatch(r"[A-Za-z0-9_\-]+", display):
                chosen2, candidates2 = resolve_basename(display, source_path, grimoire_root, index)
                if chosen2 is not None or candidates2:
                    candidates = candidates2
                    basename = display
                    fallback_note = " (via display-label fallback)"
                    if chosen2 is not None:
                        chosen = chosen2

        if chosen is None:
            if not candidates:
                unresolvables.append(
                    f"  [MISS] {rel}:{line_no}: [[{target}]] - no file named {body}.md anywhere in chapters/"
                )
                reporter.message(
                    "warning",
                    f"{rel}:{line_no}: [[{target}]] has no file named {body}.md anywhere in chapters/",
                    path=source_path,
                )
            else:
                cand_rels = [str(c.relative_to(grimoire_root)) for c in candidates]
                ambis.append(
                    f"  [AMBI] {rel}:{line_no}: [[{target}]] - {len(candidates)} candidates: {', '.join(cand_rels)}{fallback_note}"
                )
                reporter.message(
                    "warning",
                    f"{rel}:{line_no}: [[{target}]] is ambiguous - {len(candidates)} candidates: "
                    f"{', '.join(cand_rels)}{fallback_note}",
                    path=source_path,
                )
            continue

        rel_target = chosen.relative_to(grimoire_root).with_suffix("")
        display = wikilink_display(target) or basename
        new_wikilink = f"[[{rel_target}|{display}]]"

        edits.append((match.start(), match.end(), new_wikilink))
        fixes.append(
            f"  [FIX]   {rel}:{line_no}: [[{target}]] -> {new_wikilink}{fallback_note}"
        )
        if apply:
            reporter.mutation(
                "repair",
                path=source_path,
                detail=f"[[{target}]] -> {new_wikilink}{fallback_note}",
            )

    if not edits:
        return line, fixes, ambis, unresolvables, skipped

    # Apply right-to-left so earlier offsets in this line stay valid.
    new_line = line
    for start, end, new_wikilink in sorted(edits, key=lambda e: e[0], reverse=True):
        new_line = new_line[:start] + new_wikilink + new_line[end:]
    return new_line, fixes, ambis, unresolvables, skipped


def repair_file(
    path: Path,
    grimoire_root: Path,
    index: dict[str, list[Path]],
    apply: bool,
    reporter: ResultReporter,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Return (repairs, ambiguous, unresolvable, skipped) report lines for this file.

    Structured records (mutations/messages) are collected into ``reporter``.
    """
    rel = str(path.relative_to(grimoire_root))
    try:
        original = path.read_text(errors="replace")
    except OSError as exc:
        reporter.message("warning", f"{rel}: read failed: {exc}", path=path)
        return [], [], [f"  [ERROR] {rel}: read failed: {exc}"], []

    repair_lines: list[str] = []
    ambiguous_lines: list[str] = []
    unresolvable_lines: list[str] = []
    skipped_lines: list[str] = []

    in_fence = False
    new_lines: list[str] = []

    for line_no, line in enumerate(original.splitlines(keepends=True), start=1):
        bare = line.rstrip("\r\n")
        if CODE_FENCE_RE.match(bare):
            in_fence = not in_fence
            new_lines.append(line)
            continue
        if in_fence:
            new_lines.append(line)
            continue

        new_line, fixes, ambis, unr, skip = repair_line(
            line, path, grimoire_root, index, rel, line_no, reporter, apply
        )
        new_lines.append(new_line)
        repair_lines.extend(fixes)
        ambiguous_lines.extend(ambis)
        unresolvable_lines.extend(unr)
        skipped_lines.extend(skip)

    if apply and repair_lines:
        new_content = "".join(new_lines)
        if new_content != original:
            path.write_text(new_content)

    return repair_lines, ambiguous_lines, unresolvable_lines, skipped_lines


def iter_target_files(grimoire_root: Path):
    """Yield every .md file in the grimoire that the link validator would scan."""
    for path in sorted(grimoire_root.rglob("*.md")):
        rel = str(path.relative_to(grimoire_root))
        if path.name in SKIP_FILES:
            continue
        if is_skipped(rel, SKIP_DIRS):
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Repair filename-only wikilinks to full-path form"
    )
    add_grimoire_arg(parser)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes (default: dry-run, report only)",
    )
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"
    grimoire_root = resolve_grimoire_arg(args.grimoire)

    reporter = ResultReporter(
        "repair_links",
        root=grimoire_root,
        mode="apply" if args.apply else "plan",
    )

    if human:
        print()
        print("Repairing Wikilinks")
        print("==================================")
        print(f"Grimoire root: {grimoire_root}")
        print(f"Mode:          {'apply' if args.apply else 'dry-run'}")
        print()

    index = build_basename_index(grimoire_root)
    if human:
        info(f"Indexed {sum(len(v) for v in index.values())} chapter pages "
             f"under {len(index)} distinct basenames "
             f"({sum(1 for v in index.values() if len(v) > 1)} basename collisions)")
        print()

    all_repairs: list[str] = []
    all_ambiguous: list[str] = []
    all_unresolvable: list[str] = []
    all_skipped: list[str] = []
    files_touched = 0

    for path in iter_target_files(grimoire_root):
        r, a, u, s = repair_file(path, grimoire_root, index, args.apply, reporter)
        if r:
            files_touched += 1
        all_repairs.extend(r)
        all_ambiguous.extend(a)
        all_unresolvable.extend(u)
        all_skipped.extend(s)

    if human:
        if all_repairs:
            print(f"Repairs ({len(all_repairs)}):")
            for line in all_repairs:
                print(line)
            print()

        if all_ambiguous:
            print(f"Ambiguous - needs human resolution ({len(all_ambiguous)}):")
            for line in all_ambiguous:
                print(line)
            print()

        if all_unresolvable:
            print(f"Unresolvable - no target found ({len(all_unresolvable)}):")
            for line in all_unresolvable:
                print(line)
            print()

        if all_skipped:
            print(f"Skipped - placeholder-like, not repaired ({len(all_skipped)}):")
            for line in all_skipped:
                print(line)
            print()

        print("==================================")

    summary = (
        f"Repairs: {len(all_repairs)} across {files_touched} file(s); "
        f"ambiguous: {len(all_ambiguous)}; unresolvable: {len(all_unresolvable)}; "
        f"skipped: {len(all_skipped)}"
    )
    if human:
        if args.apply and all_repairs:
            ok(summary + " - applied")
        elif all_repairs:
            info(summary + " - dry-run, pass --apply to write")
        else:
            ok(summary)

    needs_attention = bool(all_ambiguous or all_unresolvable)

    if not human:
        reporter.emit(args.format, summary={
            "repairs": len(all_repairs),
            "ambiguous": len(all_ambiguous),
            "unresolvable": len(all_unresolvable),
            "skipped": len(all_skipped),
            "files_touched": files_touched,
        })

    if args.apply:
        # The apply itself succeeded; ambiguous/unresolvable links are reported
        # for human follow-up, not treated as a failure of this run.
        return 0
    # Dry-run behaves as a check: signal when there is actionable work.
    return 1 if (all_repairs or needs_attention) else 0


if __name__ == "__main__":
    sys.exit(main())
