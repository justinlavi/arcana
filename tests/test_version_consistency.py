"""The VERSION file and pyproject.toml must declare the same version."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_ROOT / "VERSION"
PYPROJECT = REPO_ROOT / "pyproject.toml"


def _pyproject_version() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"', text, re.MULTILINE)
    assert match, "no [project] version found in pyproject.toml"
    return match.group(1)


def test_version_file_matches_pyproject():
    version_file = VERSION_FILE.read_text(encoding="utf-8").strip()
    assert version_file == _pyproject_version(), (
        f"VERSION ({version_file}) and pyproject.toml ({_pyproject_version()}) disagree; "
        "bump both together."
    )
