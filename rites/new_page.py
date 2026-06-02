#!/usr/bin/env python3
"""Stamp a new grimoire page from the page formula with validated frontmatter.

Renders `formulae/page.formula.md` into a target page under a grimoire's
`chapters/` tree, filling the frontmatter an author would otherwise hand-type:
`type`, `title`, `tags`, `authority`, `sources`, and `last_verified` (stamped
with today's date). The page body structure comes from the formula, which stays
the single source of page shape; this rite stamps the fields and the title.

Stamping `last_verified` with a real date is the mechanical half of page
authoring (the script-vs-AI split): the agent decides the path, type, title, and
tags; the rite guarantees schema-valid, sentinel-free frontmatter so a page
never ships with the formula's placeholder date.

Defaults to a dry-run that prints the rendered page; pass --apply to write it.
Refuses to overwrite an existing file.

Usage:
    python3 rites/new_page.py --grimoire <path> \
        --path chapters/<chapter>/<slug>.md \
        --type concept --title "<title>" \
        [--tags a,b] [--authority grimoire] [--sources s1,s2] [--apply]

Exit codes: 0 = preview shown or page written; 1 = invalid arguments or refusal.
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

from _lib import add_grimoire_arg, resolve_grimoire_arg
from diagnostics import ResultReporter, add_output_format_arg

ARCANA_PATH = Path(__file__).resolve().parent.parent
PAGE_FORMULA = ARCANA_PATH / "formulae" / "page.formula.md"

PAGE_TYPES = {"concept", "entity", "playbook", "reference"}
VALID_AUTHORITIES = {"external", "grimoire", "hybrid"}

# Frontmatter keys this rite stamps; every other formula key passes through.
STAMPED_KEYS = {"type", "title", "tags", "sources", "authority", "last_verified"}


def split_csv(value):
    """Split a comma-separated option into a list of trimmed, non-empty items."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def default_tags(path_parts, type_, extra):
    """Build schema-aligned tags: chapter facet, type facet, then extras (deduped)."""
    tags = []
    if len(path_parts) >= 3 and path_parts[0] == "chapters":
        tags.append(f"chapter/{path_parts[1]}")
    tags.append(f"type/{type_}")
    tags.extend(extra)
    seen = set()
    ordered = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            ordered.append(tag)
    return ordered


def strip_leading_comment(body):
    """Drop the formula's leading authoring-guidance HTML comment, if present."""
    stripped = body.lstrip("\n")
    if stripped.startswith("<!--"):
        close = stripped.find("-->")
        if close != -1:
            stripped = stripped[close + len("-->"):]
    return "\n" + stripped.lstrip("\n")


def render_yaml_list(items):
    """Render a YAML inline list of double-quoted strings."""
    return "[" + ", ".join(f'"{item}"' for item in items) + "]"


def render_page(template_text, *, type_, title, tags, authority, sources, today):
    """Render the formula into a page, stamping frontmatter and the title."""
    if not template_text.startswith("---\n"):
        raise ValueError("page formula is missing opening frontmatter")
    close = template_text.find("\n---", 4)
    if close == -1:
        raise ValueError("page formula is missing closing frontmatter")
    frontmatter = template_text[4:close]
    body = template_text[close + len("\n---"):]

    overrides = {
        "type": type_,
        "title": f'"{title}"',
        "tags": "[" + ", ".join(tags) + "]",
        "sources": render_yaml_list(sources),
        "authority": authority,
        "last_verified": today,
    }

    new_lines = []
    for line in frontmatter.splitlines():
        key = line.split(":", 1)[0].strip() if ":" in line else None
        if key in overrides:
            new_lines.append(f"{key}: {overrides[key]}")
        else:
            new_lines.append(line)

    body = strip_leading_comment(body).replace("[Title]", title)
    return "---\n" + "\n".join(new_lines) + "\n---\n" + body


def resolve_target(grimoire_root, rel_path):
    """Resolve and validate a target page path under the grimoire's chapters/.

    Returns (target_abs, error_message). error_message is None on success.
    """
    candidate = Path(rel_path)
    if candidate.is_absolute():
        return None, f"--path must be relative to the grimoire root, not '{rel_path}'"
    target = (grimoire_root / candidate).resolve()
    try:
        rel = target.relative_to(grimoire_root)
    except ValueError:
        return None, f"--path '{rel_path}' escapes the grimoire root"
    if rel.parts[:1] != ("chapters",):
        return None, "--path must live under chapters/ (pages live in the chapters layer)"
    if target.suffix != ".md":
        return None, f"--path must end in .md, got '{rel_path}'"
    return target, None


def main():
    parser = argparse.ArgumentParser(
        description="Stamp a new grimoire page from the page formula"
    )
    add_grimoire_arg(parser)
    parser.add_argument("--path", required=True,
                        help="Target page path relative to the grimoire root, e.g. chapters/<chapter>/<slug>.md")
    parser.add_argument("--type", required=True, dest="type_",
                        help=f"Page type (one of: {sorted(PAGE_TYPES)})")
    parser.add_argument("--title", required=True, help="Human-readable page title")
    parser.add_argument("--tags", default="", help="Extra tags, comma-separated")
    parser.add_argument("--authority", default="grimoire",
                        help=f"Authority model (one of: {sorted(VALID_AUTHORITIES)})")
    parser.add_argument("--sources", default="",
                        help="Source paths/URLs, comma-separated (required for external/hybrid)")
    parser.add_argument("--apply", action="store_true",
                        help="Write the page (default: dry-run, print only)")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"

    grimoire_root = resolve_grimoire_arg(args.grimoire)
    reporter = ResultReporter("new_page", root=grimoire_root,
                              mode="apply" if args.apply else "plan")

    def fail(message):
        reporter.message("error", message)
        if human:
            print(f"  [ERROR] {message}", file=sys.stderr)
        else:
            reporter.emit(args.format)
        return 1

    if args.type_ not in PAGE_TYPES:
        return fail(f"invalid type '{args.type_}' (must be one of {sorted(PAGE_TYPES)})")
    if args.authority not in VALID_AUTHORITIES:
        return fail(f"invalid authority '{args.authority}' (must be one of {sorted(VALID_AUTHORITIES)})")

    sources = split_csv(args.sources)
    if args.authority in ("external", "hybrid") and not sources:
        return fail(f"authority '{args.authority}' requires at least one --sources entry")

    target, error = resolve_target(grimoire_root, args.path)
    if error:
        return fail(error)
    if target.exists():
        return fail(f"refusing to overwrite existing file: {target.relative_to(grimoire_root)}")

    rel = target.relative_to(grimoire_root)
    tags = default_tags(rel.parts, args.type_, split_csv(args.tags))
    today = datetime.date.today().isoformat()

    try:
        template_text = PAGE_FORMULA.read_text(encoding="utf-8")
        content = render_page(
            template_text,
            type_=args.type_,
            title=args.title,
            tags=tags,
            authority=args.authority,
            sources=sources,
            today=today,
        )
    except (OSError, ValueError) as exc:
        return fail(f"could not render page from formula: {exc}")

    if not args.apply:
        if human:
            print()
            print(f"Would create: {rel}")
            print("----------------------------------")
            print(content, end="" if content.endswith("\n") else "\n")
            print("----------------------------------")
            print("  Dry-run. Re-run with --apply to write the page.")
            print()
        else:
            reporter.emit(args.format, summary={"target": rel.as_posix(), "would_create": True})
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    reporter.mutation("create", path=target, detail=f"{args.type_} | {args.title}")
    if human:
        print(f"  [OK]    Created {rel}")
    else:
        reporter.emit(args.format, summary={"target": rel.as_posix()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
