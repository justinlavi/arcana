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
  5. `type: source` is reserved for source wrappers under `sources/`.
  6. `sources:` paths under `sources/` resolve on disk; URLs are not network-checked.
  7. `last_verified:` parses as YYYY-MM-DD and is not an implausibly early
     sentinel (a date before a fixed static floor; never compared to "today").
  8. `tags:` and `aliases:` are YAML lists of plain strings.

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
)
from diagnostics import DiagnosticReporter, add_output_format_arg

# Folders whose .md files require schema-compliant frontmatter.
SCAN_DIRS = ["docs", "invocations", "formulae", "chapters"]

EXEMPT_FILENAMES = {
    "SKILL.md",
    "README.md",
    "RECOVERY.md",
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

# Static floor for `last_verified`. A well-formed date earlier than this is an
# implausible sentinel (e.g. the Unix epoch `1970-01-01`) that would otherwise
# pass as a valid ISO date and report a page as verified when it never was. The
# floor is a fixed constant, never the current date: comparing against "today"
# would make validation depend on wall-clock time and break reproducibility.
# No grimoire can predate Arcana, so 2020-01-01 clears every real date.
EARLIEST_PLAUSIBLE_VERIFIED = datetime.date(2020, 1, 1)


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


def check_file(path, grimoire_root, reporter):
    """Add frontmatter diagnostics for a single file."""
    rel = path.relative_to(grimoire_root).as_posix()

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        reporter.error("FRONTMATTER_READ_ERROR", f"could not read ({exc})", path=rel)
        return

    if not FRONTMATTER_RE.match(content):
        reporter.error(
            "FRONTMATTER_MISSING",
            "missing or malformed YAML frontmatter (must start with `---`)",
            path=rel,
            docs_reference="docs/page_schema.md",
        )
        return

    fields = parse_frontmatter(content)
    type_ = fields.get("type", "")

    if not type_:
        reporter.error(
            "FRONTMATTER_MISSING_TYPE",
            "missing `type:` in frontmatter",
            path=rel,
            docs_reference="docs/page_schema.md",
        )
        return

    if type_ not in VALID_TYPES:
        reporter.error(
            "FRONTMATTER_INVALID_TYPE",
            f"invalid type '{type_}'",
            path=rel,
            hint=f"Must be one of {sorted(VALID_TYPES)}.",
            docs_reference="docs/page_schema.md",
        )
        return

    template = is_template(rel)
    if type_ == "source" and not template and not rel.startswith("sources/"):
        reporter.error(
            "FRONTMATTER_SOURCE_OUTSIDE_SOURCES",
            "`type: source` is reserved for source wrappers under sources/",
            path=rel,
            hint="Use concept/entity/playbook/reference for authored chapter synthesis.",
            docs_reference="docs/page_schema.md",
        )
    required, _optional = required_fields_for(type_)

    for field in required:
        if field not in fields or fields[field] in ("", [], None):
            # Templates carry placeholder frontmatter so users see the shape;
            # only `type` is enforced for templates (already validated above).
            if template:
                continue
            reporter.error(
                "FRONTMATTER_MISSING_REQUIRED",
                f"missing required field `{field}` for type='{type_}'",
                path=rel,
                docs_reference="docs/page_schema.md",
            )

    if "authority" in fields and fields["authority"]:
        if fields["authority"] not in VALID_AUTHORITIES:
            reporter.error(
                "FRONTMATTER_INVALID_AUTHORITY",
                f"invalid authority '{fields['authority']}'",
                path=rel,
                hint=f"Must be one of {sorted(VALID_AUTHORITIES)}.",
                docs_reference="docs/page_schema.md",
            )
        else:
            authority = fields["authority"]
            if authority in ("external", "hybrid"):
                src = fields.get("sources") or []
                if not src and not template:
                    reporter.error(
                        "FRONTMATTER_MISSING_SOURCES",
                        f"authority='{authority}' requires non-empty `sources:`",
                        path=rel,
                        docs_reference="docs/page_schema.md",
                    )

    if "sources" in fields and isinstance(fields["sources"], list):
        for src in fields["sources"]:
            if isinstance(src, str) and src.startswith("sources/"):
                src_path = grimoire_root / src
                if not src_path.exists() and not template:
                    reporter.error(
                        "FRONTMATTER_SOURCE_MISSING",
                        f"sources entry '{src}' does not resolve under sources/",
                        path=rel,
                        hint="Create the source artifact or update the source pointer.",
                        docs_reference="docs/page_schema.md",
                    )

    if "last_verified" in fields and fields["last_verified"]:
        v = fields["last_verified"]
        if isinstance(v, str) and not template:
            if not DATE_RE.match(v):
                reporter.error(
                    "FRONTMATTER_INVALID_DATE_FORMAT",
                    f"last_verified '{v}' must be YYYY-MM-DD",
                    path=rel,
                    docs_reference="docs/page_schema.md",
                )
            else:
                try:
                    parsed = datetime.date.fromisoformat(v)
                except ValueError:
                    reporter.error(
                        "FRONTMATTER_INVALID_DATE",
                        f"last_verified '{v}' is not a valid date",
                        path=rel,
                        docs_reference="docs/page_schema.md",
                    )
                else:
                    if parsed < EARLIEST_PLAUSIBLE_VERIFIED:
                        reporter.error(
                            "FRONTMATTER_IMPLAUSIBLE_DATE",
                            f"last_verified '{v}' predates {EARLIEST_PLAUSIBLE_VERIFIED.isoformat()}"
                            " and is an implausible sentinel",
                            path=rel,
                            hint="Set last_verified to the date the page was"
                            " actually hand-verified or auto-checked.",
                            docs_reference="docs/page_schema.md",
                        )

    for field in ("tags", "aliases"):
        if field in fields and not isinstance(fields[field], list):
            reporter.error(
                "FRONTMATTER_LIST_REQUIRED",
                f"`{field}:` must be a YAML list",
                path=rel,
                docs_reference="docs/page_schema.md",
            )


def main():
    parser = argparse.ArgumentParser(description="Validate page frontmatter")
    add_grimoire_arg(parser)
    add_output_format_arg(parser)
    args = parser.parse_args()
    grimoire_root = resolve_grimoire_arg(args.grimoire)
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_frontmatter", grimoire_root)

    if human:
        print()
        print("Validating Page Frontmatter")
        print("==================================")
        print(f"Grimoire root: {grimoire_root}")
        print()

    files_checked = 0

    for path in iter_pages(grimoire_root, SCAN_DIRS, exempt_filenames=EXEMPT_FILENAMES):
        files_checked += 1
        before = len(reporter.diagnostics)
        check_file(path, grimoire_root, reporter)
        if human:
            for diagnostic in reporter.diagnostics[before:]:
                print(f"  [ERROR] {diagnostic.path}: {diagnostic.message}")

    checked = {"files": files_checked}
    if not human:
        reporter.emit(args.format, checked=checked)
        return reporter.exit_code()

    print()
    print(f"Files checked:    {files_checked}")
    print(f"Violations found: {reporter.error_count()}")
    print()

    if reporter.error_count() == 0:
        print("Frontmatter validation passed")
        return 0
    print("Frontmatter validation failed")
    print("   See docs/page_schema.md for the canonical specification.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
