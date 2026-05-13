#!/usr/bin/env python3
"""Validates page frontmatter against the canonical schema.

Schema: docs/page_schema.md

Walks every authored markdown file in the grimoire (Arcana or domain) and
checks:

  1. YAML frontmatter is present, delimited by `---` on the first line and a
     closing `---`.
  2. `type:` is present and one of the seven canonical values.
  3. The required-fields matrix in docs/page_schema.md holds for the type.
  4. `authority:` (when present) is one of `external | grimoire | hybrid`.
  5. `sources:` paths under `sources/` resolve on disk; URLs are not network-checked.
  6. `last_verified:` parses as YYYY-MM-DD.
  7. `tags:` and `aliases:` are YAML lists of plain strings.

SKILL.md files are exempt — they use a different agent-defined schema.

Usage: python3 rites/validate_frontmatter.py
Exit codes: 0 = no violations, 1 = violations found
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

# Folders whose .md files require schema-compliant frontmatter.
SCAN_DIRS = ["docs", "invocations", "formulae", "chapters"]
# Plus any .md at the grimoire root (arcana.md, the equivalent root hub for a
# domain grimoire, README.md is exempt).
ROOT_REQUIRED_GLOBS = ["arcana.md"]

EXEMPT_FILENAMES = {
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    "VERSION",
    "log.md",
    "CLAUDE.md",
    "AGENTS.md",
    "LICENSE.md",
}

# Files inside formulae/ are templates with placeholder frontmatter; we still
# validate type but skip strict required-field checks because placeholders like
# `YYYY-MM-DD` would otherwise fail.
FORMULA_TEMPLATE_DIRS = {"formulae"}

VALID_TYPES = {"hub", "concept", "entity", "source", "playbook", "reference", "log-entry"}
VALID_AUTHORITIES = {"external", "grimoire", "hybrid"}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def info(msg):
    print(f"  [INFO]  {msg}")


def warn(msg):
    print(f"  [WARN]  {msg}")


def err(msg):
    print(f"  [ERROR] {msg}")


def parse_simple_yaml(block):
    """Minimal YAML parser — handles the subset used by page frontmatter.

    Supports:
      key: value
      key: "quoted value"
      key: [a, b, "c"]
      key:
        - item
        - item

    Returns dict[str, str|list[str]]. Lines that don't match are ignored.
    """
    fields = {}
    current_list_key = None
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            current_list_key = None
            continue

        # Multi-line list continuation (- item).
        if current_list_key is not None and re.match(r"^\s+-\s+", raw_line):
            value = raw_line.split("-", 1)[1].strip().strip("'\"")
            fields[current_list_key].append(value)
            continue
        else:
            current_list_key = None

        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if not value:
            # Could be a multi-line list following.
            fields[key] = []
            current_list_key = key
            continue

        # Inline list: [a, b, "c"]
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                fields[key] = []
            else:
                items = []
                for piece in re.split(r",\s*", inner):
                    items.append(piece.strip().strip("'\""))
                fields[key] = items
            continue

        fields[key] = value.strip("'\"")
    return fields


def required_fields_for(type_):
    """Return (required_set, optional_set) for a type."""
    if type_ == "hub":
        return {"type", "title", "tags"}, {"aliases"}
    if type_ == "log-entry":
        return {"type", "title"}, set()
    # All other types share the same baseline.
    return (
        {"type", "title", "tags", "authority", "last_verified"},
        {"aliases", "sources"},
    )


def is_template(rel_path):
    return any(rel_path.startswith(d + "/") or rel_path == d for d in FORMULA_TEMPLATE_DIRS)


def scan_files(grimoire_root):
    """Yield Path objects for every file we need to validate."""
    seen = set()
    for d in SCAN_DIRS:
        root = grimoire_root / d
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.md")):
            if path.name in EXEMPT_FILENAMES:
                continue
            seen.add(path)
            yield path
    # The grimoire root hub is the file named after the grimoire directory.
    root_hub = grimoire_root / f"{grimoire_root.name}.md"
    if root_hub.is_file() and root_hub not in seen:
        seen.add(root_hub)
        yield root_hub
    # Plus any other root-level .md that fits the schema and isn't exempt.
    for path in sorted(grimoire_root.glob("*.md")):
        if path in seen or path.name in EXEMPT_FILENAMES:
            continue
        yield path


def check_file(path, grimoire_root):
    """Return list of violation strings for a single file."""
    rel = str(path.relative_to(grimoire_root))
    violations = []

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"{rel}: could not read ({exc})"]

    match = FRONTMATTER_RE.match(content)
    if not match:
        return [f"{rel}: missing or malformed YAML frontmatter (must start with `---`)"]

    fields = parse_simple_yaml(match.group(1))
    type_ = fields.get("type", "")

    if not type_:
        violations.append(f"{rel}: missing `type:` in frontmatter")
        return violations

    if type_ not in VALID_TYPES:
        violations.append(
            f"{rel}: invalid type '{type_}' (must be one of {sorted(VALID_TYPES)})"
        )
        return violations

    template = is_template(rel)
    required, _optional = required_fields_for(type_)

    for field in required:
        if field not in fields or fields[field] in ("", [], None):
            # Templates carry placeholder frontmatter so users see the shape;
            # only `type` is enforced for templates (already validated above).
            if template:
                continue
            violations.append(f"{rel}: missing required field `{field}` for type='{type_}'")

    if "authority" in fields and fields["authority"]:
        if fields["authority"] not in VALID_AUTHORITIES:
            violations.append(
                f"{rel}: invalid authority '{fields['authority']}' "
                f"(must be one of {sorted(VALID_AUTHORITIES)})"
            )
        else:
            authority = fields["authority"]
            if authority in ("external", "hybrid"):
                src = fields.get("sources") or []
                if not src and not template:
                    violations.append(
                        f"{rel}: authority='{authority}' requires non-empty `sources:`"
                    )

    if "sources" in fields and isinstance(fields["sources"], list):
        for src in fields["sources"]:
            if isinstance(src, str) and src.startswith("sources/"):
                src_path = grimoire_root / src
                if not src_path.exists() and not template:
                    violations.append(
                        f"{rel}: sources entry '{src}' does not resolve under sources/"
                    )

    if "last_verified" in fields and fields["last_verified"]:
        v = fields["last_verified"]
        if isinstance(v, str) and not template:
            if not DATE_RE.match(v):
                violations.append(f"{rel}: last_verified '{v}' must be YYYY-MM-DD")
            else:
                try:
                    datetime.date.fromisoformat(v)
                except ValueError:
                    violations.append(f"{rel}: last_verified '{v}' is not a valid date")

    for field in ("tags", "aliases"):
        if field in fields and not isinstance(fields[field], list):
            violations.append(f"{rel}: `{field}:` must be a YAML list")

    return violations


def main():
    parser = argparse.ArgumentParser(description="Validate page frontmatter")
    parser.add_argument(
        "--grimoire", type=Path,
        default=Path(os.environ.get("GRIMOIRE_ARCANA", Path(__file__).resolve().parent.parent)),
        help="Grimoire root (default: GRIMOIRE_ARCANA env var or rites parent)",
    )
    args = parser.parse_args()
    grimoire_root = args.grimoire.expanduser().resolve()

    print()
    print("Validating Page Frontmatter")
    print("==================================")
    print(f"Grimoire root: {grimoire_root}")
    print()

    total_violations = 0
    files_checked = 0

    for path in scan_files(grimoire_root):
        files_checked += 1
        violations = check_file(path, grimoire_root)
        for v in violations:
            warn(v)
            total_violations += 1

    print()
    print(f"Files checked:    {files_checked}")
    print(f"Violations found: {total_violations}")
    print()

    if total_violations == 0:
        print("Frontmatter validation passed")
        return 0
    print("Frontmatter validation failed")
    print("   See docs/page_schema.md for the canonical specification.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
