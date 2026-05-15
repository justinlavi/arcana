"""Pytest configuration — make `from _lib import ...` work in tests."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RITES_DIR = REPO_ROOT / "rites"

if str(RITES_DIR) not in sys.path:
    sys.path.insert(0, str(RITES_DIR))
