#!/usr/bin/env python3
"""Security scanning for credentials and unsafe patterns in Arcana files.

Usage: python3 rites/validate_security.py
Exit codes: 0 = success, 1 = security issues found
"""

import re
import sys
from pathlib import Path

from _lib import default_arcana_root, is_skipped, ok, warn
from diagnostics import DiagnosticReporter, add_output_format_arg

ARCANA_ROOT = default_arcana_root()

FORBIDDEN_PATTERNS = [
    (re.compile(r"""password\s*=\s*['"][^'"]+['"]""", re.IGNORECASE), "password assignment"),
    (re.compile(r"""api[_-]?key\s*=\s*['"][^'"]+['"]""", re.IGNORECASE), "API key assignment"),
    (re.compile(r"""secret\s*=\s*['"][^'"]+['"]""", re.IGNORECASE), "secret assignment"),
    (re.compile(r"""token\s*=\s*['"][^'"]+['"]""", re.IGNORECASE), "token assignment"),
    (re.compile(r"BEGIN.*PRIVATE KEY"), "private key"),
]

SKIP_DIRS = {"rites", "invocations/arc/validators", "invocations/arc/quality", "sources"}


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Security scanning for Arcana files")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_security", ARCANA_ROOT)

    if human:
        print()
        print("Validating Arcana Security")
        print("==================================")
        print(f"Arcana root: {ARCANA_ROOT}")
        print()

    # Scan for forbidden patterns
    if human:
        print("Scanning for potential credentials...")
    cred_found = 0

    for path in sorted(ARCANA_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in (".md", ".py"):
            continue

        rel = str(path.relative_to(ARCANA_ROOT)).replace("\\", "/")
        if is_skipped(rel, SKIP_DIRS):
            continue

        try:
            content = path.read_text(errors="replace")
        except OSError:
            continue

        for pattern, label in FORBIDDEN_PATTERNS:
            for match in pattern.finditer(content):
                reporter.error(
                    "SECURITY_CREDENTIAL_PATTERN",
                    f"found potential {label}",
                    path=rel,
                    hint=f"Match: {match.group()[:80]}",
                )
                if human:
                    print()
                    print(f"  CRED   Found potential {label}: {rel}")
                    print(f"         Match: {match.group()[:80]}")
                cred_found += 1

    if human and cred_found == 0:
        ok("No potential credentials found")
    if human:
        print()

    # Check Python scripts for unsafe patterns
    if human:
        print("Checking for unsafe script patterns...")
    unsafe = 0

    rites_dir = ARCANA_ROOT / "rites"
    if rites_dir.is_dir():
        for path in sorted(rites_dir.glob("*.py")):
            if path.name == "validate_security.py":
                continue

            content = path.read_text(errors="replace")

            if "eval(" in content:
                reporter.error(
                    "SECURITY_EVAL",
                    "script uses eval()",
                    path=path,
                    hint="Use explicit parsing or dispatch instead.",
                )
                if human:
                    warn(f"Script uses eval() (security risk): {path.relative_to(ARCANA_ROOT)}")
                unsafe += 1

            if "exec(" in content:
                reporter.error(
                    "SECURITY_EXEC",
                    "script uses exec()",
                    path=path,
                    hint="Use explicit APIs instead.",
                )
                if human:
                    warn(f"Script uses exec() (security risk): {path.relative_to(ARCANA_ROOT)}")
                unsafe += 1

    if human and unsafe == 0:
        ok("No unsafe script patterns found")
    if human:
        print()

    if not human:
        reporter.emit(args.format, checked={"credential_hits": cred_found, "unsafe_hits": unsafe})
        return reporter.exit_code()

    print("==================================")
    if reporter.error_count() == 0:
        print("Security validation passed")
        return 0
    else:
        print(f"Security validation failed with {reporter.error_count()} issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
