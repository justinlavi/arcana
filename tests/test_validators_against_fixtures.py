"""End-to-end tests: every validator runs as a subprocess against fixture grimoires.

The good_grimoire fixture must produce exit 0 from every validator that
accepts a `--grimoire` flag. The bad_* fixtures must produce exit 1 from
their corresponding validator(s).

These tests exercise the validators exactly the way the orchestrator and
domain-skill flows do — via subprocess invocation, so any breakage in argv
parsing, exit codes, or stdout flushing is caught.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RITES = REPO_ROOT / "rites"
FIXTURES = Path(__file__).parent / "fixtures"
GOOD = FIXTURES / "good_grimoire"
BAD_FRONT = FIXTURES / "bad_frontmatter"
BAD_LINKS = FIXTURES / "bad_links"


def _run(script: str, grimoire: Path) -> subprocess.CompletedProcess:
    """Invoke a validator against a fixture grimoire."""
    return subprocess.run(
        [sys.executable, str(RITES / script), "--grimoire", str(grimoire)],
        capture_output=True,
        text=True,
        timeout=30,
    )


# ---------------------------------------------------------------------------
# Good fixture — every domain-aware validator must exit 0
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "script",
    [
        "validate_frontmatter.py",
        "validate_links.py",
        "validate_orphans.py",
        "validate_provenance.py",
        "validate_domain_structure.py",
    ],
)
def test_good_grimoire_passes(script):
    result = _run(script, GOOD)
    assert result.returncode == 0, (
        f"{script} unexpectedly failed on good_grimoire fixture\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# Bad fixtures — the corresponding validator must exit non-zero
# ---------------------------------------------------------------------------


def test_bad_frontmatter_is_caught():
    result = _run("validate_frontmatter.py", BAD_FRONT)
    assert result.returncode != 0, (
        "validate_frontmatter.py should have flagged bad_frontmatter fixture\n"
        f"--- stdout ---\n{result.stdout}"
    )
    out = result.stdout
    # The three deliberate violations should each surface.
    assert "missing required field" in out or "missing `type" in out
    assert "invalid authority" in out
    assert "last_verified" in out


def test_bad_links_is_caught():
    result = _run("validate_links.py", BAD_LINKS)
    assert result.returncode != 0, (
        "validate_links.py should have flagged bad_links fixture\n"
        f"--- stdout ---\n{result.stdout}"
    )
    out = result.stdout
    assert "BROKEN" in out
    # Both a markdown link and a wikilink should be reported broken.
    assert "does_not_exist.md" in out
    assert "no-such-wikilink" in out


# ---------------------------------------------------------------------------
# Arcana itself — meta-test that the suite still passes against the live tree
# ---------------------------------------------------------------------------


def test_full_validator_suite_passes_against_arcana():
    """The orchestrator should keep returning 0 on Arcana itself.

    This guards against any future _lib change that subtly breaks a validator.
    """
    result = subprocess.run(
        [sys.executable, str(RITES / "validate.py")],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        "Full validator suite failed against Arcana\n"
        f"--- stdout (tail) ---\n{result.stdout[-2000:]}\n"
        f"--- stderr (tail) ---\n{result.stderr[-1000:]}"
    )
