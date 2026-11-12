#!/usr/bin/env python3
"""Stage a grimoire's publishable content for a static-site generator.

The authoring layout (`chapters/`, `inbox/`, `skills/`, `publish/`, editor
dotfiles) is not the layout readers should see. This rite copies just the
publishable content into a content directory the generator reads:

- the root hub becomes `index.md`;
- every top-level folder under `chapters/` lands at the content root
  (readers see `travel/`, not `chapters/travel/`), with chapter-local
  `sources/` folders carried along;
- asset folders (`templates/`, `snippets/`, `scripts/`, `configs/`,
  `assets/`, `media/`) and anything listed under `exclude` in
  `publish/publish.json` are left out; `.gitkeep` files are dropped;
- wikilinks, Markdown asset links, and frontmatter `sources:` paths are
  rewritten so they resolve against the flattened tree, and aliases equal to
  a page's own slug are removed (they would make a generator emit redirect
  loops).

Configuration (all optional) lives in `<grimoire>/publish/publish.json`:

    {
      "generator": "quartz",
      "content_dir": "publish/content",
      "exclude": ["chapters/travel/templates"],
      "include_asset_folders": false
    }

Mutation profile: plan_apply. Without `--apply` the rite lists what it would
stage and writes nothing; with `--apply` it empties the content directory
(which must sit under `publish/`) and writes the staged copy.

Usage:
    python3 rites/stage_publish.py --grimoire <path> [--apply] [--format human|json|jsonl]

Exit codes: 0 = planned or staged, 1 = refused (no root hub, no chapters,
content directory outside publish/), 2 = argparse invalid arguments.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from _lib import add_grimoire_arg, info, ok, resolve_grimoire_arg, warn
from diagnostics import ResultReporter, add_output_format_arg

ASSET_FOLDERS = {"templates", "snippets", "scripts", "configs", "assets", "media"}
ASSET_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf",
    ".heic", ".avif", ".mp4", ".mov", ".m4v", ".webm", ".eml",
}
WIKI_RE = re.compile(r"(!?)\[\[([^\]]+)\]\]")
MD_LINK_RE = re.compile(r"(!?\[[^\]]*\]\()([^)]+)(\))")
DEFAULT_CONFIG = {
    "generator": "quartz",
    "content_dir": "publish/content",
    "exclude": [],
    "include_asset_folders": False,
}


def load_config(root: Path) -> dict:
    config = dict(DEFAULT_CONFIG)
    path = root / "publish" / "publish.json"
    if path.is_file():
        try:
            config.update(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as exc:
            raise ValueError(f"publish/publish.json is not valid JSON: {exc}") from exc
    return config


def is_external_url(target: str) -> bool:
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target)) or target.startswith("//")


def split_target(target: str) -> tuple[str, str, str]:
    query = anchor = ""
    if "#" in target:
        target, anchor = target.split("#", 1)
        anchor = "#" + anchor
    if "?" in target:
        target, query = target.split("?", 1)
        query = "?" + query
    return target, query, anchor


class Rewriter:
    """Rewrites authoring paths into published paths for one grimoire."""

    def __init__(self, root: Path, content_dir: Path) -> None:
        self.root_stem = root.name
        self.root_targets = {self.root_stem, f"{self.root_stem}.md"}
        self.content_dir = content_dir.resolve()

    def target(self, target: str) -> str:
        body, query, anchor = split_target(target)
        if body in self.root_targets:
            return "index" + query + anchor
        if body.startswith("chapters/"):
            return body[len("chapters/"):] + query + anchor
        return body + query + anchor

    def wikilinks(self, text: str) -> str:
        def rewrite(match: re.Match) -> str:
            embed, body = match.groups()
            if "|" in body:
                target, label = body.split("|", 1)
                return f"{embed}[[{self.target(target)}|{label}]]"
            return f"{embed}[[{self.target(body)}]]"
        return WIKI_RE.sub(rewrite, text)

    def frontmatter(self, path: Path, text: str) -> str:
        if not text.startswith("---\n"):
            return text
        end = text.find("\n---\n", 4)
        if end == -1:
            return text
        lines = text[4:end].splitlines()
        body = text[end:]
        stem = "index" if path.name == "index.md" else path.stem
        own = stem.replace("_", "-").lower()
        out = []
        in_sources = False
        indent = 0
        for line in lines:
            stripped = line.strip()
            level = len(line) - len(line.lstrip(" "))
            match = re.match(r"^(\s*)aliases:\s*\[(.*)\]\s*$", line)
            if match:
                kept = [a.strip() for a in match.group(2).split(",") if a.strip() and a.strip().strip("\"'").replace("_", "-").lower() != own]
                out.append(f"{match.group(1)}aliases: [{', '.join(kept)}]")
                continue
            if in_sources:
                if stripped.startswith("- "):
                    marker = line.find("- ")
                    out.append(line[: marker + 2] + self._scalar(line[marker + 2:]))
                    continue
                if stripped and level <= indent:
                    in_sources = False
            match = re.match(r"^(\s*)sources:\s*(.*)$", line)
            if match:
                indent = len(match.group(1))
                value = match.group(2)
                if value.startswith("["):
                    rewritten = re.sub(
                        r"([\"'])([^\"']+)\1",
                        lambda m: m.group(0) if is_external_url(m.group(2)) else f"{m.group(1)}{self.target(m.group(2))}{m.group(1)}",
                        value,
                    )
                    out.append(f"{match.group(1)}sources: {rewritten}")
                else:
                    in_sources = True
                    out.append(line)
                continue
            out.append(line)
        return "---\n" + "\n".join(out) + body

    def _scalar(self, value: str) -> str:
        inner = value.strip()
        if not inner:
            return value
        comment = ""
        if not inner.startswith(("\"", "'")) and " #" in inner:
            inner, comment = inner.split(" #", 1)
            comment = " #" + comment
        quote = ""
        raw = inner
        if len(inner) >= 2 and inner[0] in "\"'" and inner[-1] == inner[0]:
            quote, raw = inner[0], inner[1:-1]
        rewritten = raw if (not raw or is_external_url(raw)) else self.target(raw)
        return f"{quote}{rewritten}{quote}{comment}"

    def asset_links(self, path: Path, text: str) -> str:
        def rewrite(match: re.Match) -> str:
            prefix, inner, suffix = match.groups()
            raw = inner.strip()
            angle = raw.startswith("<") and ">" in raw
            if angle:
                target, rest = raw[1:].split(">", 1)
            else:
                parts = raw.split(maxsplit=1)
                target, rest = parts[0], (" " + parts[1] if len(parts) > 1 else "")
            if not target or target.startswith("#") or is_external_url(target):
                return match.group(0)
            body, query, anchor = split_target(target.replace("\\", "/"))
            if not body or Path(body).suffix.lower() not in ASSET_EXTS:
                return match.group(0)
            resolved = (self.content_dir / body.lstrip("/")) if body.startswith("/") else (path.parent / body)
            try:
                resolved = resolved.resolve()
                rel = resolved.relative_to(self.content_dir)
            except (OSError, ValueError):
                return match.group(0)
            if not resolved.exists():
                return match.group(0)
            published = "/" + rel.as_posix() + query + anchor
            return f"{prefix}<{published}>{rest}{suffix}" if angle else f"{prefix}{published}{rest}{suffix}"
        return MD_LINK_RE.sub(rewrite, text)


def excluded(rel_parts: tuple[str, ...], config: dict) -> bool:
    """True when a path under chapters/ is left out of the staged copy."""
    rel = "/".join(rel_parts)
    for item in config.get("exclude", []):
        item = str(item).replace("\\", "/").strip("/")
        if rel == item or rel.startswith(item + "/"):
            return True
    if not config.get("include_asset_folders"):
        if any(part.casefold() in ASSET_FOLDERS for part in rel_parts[:-1]) or (
            len(rel_parts) and rel_parts[-1].casefold() in ASSET_FOLDERS
        ):
            return True
    return rel_parts[-1] == ".gitkeep"


def plan_files(root: Path, config: dict) -> list[tuple[Path, Path]]:
    """(source, destination relative to content dir) for every file to stage."""
    chapters = root / "chapters"
    pairs = [(root / f"{root.name}.md", Path("index.md"))]
    for path in sorted(chapters.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).parts  # ('chapters', ...)
        if excluded(rel, config):
            continue
        pairs.append((path, Path(*rel[1:])))
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage a grimoire's publishable content")
    add_grimoire_arg(parser)
    parser.add_argument("--apply", action="store_true", help="Write the staged copy (default: plan only)")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"

    root = resolve_grimoire_arg(args.grimoire)
    mode = "apply" if args.apply else "plan"
    reporter = ResultReporter("stage_publish", root=root, mode=mode)
    summary: dict = {"files": 0, "content_dir": "", "generator": ""}

    def finish(code: int) -> int:
        if not human:
            reporter.emit(args.format, summary=summary)
        return code

    def refuse(text: str) -> int:
        reporter.message("error", text)
        reporter.set_status("blocked")
        if human:
            warn(text)
        return finish(1)

    try:
        config = load_config(root)
    except ValueError as exc:
        return refuse(str(exc))
    content_dir = (root / str(config["content_dir"])).resolve()
    summary["content_dir"] = str(content_dir)
    summary["generator"] = str(config.get("generator", "quartz"))
    try:
        content_dir.relative_to((root / "publish").resolve())
    except ValueError:
        return refuse(f"content_dir must sit under publish/: {config['content_dir']}")
    if not (root / f"{root.name}.md").is_file():
        return refuse(f"root hub not found: {root.name}.md")
    if not (root / "chapters").is_dir():
        return refuse("chapters/ not found")

    pairs = plan_files(root, config)
    summary["files"] = len(pairs)
    if human:
        print()
        print(f"Stage {root.name} for {summary['generator']} ({mode})")
        info(f"{len(pairs)} file(s) -> {content_dir}")
        if config.get("exclude"):
            info("excluded: " + ", ".join(str(e) for e in config["exclude"]))

    if not args.apply:
        reporter.set_status("noop")
        if human:
            ok("Plan only. Re-run with --apply to stage.")
        return finish(0)

    if content_dir.exists():
        shutil.rmtree(content_dir)
    content_dir.mkdir(parents=True, exist_ok=True)
    for source, rel in pairs:
        destination = content_dir / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    rewriter = Rewriter(root, content_dir)
    for page in sorted(content_dir.rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        text = rewriter.frontmatter(page, text)
        text = rewriter.wikilinks(text)
        text = rewriter.asset_links(page, text)
        page.write_bytes(text.encode("utf-8"))

    reporter.mutation("stage", path=content_dir, detail=f"{len(pairs)} file(s)")
    if human:
        ok(f"Staged {len(pairs)} file(s) into {content_dir}")
    return finish(0)


if __name__ == "__main__":
    sys.exit(main())
