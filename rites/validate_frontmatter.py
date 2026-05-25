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

SKILL.md files are exempt - they use a different agent-defined schema.

Usage: python3 rites/validate_frontmatter.py
Exit codes: 0 = no violations, 1 = violations found
"""

import argparse
import datetime
import sys
from pathlib import Path

from _lib import (
    DATE_RE,
    FRONTMATTER_RE,
    add_grimoire_arg,
    iter_pages,
    parse_frontmatter,
    resolve_grimoire_arg,
    warn,
)

# Folders whose .md files require schema-compliant frontmatter.
SCAN_DIRS = ["docs", "invocations", "formulae", "chapters"]

EXEMPT_FILENAMES = {
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
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


def check_file(path, grimoire_root):
    """Return list of violation strings for a single file."""
    rel = str(path.relative_to(grimoire_root))
    violations = []

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"{rel}: could not read ({exc})"]

    if not FRONTMATTER_RE.match(content):
        return [f"{rel}: missing or malformed YAML frontmatter (must start with `---`)"]

    fields = parse_frontmatter(content)
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
    add_grimoire_arg(parser)
    args = parser.parse_args()
    grimoire_root = resolve_grimoire_arg(args.grimoire)

    print()
    print("Validating Page Frontmatter")
    print("==================================")
    print(f"Grimoire root: {grimoire_root}")
    print()

    total_violations = 0
    files_checked = 0

    for path in iter_pages(grimoire_root, SCAN_DIRS, exempt_filenames=EXEMPT_FILENAMES):
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
