#!/usr/bin/env python3
"""Validates that ASCII directory-tree diagrams in markdown match the filesystem.

Many grimoire and Arcana pages embed file-tree diagrams in fenced code blocks
using the box-drawing characters:

    project/
    ├── README.md
    ├── chapters/
    │   ├── glossary/
    │   └── standards/
    └── log.md

These diagrams drift when folders are renamed, added, or removed and the doc
isn't updated to match. This validator parses every such diagram in the
grimoire (or Arcana), resolves it to a real filesystem anchor when possible,
and reports:

- DOC_TREE_MISSING_ENTRY     — the diagram lists a path that doesn't exist
- DOC_TREE_UNLISTED_ENTRY    — the actual directory has visible children that
                                the diagram (when it claims to be exhaustive)
                                doesn't mention

A diagram is treated as illustrative (and skipped) when ANY of the following
apply, because we cannot meaningfully diff illustration against reality:

- The root line contains a placeholder (`<name>`, `{name}`, `[name]`, `...`)
- The diagram lives under a `templates/` folder
- The doc itself sits inside `sources/`, `inbox/`, or `templates/`
- No anchor (a real directory) can be resolved for the diagram's root

Entries inside an otherwise-real diagram that are themselves placeholders
(`<...>`, `{...}`, `...`, `…`) are skipped per-line; the rest of the diagram
is still validated.

Usage:
    python3 rites/validate_doc_trees.py                       # arcana mode
    python3 rites/validate_doc_trees.py --grimoire <path>     # grimoire mode

Exit codes: 0 = clean, 1 = drift found
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

from _lib import default_arcana_root
from diagnostics import DiagnosticReporter, add_output_format_arg


# Box-drawing markers that introduce a child entry.
BRANCH_RE = re.compile(r"^(?P<indent>.*?)(?P<marker>├──|└──|`--|\|--)\s+(?P<rest>\S.*)$")
# Leading-only indentation prefix (continuation columns).
INDENT_RE = re.compile(r"^(?:[│|]\s*|\s{4})*")
PLACEHOLDER_RE = re.compile(r"[<{\[]|\.\.\.|…|\*")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
TRAILING_COMMENT_RE = re.compile(r"\s+#.*$")

# Folders inside which any tree diagram is treated as illustrative.
ILLUSTRATIVE_PARENT_DIRS = {"templates", "snippets", "scripts", "examples"}

# Top-level scaffold dirs we never descend into when listing real children.
SCAFFOLD_DIRS_SKIPPED = {".git", ".obsidian", "__pycache__", ".venv", "venv", "node_modules"}

# Files at the directory root we treat as routine and don't insist a tree mention.
ROUTINE_ROOT_ENTRIES = {".gitignore", ".gitattributes", ".editorconfig", ".gitkeep"}

# Files at the chapters root that should always appear if not listed.
# (Empty — we don't enforce specific files here; drift on missing entries is
# only reported when the diagram is structurally exhaustive.)


@dataclass(frozen=True)
class TreeEntry:
    """A single line inside a tree diagram, fully resolved to a relative path."""

    line_number: int
    relative_path: str        # path relative to the diagram's anchor
    is_directory: bool
    placeholder: bool


@dataclass
class TreeDiagram:
    """One contiguous tree diagram inside one markdown file."""

    file_path: Path
    start_line: int           # 1-indexed line of the root entry
    anchor_label: str         # raw root line content (without trailing comment)
    entries: list[TreeEntry]
    has_placeholder_root: bool
    has_ellipsis: bool        # diagram contains `...` somewhere = "not exhaustive"


def strip_trailing_comment(text: str) -> str:
    return TRAILING_COMMENT_RE.sub("", text).rstrip()


def looks_like_placeholder(text: str) -> bool:
    if not text:
        return True
    return bool(PLACEHOLDER_RE.search(text))


def parse_tree(lines: list[str], start_index: int, fence_start_line: int) -> tuple[TreeDiagram | None, int]:
    """Parse one contiguous tree starting at lines[start_index].

    Returns (diagram-or-None, next_index_to_consider).
    The root of the tree is lines[start_index]; subsequent lines must start
    with a branch marker until we hit a blank line or non-tree content.
    """
    root_raw = lines[start_index].rstrip()
    if not root_raw.strip():
        return None, start_index + 1
    root_clean = strip_trailing_comment(root_raw).strip()
    if not root_clean:
        return None, start_index + 1
    if BRANCH_RE.match(root_raw):
        # The "root" of this run starts directly with a branch marker; treat
        # that branch line as the first entry of an anchorless tree by using
        # the immediately enclosing directory as anchor. Because we have no
        # named anchor, skip it.
        return None, start_index + 1

    entries: list[TreeEntry] = []
    has_ellipsis = False
    # Stack of (depth_column, directory_path) tracking the active parent for
    # each indentation level. depth_column is the character column at which
    # the parent's branch marker sits (column 0 = the root).
    parent_stack: list[tuple[int, str]] = [(-1, "")]  # root anchor lives at "" with column -1
    next_index = start_index + 1
    while next_index < len(lines):
        raw = lines[next_index].rstrip()
        if not raw.strip():
            break
        branch = BRANCH_RE.match(raw)
        if not branch:
            # Continuation of the current tree only when the line is purely
            # box-drawing indentation; otherwise the tree is done.
            indent_match = INDENT_RE.match(raw)
            if indent_match and not raw[indent_match.end():].strip():
                next_index += 1
                continue
            break

        # Column index where the branch marker starts. Each indentation
        # "column" is typically 4 characters wide (`│   ` or `    `); we use
        # the raw character offset so any column scheme stays consistent.
        marker_column = branch.start("marker")
        # Pop any parents whose column is greater than or equal to ours.
        while parent_stack and parent_stack[-1][0] >= marker_column:
            parent_stack.pop()
        parent_path = parent_stack[-1][1] if parent_stack else ""

        entry_text = strip_trailing_comment(branch.group("rest")).strip()
        if entry_text in ("...", "…"):
            has_ellipsis = True
            next_index += 1
            continue

        is_dir = entry_text.endswith("/")
        bare = entry_text.rstrip("/")
        placeholder = looks_like_placeholder(bare)
        if "..." in bare or "…" in bare:
            has_ellipsis = True

        rel = bare if not parent_path else f"{parent_path}/{bare}"
        entries.append(
            TreeEntry(
                line_number=fence_start_line + next_index + 1,
                relative_path=rel,
                is_directory=is_dir,
                placeholder=placeholder,
            )
        )
        if is_dir:
            parent_stack.append((marker_column, rel))
        next_index += 1

    diagram = TreeDiagram(
        file_path=Path(),  # filled in by caller
        start_line=fence_start_line + start_index + 1,
        anchor_label=root_clean,
        entries=entries,
        has_placeholder_root=looks_like_placeholder(root_clean.rstrip("/").strip()),
        has_ellipsis=has_ellipsis,
    )
    return diagram, next_index


def extract_tree_diagrams(file_path: Path) -> Iterator[TreeDiagram]:
    """Yield every tree diagram inside fenced code blocks of `file_path`."""
    text = file_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    in_fence = False
    fence_marker: str | None = None
    fence_open_line = 0
    fence_lines: list[str] = []
    fence_start_line = 0  # 1-indexed line of the opening fence

    for line_index, raw_line in enumerate(lines):
        fence_match = FENCE_RE.match(raw_line)
        if fence_match:
            marker = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker
                fence_lines = []
                fence_start_line = line_index + 1
                fence_open_line = line_index
                continue
            if marker == fence_marker:
                in_fence = False
                fence_marker = None
                for diagram in _scan_fence(fence_lines, fence_start_line):
                    object.__setattr__(diagram, "file_path", file_path) if False else None
                    diagram.file_path = file_path
                    yield diagram
                continue
        if in_fence:
            fence_lines.append(raw_line)


def _scan_fence(fence_lines: list[str], fence_start_line: int) -> Iterator[TreeDiagram]:
    """Walk fence content and emit each tree diagram found."""
    i = 0
    while i < len(fence_lines):
        # A tree is recognized as: a non-blank line, then at least one line
        # starting with a branch marker within the next 3 lines.
        if not fence_lines[i].strip():
            i += 1
            continue
        if BRANCH_RE.match(fence_lines[i]):
            # Anchorless tree (no named root). Skip.
            i += 1
            continue
        # Lookahead for branch marker.
        lookahead = 1
        found_branch = False
        while lookahead < 4 and i + lookahead < len(fence_lines):
            if BRANCH_RE.match(fence_lines[i + lookahead]):
                found_branch = True
                break
            if not fence_lines[i + lookahead].strip():
                break
            lookahead += 1
        if not found_branch:
            i += 1
            continue
        diagram, next_i = parse_tree(fence_lines, i, fence_start_line)
        if diagram is not None and diagram.entries:
            yield diagram
        i = next_i if next_i > i else i + 1


def resolve_anchor(diagram: TreeDiagram, root: Path) -> Path | None:
    """Return the on-disk directory the diagram is rooted at, or None."""
    label = diagram.anchor_label.rstrip("/").strip()
    if not label or diagram.has_placeholder_root:
        return None
    # Try multiple resolution strategies, prefer the first match.
    candidates: list[Path] = []
    name = label.split("/")[-1]
    # 1. Anchor matches the grimoire root folder name.
    if root.name == name:
        candidates.append(root)
    # 2. Anchor as a relative path from grimoire root (e.g. "chapters/standards").
    rel = label.lstrip("./")
    if rel:
        candidates.append(root / rel)
    # 3. Anchor as a single name resolved anywhere inside grimoire (first match).
    if "/" not in label:
        for found in sorted(root.rglob(name)):
            if found.is_dir():
                candidates.append(found)
                break
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def doc_is_illustrative(path: Path, root: Path) -> bool:
    """Return True if the doc itself is in an illustrative context."""
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return False
    for part in rel_parts:
        if part in ILLUSTRATIVE_PARENT_DIRS:
            return True
        if part in {"sources", "inbox"}:
            return True
        if "<" in part or "{" in part or "[" in part:
            return True
    return False


def real_children(directory: Path) -> set[str]:
    """Return immediate children of `directory` as `name` or `name/` strings,
    excluding scaffold directories and dotfiles unless they're routine.
    """
    out: set[str] = set()
    if not directory.is_dir():
        return out
    for entry in directory.iterdir():
        name = entry.name
        if name in SCAFFOLD_DIRS_SKIPPED:
            continue
        if name.startswith(".") and name not in ROUTINE_ROOT_ENTRIES:
            continue
        out.add(name + "/" if entry.is_dir() else name)
    return out


def listed_children(diagram: TreeDiagram) -> set[str]:
    """Return immediate children mentioned in the diagram as `name` or `name/`."""
    out: set[str] = set()
    for entry in diagram.entries:
        if entry.placeholder:
            continue
        # Only consider top-level entries — lines whose path doesn't traverse
        # an intermediate directory. Because parse_tree resolves relative_path
        # without depth tracking, we infer top-level by the absence of `/`
        # in the bare path. Sub-entries inside the diagram look like a bare
        # name regardless of indent, so we cannot distinguish reliably; treat
        # every named entry as a potential top-level child for the missing-
        # entry check (real_children comparison) and let comments / placeholders
        # filter out the rest.
        if "/" in entry.relative_path:
            # Already a sub-path; skip for top-level child comparison.
            continue
        name = entry.relative_path + ("/" if entry.is_directory else "")
        out.add(name)
    return out


def validate_diagram(
    diagram: TreeDiagram,
    root: Path,
    reporter: DiagnosticReporter,
    human: bool,
) -> None:
    """Apply drift checks to one diagram."""
    if diagram.has_placeholder_root:
        return
    if doc_is_illustrative(diagram.file_path, root):
        return
    anchor = resolve_anchor(diagram, root)
    if anchor is None:
        # No filesystem anchor to validate against — treat as illustrative.
        return

    # MISSING ENTRY checks (diagram lists a path the filesystem doesn't have).
    for entry in diagram.entries:
        if entry.placeholder:
            continue
        target = anchor / entry.relative_path
        if entry.is_directory:
            if not target.is_dir():
                reporter.error(
                    "DOC_TREE_MISSING_ENTRY",
                    f"diagram lists `{entry.relative_path}/` under `{diagram.anchor_label.rstrip('/')}` "
                    f"but the directory does not exist on disk",
                    path=diagram.file_path,
                    line=entry.line_number,
                    hint=f"Either create `{anchor.relative_to(root)}/{entry.relative_path}/` "
                         f"or remove the entry from the diagram.",
                )
                if human:
                    print(
                        f"  MISSING  {diagram.file_path.relative_to(root)}:{entry.line_number} "
                        f"lists `{entry.relative_path}/` not on disk"
                    )
        else:
            if not target.is_file():
                reporter.error(
                    "DOC_TREE_MISSING_ENTRY",
                    f"diagram lists `{entry.relative_path}` under `{diagram.anchor_label.rstrip('/')}` "
                    f"but the file does not exist on disk",
                    path=diagram.file_path,
                    line=entry.line_number,
                    hint=f"Either create `{anchor.relative_to(root)}/{entry.relative_path}` "
                         f"or remove the entry from the diagram.",
                )
                if human:
                    print(
                        f"  MISSING  {diagram.file_path.relative_to(root)}:{entry.line_number} "
                        f"lists `{entry.relative_path}` not on disk"
                    )

    # UNLISTED ENTRY checks (filesystem has a top-level child the diagram
    # doesn't mention). Only emit when the diagram looks structurally
    # exhaustive — no ellipsis marker, no placeholder entries.
    has_placeholders = any(e.placeholder for e in diagram.entries)
    if diagram.has_ellipsis or has_placeholders:
        return
    listed = listed_children(diagram)
    if not listed:
        return
    actual = real_children(anchor)
    # If the diagram listed nothing recognizable as a top-level child, skip.
    if not any(name in actual for name in listed):
        return
    missing_from_diagram = sorted(actual - listed)
    for name in missing_from_diagram:
        # Skip routine root entries the doc legitimately omits unless the
        # diagram clearly lists every other root-level item.
        if name in ROUTINE_ROOT_ENTRIES:
            continue
        reporter.warning(
            "DOC_TREE_UNLISTED_ENTRY",
            f"`{anchor.relative_to(root)}/{name}` exists on disk but is not listed in the diagram",
            path=diagram.file_path,
            line=diagram.start_line,
            hint="Add it to the diagram or add `...` to mark the diagram as non-exhaustive.",
        )
        if human:
            print(
                f"  EXTRA    {diagram.file_path.relative_to(root)}:{diagram.start_line} "
                f"`{name}` exists but not listed"
            )


def collect_markdown_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.md")):
        try:
            rel_parts = path.relative_to(root).parts
        except ValueError:
            continue
        if rel_parts and rel_parts[0] in {"sources", "inbox", ".git", "node_modules"}:
            continue
        # Skip the activity log — historical tree references are preserved.
        if path.name in {"log.md", "CHANGELOG.md"}:
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate ASCII directory-tree diagrams against the filesystem.",
    )
    parser.add_argument(
        "--grimoire",
        type=Path,
        default=None,
        help="Grimoire root (default: Arcana root)",
    )
    add_output_format_arg(parser)
    args = parser.parse_args()

    root = (args.grimoire or default_arcana_root()).expanduser().resolve()
    if not root.is_dir():
        print(f"error: root not found: {root}", file=sys.stderr)
        return 2
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_doc_trees", root)

    files = list(collect_markdown_files(root))
    if human:
        print()
        print("Validating Documented File Trees")
        print("================================")
        print(f"Root: {root}")
        print()

    diagrams_total = 0
    diagrams_validated = 0
    for path in files:
        try:
            for diagram in extract_tree_diagrams(path):
                diagrams_total += 1
                if doc_is_illustrative(path, root):
                    continue
                if diagram.has_placeholder_root:
                    continue
                anchor = resolve_anchor(diagram, root)
                if anchor is None:
                    continue
                diagrams_validated += 1
                validate_diagram(diagram, root, reporter, human)
        except Exception as exc:
            reporter.error(
                "DOC_TREE_PARSE_FAILED",
                f"failed to scan tree diagrams: {exc}",
                path=path,
            )
            if human:
                print(f"  ERROR    {path.relative_to(root)}: parse failed: {exc}")

    if args.format != "human":
        reporter.emit(args.format, checked={"files": len(files), "diagrams": diagrams_total, "validated": diagrams_validated})
        return reporter.exit_code()

    print()
    print(f"Files scanned:      {len(files)}")
    print(f"Diagrams found:     {diagrams_total}")
    print(f"Diagrams validated: {diagrams_validated}")
    print(f"Drift errors:       {reporter.error_count()}")
    print(f"Drift warnings:     {reporter.warning_count()}")
    print()
    print("================================")
    if reporter.error_count():
        print(f"  [FAIL]  Doc-tree drift found ({reporter.error_count()} errors)")
    elif reporter.warning_count():
        print(f"  [WARN]  Doc-tree drift hints ({reporter.warning_count()} warnings)")
    else:
        print("  [OK]    Doc-tree validation passed")
    return reporter.exit_code()


if __name__ == "__main__":
    sys.exit(main())
