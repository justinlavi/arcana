#!/usr/bin/env python3
"""Audit staged or built publishing output before it goes anywhere.

Publishing makes whatever is staged reachable, so this read-only check runs
over the staged content (`--mode content`, the default) or the generated
static site (`--mode static-output`) and reports:

- BLOCKER: authoring roots that must never be published (`.git/`,
  `.obsidian/`, `chapters/`, `inbox/`, `publish/`, `skills/`, asset folders),
  assets whose names mark identity, payment, or credential material,
  possible full payment-card numbers (Luhn-checked), credentials, private
  keys, national identity numbers, bank details, seed phrases, identity
  document scans, and frontmatter `sources:` that do not resolve in the
  staged tree; in static mode, broken asset references in the built HTML.
- WARNING: published documents and images (fine behind access control,
  worth a look), unresolved wikilinks or asset links, unlinked source asset
  paths, and any pattern the grimoire adds in `publish/publish.json`.

A grimoire extends the audit in `publish/publish.json`:

    {
      "audit": {
        "warning_patterns": {"booking-reference": "\\\\b(?:confirmation code|record locator)\\\\b"},
        "known_identifier_patterns": ["airbnb\\\\.com/rooms/{digits}\\\\b"]
      }
    }

`known_identifier_patterns` name number formats that look like card numbers
but are not; `{digits}` stands for the candidate digits.

Usage:
    python3 rites/audit_publish.py --grimoire <path> [--target <dir>] [--mode content|static-output]
        [--verbose-warnings] [--format human|json|jsonl]

Exit codes: 0 = no blockers, 1 = blockers found, 2 = target missing or
invalid arguments.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from _lib import add_grimoire_arg, resolve_grimoire_arg
from diagnostics import DiagnosticReporter, add_output_format_arg

ASSET_FOLDERS = {"templates", "snippets", "scripts", "configs", "assets", "media"}
BLOCKED_ROOTS = (".git", ".obsidian", "chapters", "inbox", "private", "publish", "skills")
ASSET_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf",
    ".heic", ".avif", ".mp4", ".mov", ".m4v", ".webm", ".eml",
}
TEXT_EXTS = {".md", ".html", ".htm", ".txt", ".json", ".js", ".css", ".xml", ".yaml", ".yml"}
BLOCKER_PATTERNS = [
    ("cvv-or-security-code", re.compile(r"\b(?:cvv|cvc|security\s+code|card\s+security\s+code)\b", re.I)),
    ("bank-account-data", re.compile(r"\b(?:bank\s+account|routing\s+number|iban|swift\s+code)\b", re.I)),
    ("national-identity-number", re.compile(r"\b(?:ssn|social\s+security\s+number|mynumber|my\s+number)\b", re.I)),
    ("api-key-or-token", re.compile(r"\b(?:api[_ -]?key|access[_ -]?token|auth[_ -]?token|secret[_ -]?key)\b", re.I)),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----", re.I)),
    ("password-or-credential", re.compile(r"\b(?:password|passphrase|recovery\s+code|backup\s+code)\b\s*[:=]", re.I)),
    ("seed-phrase", re.compile(r"\b(?:seed\s+phrase|mnemonic\s+phrase)\b", re.I)),
    ("identity-document-scan", re.compile(r"\b(?:passport|driver'?s?\s+licen[cs]e|identity\s+document|id\s+card).{0,40}\b(?:scan|photo|image|front|back)\b", re.I)),
    ("passport-number", re.compile(r"\bpassport\s+number\b", re.I)),
]
ASSET_WARNING_TYPES = {
    ".pdf": "published-document", ".png": "published-image", ".jpg": "published-image",
    ".jpeg": "published-image", ".heic": "published-image", ".eml": "email-export",
}
IDENTITY_ASSET_RE = re.compile(
    r"(passport|driver.?s.?licen[cs]e|identity.?document|id.?card|ssn|social.?security|credit.?card|password|private.?key|token|seed.?phrase)",
    re.I,
)
WIKI_RE = re.compile(r"(!?)\[\[([^\]]+)\]\]")
MD_LINK_RE = re.compile(r"(!?)\[[^\]]*\]\(([^)]+)\)")
HTML_REF_RE = re.compile(r"\b(?:href|src)=['\"]([^'\"]+)['\"]", re.I)
SOURCE_PATH_RE = re.compile(r"(?<!\]\()(?P<target>(?:\.\./)*sources/[^\s`)>,]+|chapters/[^\s`)>,]*/sources/[^\s`)>,]+)")
DETAILED_WARNINGS = {
    "unresolved-wikilink", "unresolved-asset-reference", "unlinked-source-asset-path",
    "unresolved-frontmatter-source", "broken-static-asset-reference",
}


def load_audit_config(root: Path) -> dict:
    path = root / "publish" / "publish.json"
    config = {"content_dir": "publish/content", "audit": {}}
    if path.is_file():
        config.update(json.loads(path.read_text(encoding="utf-8")))
    audit = config.get("audit") or {}
    warnings = [(name, re.compile(pattern, re.I)) for name, pattern in (audit.get("warning_patterns") or {}).items()]
    known = [str(p) for p in (audit.get("known_identifier_patterns") or [])]
    return {"content_dir": config["content_dir"], "warning_patterns": warnings, "known_identifier_patterns": known}


def is_external_url(target: str) -> bool:
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target)) or target.startswith("//")


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5:]


def iter_frontmatter_sources(text: str):
    frontmatter, _ = split_frontmatter(text)
    if not frontmatter:
        return
    in_sources = False
    indent = 0

    def scalar(value: str) -> str:
        value = value.strip()
        if value.startswith(("\"", "'")) and len(value) >= 2 and value[-1] == value[0]:
            return value[1:-1]
        return value.split(" #", 1)[0].strip()

    for line in frontmatter.splitlines():
        stripped = line.strip()
        level = len(line) - len(line.lstrip(" "))
        if in_sources:
            if stripped.startswith("- "):
                target = scalar(stripped[2:])
                if target:
                    yield target
                continue
            if stripped and level <= indent:
                in_sources = False
        match = re.match(r"^(\s*)sources:\s*(.*)$", line)
        if not match:
            continue
        indent = len(match.group(1))
        value = match.group(2).strip()
        if not value or value == "[]":
            in_sources = True
            continue
        if value.startswith("[") and value.endswith("]"):
            for _q, target in re.findall(r"([\"'])([^\"']+)\1", value):
                yield target
            continue
        target = scalar(value)
        if target:
            yield target


def resolve_staged(scan_root: Path, target: str, source: Path) -> Path | None:
    target = target.strip().replace("\\", "/")
    if not target or target.startswith("#") or is_external_url(target):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0].lstrip("/")
    candidates = [scan_root / target, source.parent / target]
    if not Path(target).suffix:
        candidates += [scan_root / f"{target}.md", source.parent / f"{target}.md"]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def resolve_static(scan_root: Path, target: str, source: Path) -> Path | None:
    target = html.unescape(target).strip().replace("\\", "/")
    if not target or target.startswith("#") or is_external_url(target):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None
    candidate = (scan_root / target.lstrip("/")) if target.startswith("/") else (source.parent / target)
    if candidate.exists():
        return candidate.resolve()
    if not candidate.suffix:
        for page in (candidate / "index.html", candidate.with_suffix(".html")):
            if page.exists():
                return page.resolve()
    return None


def luhn_ok(digits: str) -> bool:
    total = 0
    for index, char in enumerate(reversed(digits)):
        digit = int(char)
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def has_payment_card_number(text: str, known_patterns: list[str]) -> bool:
    for match in re.finditer(r"\b(?:\d[ -]*?){13,19}\b", text):
        digits = re.sub(r"\D", "", match.group(0))
        if not (13 <= len(digits) <= 19 and luhn_ok(digits)):
            continue
        start, end = max(0, match.start() - 160), min(len(text), match.end() + 160)
        context = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(text[start:end])))
        raw_context = html.unescape(text[start:end])
        if any(re.search(p.replace("{digits}", re.escape(digits)), raw_context, re.I) or re.search(p.replace("{digits}", re.escape(digits)), context, re.I) for p in known_patterns):
            continue
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit staged or built publishing output")
    add_grimoire_arg(parser)
    parser.add_argument("--target", help="Directory to audit (default: the configured content_dir)")
    parser.add_argument("--mode", choices=["content", "static-output"], default="content")
    parser.add_argument("--verbose-warnings", action="store_true", help="Print every routine warning")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"

    root = resolve_grimoire_arg(args.grimoire)
    config = load_audit_config(root)
    scan_root = Path(args.target).expanduser().resolve() if args.target else (root / config["content_dir"]).resolve()
    reporter = DiagnosticReporter("audit_publish", scan_root)
    if not scan_root.exists():
        if human:
            print(f"Audit target does not exist: {scan_root}", file=sys.stderr)
        else:
            reporter.error("PUBLISH_TARGET_MISSING", f"audit target does not exist: {scan_root}")
            reporter.emit(args.format)
        return 2

    findings: list[tuple[str, str, str, str]] = []
    stats = Counter()
    external_hosts: Counter = Counter()

    def rel_for(path: Path) -> str:
        try:
            return path.resolve().relative_to(scan_root).as_posix()
        except ValueError:
            return path.as_posix()

    def report(severity: str, path: Path, risk: str, action: str) -> None:
        rel = rel_for(path)
        findings.append((severity, rel, risk, action))
        if severity == "BLOCKER":
            reporter.error("PUBLISH_BLOCKER", f"{risk}: {action}", path=rel)
        else:
            reporter.warning("PUBLISH_WARNING", f"{risk}: {action}", path=rel)

    blocked_prefixes = tuple(f"{name}/" for name in BLOCKED_ROOTS)
    for path in sorted(p for p in scan_root.rglob("*") if p.is_file()):
        rel = rel_for(path)
        suffix = path.suffix.lower()
        if args.mode == "content":
            top = rel.split("/", 1)[0]
            if rel.startswith(blocked_prefixes) or any(part.casefold() in ASSET_FOLDERS for part in rel.split("/")[:-1]):
                report("BLOCKER", path, "authoring root staged", f"remove {top}/ from the published output")
        if suffix in ASSET_WARNING_TYPES:
            if IDENTITY_ASSET_RE.search(rel):
                report("BLOCKER", path, "identity, payment, or credential asset", "move this asset outside the publish boundary")
            else:
                report("WARNING", path, ASSET_WARNING_TYPES[suffix], "publishable only behind access control; confirm it holds no permanent secret")
        if suffix not in TEXT_EXTS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            report("BLOCKER", path, "unreadable file", "inspect file permissions before publishing")
            continue
        if has_payment_card_number(text, config["known_identifier_patterns"]):
            report("BLOCKER", path, "possible full payment card number", "remove full card numbers before publishing")
        for name, pattern in BLOCKER_PATTERNS:
            if pattern.search(text):
                report("BLOCKER", path, name, "move severe identity, payment, credential, or permanent-secret material outside the publish boundary")
        for name, pattern in config["warning_patterns"]:
            if pattern.search(text):
                report("WARNING", path, name, "private operational detail; publishable only behind access control")
        if args.mode == "static-output" and suffix in {".html", ".htm"}:
            for match in HTML_REF_RE.finditer(text):
                target = match.group(1)
                if is_external_url(target):
                    continue
                if Path(target.split("#", 1)[0].split("?", 1)[0]).suffix.lower() not in ASSET_EXTS:
                    continue
                if resolve_static(scan_root, target, path) is None:
                    report("BLOCKER", path, "broken-static-asset-reference", f"fix the published asset link: {target}")
                else:
                    stats["static_asset_links"] += 1
        if args.mode == "content" and suffix == ".md":
            _, body = split_frontmatter(text)
            for target in iter_frontmatter_sources(text):
                if is_external_url(target):
                    external_hosts[urlparse(target).netloc.lower()] += 1
                    stats["external_frontmatter_sources"] += 1
                    continue
                stats["frontmatter_sources"] += 1
                if resolve_staged(scan_root, target, path) is None:
                    report("BLOCKER", path, "unresolved-frontmatter-source", f"the cited source is not in the staged tree: {target}")
            for match in WIKI_RE.finditer(text):
                target = match.group(2).split("|", 1)[0].split("#", 1)[0].strip()
                if resolve_staged(scan_root, target, path) is None:
                    if target.startswith(("chapters/", "sources/", "inbox/")):
                        report("WARNING", path, "unresolved-wikilink", f"review whether the target should be staged or the link updated: {target}")
                    continue
                stats["internal_wikilinks"] += 1
            for match in MD_LINK_RE.finditer(text):
                target = match.group(2).strip().split()[0]
                if is_external_url(target):
                    external_hosts[urlparse(target).netloc.lower()] += 1
                    continue
                if Path(target.split("#", 1)[0].split("?", 1)[0]).suffix.lower() in ASSET_EXTS:
                    if resolve_staged(scan_root, target, path) is None:
                        report("WARNING", path, "unresolved-asset-reference", f"review whether the asset should be staged or the link updated: {target}")
                    else:
                        stats["asset_links"] += 1
            for match in SOURCE_PATH_RE.finditer(MD_LINK_RE.sub("", body)):
                target = match.group("target").rstrip(".,;:")
                if Path(target.split("#", 1)[0].split("?", 1)[0]).suffix.lower() in ASSET_EXTS:
                    report("WARNING", path, "unlinked-source-asset-path", f"turn this path into a Markdown link so the build can check it: {target}")

    counts = Counter(severity for severity, *_ in findings)
    if not human:
        reporter.emit(args.format, checked={"files": sum(1 for p in scan_root.rglob("*") if p.is_file()), "mode": args.mode, **stats})
        return 1 if counts["BLOCKER"] else 0

    print("Grimoire publish audit")
    print(f"Target: {scan_root}")
    print(f"Mode: {args.mode}")
    for key, value in sorted(stats.items()):
        print(f"{key.replace('_', ' ').capitalize()}: {value}")
    if external_hosts:
        print("External URL domains: " + ", ".join(f"{h}={c}" for h, c in sorted(external_hosts.items()) if h))
    print(f"Findings: BLOCKER={counts['BLOCKER']}, WARNING={counts['WARNING']}")
    if findings:
        print()
        for risk, count in sorted(Counter(f[2] for f in findings).items()):
            print(f"- {risk}: {count}")
        print()
        shown = [f for f in findings if f[0] == "BLOCKER" or args.verbose_warnings or f[2] in DETAILED_WARNINGS]
        for severity, rel, risk, action in shown:
            print(f"{severity}: {risk}\nFile: {rel}\nAction: {action}\n")
        suppressed = len(findings) - len(shown)
        if suppressed:
            print(f"Suppressed {suppressed} routine warning detail line(s); pass --verbose-warnings to print them.\n")
    if counts["BLOCKER"]:
        print(f"Audit failed with {counts['BLOCKER']} blocker finding(s).", file=sys.stderr)
        return 1
    print("Audit passed with warnings; keep access control in front of the site." if counts["WARNING"] else "Audit passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
