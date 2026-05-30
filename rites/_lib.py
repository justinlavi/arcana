"""Shared utilities for Arcana rites.

Centralizes the patterns that every validator and library utility needs:
frontmatter parsing, markdown link/code-fence helpers, the canonical logger,
grimoire-root resolution, manifest / library loading, and the skill_prefix regex.

New rites should import from here rather than redefining these primitives.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable, Optional


# ---------------------------------------------------------------------------
# Regexes - shared across validators
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
LINK_RE = re.compile(r"\]\(([^)]+)\)")
WIKILINK_RE = re.compile(r"\[\[([^\]\n]+)\]\]")
CODE_FENCE_RE = re.compile(r"^```")
SKILL_PREFIX_RE = re.compile(r"^[a-z][a-z0-9]*$")
SKILL_SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------------------
# Logging - uniform `[LEVEL]` prefix in 2-space indent
# ---------------------------------------------------------------------------


def info(msg: str) -> None:
    print(f"  [INFO]  {msg}")


def ok(msg: str) -> None:
    print(f"  [OK]    {msg}")


def warn(msg: str) -> None:
    print(f"  [WARN]  {msg}")


def err(msg: str) -> None:
    print(f"  [ERROR] {msg}")


# ---------------------------------------------------------------------------
# Grimoire root resolution
# ---------------------------------------------------------------------------


def default_arcana_root() -> Path:
    """Return the Arcana root: ARCANA_HOME env var, else this file's parent.parent.

    Validators and rites that operate on Arcana itself use this as their fallback
    when no `--grimoire` flag is supplied.
    """
    return Path(os.environ.get("ARCANA_HOME", Path(__file__).resolve().parent.parent))


def add_grimoire_arg(parser: argparse.ArgumentParser, flag: str = "--grimoire") -> None:
    """Register the standard `--grimoire <path>` flag on a parser.

    The default is `default_arcana_root()`, so a script invoked without args
    operates on Arcana itself; passing `--grimoire ~/grimoires/cooking-grimoire`
    points the same script at any grimoire.
    """
    parser.add_argument(
        flag,
        type=Path,
        default=default_arcana_root(),
        help="Grimoire root (default: ARCANA_HOME env var or rites parent)",
    )


def resolve_grimoire_arg(path: Path) -> Path:
    """Expanduser + resolve, used after argparse to normalize the --grimoire value."""
    return path.expanduser().resolve()


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------


def parse_frontmatter(text: str) -> dict:
    """Parse a markdown file's YAML frontmatter into a dict.

    Returns `{}` when no frontmatter block is present.

    Supported syntax (the subset Arcana uses):

        key: value
        key: "quoted value"
        key: [a, b, "c"]
        key:
         - item
         - item

    Returns `dict[str, str | list[str]]`. Lines that don't match any form are
    ignored - the parser is forgiving by design (it's a linter helper, not a
    full YAML implementation).
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}

    fields: dict = {}
    current_list_key: Optional[str] = None

    for raw_line in match.group(1).splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            current_list_key = None
            continue

        # Multi-line list continuation (` - item`)
        if current_list_key is not None and re.match(r"^\s+-\s+", raw_line):
            value = raw_line.split("-", 1)[1].strip().strip("'\"")
            fields[current_list_key].append(value)
            continue

        current_list_key = None

        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if not value:
            # Empty value may be followed by a multi-line list.
            fields[key] = []
            current_list_key = key
            continue

        # Inline list: [a, b, "c"]
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                fields[key] = []
            else:
                fields[key] = [
                    piece.strip().strip("'\"") for piece in re.split(r",\s*", inner)
                ]
            continue

        fields[key] = value.strip("'\"")

    return fields


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------


def strip_code_blocks(content: str) -> str:
    """Replace fenced code blocks and inline backticks with whitespace.

    Used by link/orphan validators so links inside code samples don't trigger
    false positives. Preserves line numbering so error messages stay useful.
    """
    out = []
    in_fence = False
    for line in content.splitlines():
        if CODE_FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        out.append(re.sub(r"`[^`]*`", lambda m: " " * len(m.group()), line))
    return "\n".join(out)


def wikilink_target_body(target: str) -> str:
    """Return the target portion of a wikilink, without display text or section.

    Examples:
      ``page|Label`` -> ``page``
      ``chapters/places/places#Routes|Places`` -> ``chapters/places/places``
    """
    return target.split("|", 1)[0].split("#", 1)[0].strip()


def resolve_wikilink_path(body: str, root: Path) -> Optional[Path]:
    """Resolve a full-path wikilink target against a grimoire root.

    Wikilinks are repository-root relative paths, with the ``.md`` suffix
    optional for Obsidian compatibility. Aliases and global filename-stem
    matches are intentionally not resolved.

    Multi-dot filenames are supported: ``[[path/to/plugin_ICD.template]]``
    resolves to ``path/to/plugin_ICD.template.md``. The convention covers
    capitalized acronym suffixes (ICD, IDD, SDK) and role suffixes
    (``.template``, ``.example``) that grimoires use deliberately.
    """
    if not body:
        return None

    candidate = Path(body)
    if candidate.is_absolute():
        return None

    # Try variants in priority order: body+.md first (Obsidian default), then
    # body as-given (in case the wikilink already includes the .md suffix).
    if candidate.suffix == ".md":
        tries = [candidate]
    else:
        tries = [Path(str(candidate) + ".md"), candidate]

    for cand in tries:
        resolved_raw = root / cand
        try:
            resolved = resolved_raw.resolve()
        except OSError:
            continue
        try:
            resolved.relative_to(root)
        except ValueError:
            continue
        if resolved.is_file() and resolved.suffix == ".md":
            return resolved
    return None


# ---------------------------------------------------------------------------
# Manifest / library
# ---------------------------------------------------------------------------


def load_manifest(directory: Path) -> tuple[Optional[dict], list]:
    """Load and shallow-validate a grimoire's `grimoire.json` manifest.

    Returns `(manifest_dict, errors)`. `manifest_dict` is `None` when the file
    is missing or unparseable; otherwise it's the parsed JSON regardless of
    validation outcome (so callers can still inspect partial data).

    Validation covers the universal fields: `name`, `skill_prefix` (must match
    `SKILL_PREFIX_RE`). Callers needing stricter checks (e.g. skill_prefix
    collisions across grimoires) compose on top.
    """
    manifest_file = directory / "grimoire.json"
    if not manifest_file.is_file():
        return None, ["missing grimoire.json"]

    try:
        with open(manifest_file) as f:
            metadata = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return None, [f"could not parse grimoire.json: {exc}"]

    errors = []
    name = metadata.get("name", "")
    skill_prefix = metadata.get("skill_prefix", "")
    if not name:
        errors.append("grimoire.json missing 'name' field")
    if not skill_prefix:
        errors.append("grimoire.json missing 'skill_prefix' field")
    elif not SKILL_PREFIX_RE.fullmatch(skill_prefix):
        errors.append(
            f"invalid skill_prefix '{skill_prefix}' (must match {SKILL_PREFIX_RE.pattern})"
        )

    return metadata, errors


def load_library(library_path: Path) -> dict:
    """Read a `library.json` file. Always returns a dict with a `grimoires` key.

    Missing file or unreadable JSON returns `{"grimoires": {}}` (with a warning
    logged for the unreadable case). This matches the contract every consumer
    (`sync_library`, `register_skills`, `clean_artifacts`) expects.
    """
    if not library_path.is_file():
        return {"grimoires": {}}
    try:
        with open(library_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        warn(f"could not read library {library_path}: {exc} (treating as empty)")
        return {"grimoires": {}}
    if "grimoires" not in data or not isinstance(data["grimoires"], dict):
        data["grimoires"] = {}
    return data


def resolve_local_path(raw: str) -> Path:
    """Expand the `$HOME` token used in library `local_path` entries."""
    if not raw:
        return Path()
    return Path(raw.replace("$HOME", str(Path.home())))


# ---------------------------------------------------------------------------
# Page discovery
# ---------------------------------------------------------------------------


def iter_pages(
    root: Path,
    scan_dirs: Iterable[str],
    exempt_filenames: Iterable[str] = (),
    skip_dirs: Iterable[str] = (),
    include_root_md: bool = True,
) -> Iterable[Path]:
    """Yield markdown files a validator should consider.

    Walks each `scan_dirs` subtree under `root`, skipping any path whose
    relative parts include a `skip_dirs` entry, and any file whose name is in
    `exempt_filenames`. Optionally also yields any `*.md` directly under
    `root` (the grimoire root hub plus any peer-level docs).

    Yields each path at most once, in deterministic sorted order per scan dir.
    """
    seen: set = set()
    skip_set = set(skip_dirs)
    exempt_set = set(exempt_filenames)

    for d in scan_dirs:
        sub = root / d
        if not sub.is_dir():
            continue
        for path in sorted(sub.rglob("*.md")):
            if path.name in exempt_set:
                continue
            rel_parts = path.relative_to(root).parts
            if any(part in skip_set for part in rel_parts):
                continue
            if path in seen:
                continue
            seen.add(path)
            yield path

    if include_root_md:
        for path in sorted(root.glob("*.md")):
            if path in seen or path.name in exempt_set:
                continue
            yield path


# ---------------------------------------------------------------------------
# Path skip / public-doc classification
# ---------------------------------------------------------------------------

PUBLIC_DOC_DIRS = {"docs"}
PUBLIC_DOC_FILENAMES = {"README.md", "RECOVERY.md", "CONTRIBUTING.md", "CHANGELOG.md"}


def is_skipped(rel, skip_dirs: Iterable[str]) -> bool:
    """Return True when a root-relative path falls inside a skip directory.

    `rel` may be a Path or a string. A skip entry matches as a leading path
    prefix at segment boundaries: a single-segment entry like ``sources`` skips
    ``sources/...`` but never a sibling like ``sources_extra/...``, and a
    multi-segment entry like ``invocations/arcana/validators`` skips only that
    subtree.
    """
    if isinstance(rel, Path):
        parts = rel.parts
    else:
        parts = tuple(p for p in str(rel).replace("\\", "/").split("/") if p)
    for sd in skip_dirs:
        sd_parts = tuple(p for p in str(sd).replace("\\", "/").split("/") if p)
        if sd_parts and parts[: len(sd_parts)] == sd_parts:
            return True
    return False


def public_document(path: Path, root: Path) -> bool:
    """Return True when a Markdown file is meant to render portably on Git hosts.

    Public docs - the top-level README/RECOVERY/CONTRIBUTING/CHANGELOG plus the
    ``docs/`` tree - use standard Markdown links; vault and AI-routing surfaces
    use full-path wikilinks.
    """
    if path.name in PUBLIC_DOC_FILENAMES:
        return True
    rel = path.relative_to(root)
    return bool(rel.parts and rel.parts[0] in PUBLIC_DOC_DIRS)
