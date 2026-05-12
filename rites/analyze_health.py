#!/usr/bin/env python3
"""Analyze Arcana health and suggest improvements.

Usage: python3 rites/analyze_health.py
Exit codes: 0 = healthy, 1 = issues found
"""

import os
import re
import subprocess
import sys
from pathlib import Path

ARCANA_ROOT = Path(os.environ.get("GRIMOIRE_ARCANA", Path(__file__).resolve().parent.parent))


def git(*args):
    try:
        result = subprocess.run(
            ["git"] + list(args), capture_output=True, text=True, cwd=str(ARCANA_ROOT)
        )
        return result.returncode == 0, result.stdout.strip()
    except FileNotFoundError:
        return False, ""


def main():
    issues = 0
    warnings = 0

    print()
    print("Analyzing Arcana Health")
    print("======================================")
    print(f"Arcana root: {ARCANA_ROOT}")
    print()

    # Health Check 1: File size analysis
    print("Analyzing file sizes...")
    large_files = 0

    size_exceptions = {"improve_arcana.md", "validate_structure.md", "analyze_health.py",
                       "summon.py", "register_skills.py"}

    for path in sorted(ARCANA_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in (".md", ".py"):
            continue

        rel = str(path.relative_to(ARCANA_ROOT))
        lines = len(path.read_text(errors="replace").splitlines())

        if "invocations/" in rel and path.name not in size_exceptions and lines > 800:
            print(f"  WARN  Large invocation: {rel} ({lines} lines, consider splitting)")
            warnings += 1
            large_files += 1

        if "rites/" in rel and path.suffix == ".py" and path.name not in size_exceptions and lines > 150:
            print(f"  WARN  Large rite script: {rel} ({lines} lines, consider refactoring)")
            warnings += 1
            large_files += 1

        if path.name == "INDEX.md" and lines > 200:
            print(f"  ERROR Bloated INDEX: {rel} ({lines} lines, should be < 200)")
            issues += 1
            large_files += 1

    if large_files == 0:
        print("  OK    All files appropriately sized")
    print()

    # Health Check 2: Complexity analysis
    print("Analyzing code complexity...")
    complex_scripts = 0

    complexity_exceptions = {"validate_security.py", "analyze_health.py", "summon.py"}

    for path in sorted((ARCANA_ROOT / "rites").glob("*.py")):
        if path.name in complexity_exceptions:
            continue

        content = path.read_text(errors="replace")
        functions = len(re.findall(r"^def ", content, re.MULTILINE))
        loops = len(re.findall(r"\bfor \b|\bwhile \b", content))
        conditionals = len(re.findall(r"\bif \b|\belif \b", content))
        total = functions + loops + conditionals

        if total > 25:
            print(f"  WARN  Complex script: {path.relative_to(ARCANA_ROOT)} "
                  f"(complexity: {total}, consider simplifying)")
            warnings += 1
            complex_scripts += 1

    if complex_scripts == 0:
        print("  OK    All scripts have manageable complexity")
    print()

    # Health Check 3: Documentation coverage
    print("Checking documentation coverage...")
    undocumented = 0

    invocations_dir = ARCANA_ROOT / "invocations"
    if invocations_dir.is_dir():
        for path in sorted(invocations_dir.rglob("*.md")):
            if path.name == "INDEX.md":
                continue

            index = path.parent / "INDEX.md"
            if not index.is_file():
                print(f"  WARN  Missing INDEX.md in: {path.parent.relative_to(ARCANA_ROOT)}")
                warnings += 1
                undocumented += 1
            elif path.name not in index.read_text(errors="replace"):
                print(f"  INFO  Not listed in INDEX (OK if dynamic discovery): "
                      f"{path.relative_to(ARCANA_ROOT)}")

    if undocumented == 0:
        print("  OK    Documentation coverage is good")
    print()

    # Health Check 4: Consistency checks
    print("Checking consistency...")

    versions = set()
    for path in sorted(ARCANA_ROOT.rglob("*.md")):
        content = path.read_text(errors="replace")
        for line in content.splitlines():
            if "Semantic Versioning" in line:
                continue
            if "Version" in line and ":" in line:
                for m in re.findall(r"v?(\d+\.\d+\.\d+)", line):
                    versions.add(m)

    if len(versions) > 2:
        print(f"  WARN  Multiple version numbers found: {', '.join(sorted(versions))}")
        print("         Arcana should primarily use one main version")
        warnings += 1
    else:
        print("  OK    Version numbering is reasonably consistent")

    broken_links = 0
    for path in sorted(ARCANA_ROOT.rglob("*")):
        if path.is_symlink() and not path.exists():
            print(f"  ERROR Broken symbolic link: {path.relative_to(ARCANA_ROOT)}")
            issues += 1
            broken_links += 1

    if broken_links == 0:
        print("  OK    No broken symbolic links")
    print()

    # Health Check 5: Git hygiene
    ok, _ = git("rev-parse", "--git-dir")
    if ok:
        print("Checking git hygiene...")

        large_tracked = 0
        ok, files = git("ls-files")
        if ok:
            for f in files.splitlines():
                fpath = ARCANA_ROOT / f
                if not fpath.is_file():
                    continue
                try:
                    size_kb = fpath.stat().st_size // 1024
                except OSError:
                    continue
                if size_kb > 100:
                    print(f"  WARN  Large file tracked by git: {f} ({size_kb}KB)")
                    warnings += 1
                    large_tracked += 1

        if large_tracked == 0:
            print("  OK    No large files tracked by git")

        ok, diff = git("diff", "--quiet")
        if not ok:
            print("  INFO  Unstaged changes detected (normal during development)")
        else:
            print("  OK    Working directory clean")
    else:
        print("  INFO  Not a git repository, skipping git checks")
    print()

    # Summary
    print("======================================")
    print("Health Analysis Summary")
    print()
    print(f"Issues:   {issues}")
    print(f"Warnings: {warnings}")
    print()

    if issues == 0 and warnings == 0:
        print("Arcana is in excellent health!")
        return 0
    elif issues == 0:
        print("Arcana is healthy with minor warnings")
        return 0
    else:
        print("Arcana has issues that should be addressed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
