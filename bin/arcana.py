#!/usr/bin/env python3
"""Launcher body: resolve the engine and run one rite.

`bin/arcana` (POSIX sh) and `bin/arcana.cmd` (Windows) find a Python 3.10+ and
hand off here. The engine is the checkout this file sits in (`<engine>/bin/`)
or, when the launcher runs from the grm plugin, `$ARCANA_HOME`, default
`~/grimoires/arcana`.

    arcana <rite> [arguments...]
    arcana --list
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
USAGE = (
    "usage: arcana <rite> [arguments...]\n"
    "       arcana --list\n"
    "Runs rites/<rite>.py from the Arcana engine with this Python."
)


def engine_root() -> Path:
    beside = HERE.parent
    if (beside / "rites").is_dir():
        return beside
    return Path(os.environ.get("ARCANA_HOME") or Path.home() / "grimoires" / "arcana").expanduser()


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(USAGE)
        return 0
    rites = engine_root() / "rites"
    if argv[0] == "--list":
        if not rites.is_dir():
            print(f"arcana: engine not found at {rites.parent}", file=sys.stderr)
            return 2
        for path in sorted(rites.glob("*.py")):
            if not path.name.startswith("_"):
                print(path.stem)
        return 0
    rite, args = argv[0], argv[1:]
    script = rites / f"{rite}.py"
    if not script.is_file():
        print(f"arcana: no rite named '{rite}' (expected {script})", file=sys.stderr)
        return 2
    if sys.version_info < (3, 10):
        print("arcana: Python 3.10 or newer is required", file=sys.stderr)
        return 127
    command = [sys.executable, str(script), *args]
    if os.name == "posix":
        os.execv(sys.executable, command)
    return subprocess.run(command).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
