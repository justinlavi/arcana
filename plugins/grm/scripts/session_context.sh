#!/bin/sh
# Session-start hook entry for the grm plugin.
# Finds a Python 3.10+ interpreter and runs session_context.py; prints a
# one-line note when none is available so the agent can tell the user.

here="$(cd "$(dirname "$0")" && pwd)"

for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
            exec "$candidate" "$here/session_context.py"
        fi
    fi
done
if command -v py >/dev/null 2>&1; then
    if py -3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
        exec py -3 "$here/session_context.py"
    fi
fi

echo "engine: Python 3.10 or newer is not installed, so the Grimoire engine cannot run; install Python from python.org (Windows: tick Add to PATH) and start a new session."
exit 0
