"""End-to-end tests: every validator runs as a subprocess against fixture grimoires.

The good_grimoire fixture must produce exit 0 from every validator that
accepts a `--grimoire` flag. The bad_* fixtures must produce exit 1 from
their corresponding validator(s).

These tests exercise the validators exactly the way the orchestrator and
grimoire-skill flows do - via subprocess invocation, so any breakage in argv
parsing, exit codes, or stdout flushing is caught.
"""

import subprocess
import sys
import shutil
import json
from pathlib import Path

import pytest

# rites/ is on sys.path via tests/conftest.py; the orchestrator's validator
# lists are the source of truth for the expected validator counts and names.
import validate

REPO_ROOT = Path(__file__).resolve().parent.parent
RITES = REPO_ROOT / "rites"
FIXTURES = Path(__file__).parent / "fixtures"
GOOD = FIXTURES / "good_grimoire"
BAD_FRONT = FIXTURES / "bad_frontmatter"
BAD_LINKS = FIXTURES / "bad_links"
WARN_LABELS = FIXTURES / "warn_labels"

ARCANA_VALIDATOR_NAMES = {Path(name).stem for name in validate.ARCANA_RITES}
GRIMOIRE_VALIDATOR_NAMES = {Path(name).stem for name in validate.GRIMOIRE_RITES}


def _run(script: str, grimoire: Path, *extra_args: str) -> subprocess.CompletedProcess:
    """Invoke a validator against a fixture grimoire."""
    return subprocess.run(
        [sys.executable, str(RITES / script), "--grimoire", str(grimoire), *extra_args],
        capture_output=True,
        text=True,
        timeout=30,
    )


# ---------------------------------------------------------------------------
# Good fixture - every grimoire-aware validator must exit 0
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "script",
    [
        "validate_encoding.py",
        "validate_format.py",
        "validate_frontmatter.py",
        "validate_grimoire_structure.py",
        "validate_links.py",
        "validate_orphans.py",
        "validate_portability.py",
        "validate_provenance.py",
    ],
)
def test_good_grimoire_passes(script):
    result = _run(script, GOOD)
    assert result.returncode == 0, (
        f"{script} unexpectedly failed on good_grimoire fixture\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# Bad fixtures - the corresponding validator must exit non-zero
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


def test_bad_frontmatter_structured_diagnostics_have_codes():
    result = _run("validate_frontmatter.py", BAD_FRONT, "--format", "json")

    assert result.returncode != 0
    report = json.loads(result.stdout)
    codes = {diagnostic["code"] for diagnostic in report["diagnostics"]}
    assert "FRONTMATTER_INVALID_AUTHORITY" in codes
    assert "FRONTMATTER_INVALID_DATE_FORMAT" in codes
    assert "FRONTMATTER_MISSING_TYPE" in codes


def test_validator_scans_sibling_of_skip_dir(tmp_path):
    grimoire = tmp_path / "good_grimoire"
    shutil.copytree(GOOD, grimoire)
    extra = grimoire / "sources_extra"
    extra.mkdir()
    (extra / "broken.md").write_text(
        "---\n"
        'type: reference\n'
        'title: "Broken"\n'
        "tags: []\n"
        "authority: grimoire\n"
        "last_verified: 2026-05-25\n"
        "---\n\n"
        "See [[chapters/nope/nope|nope]].\n",
        encoding="utf-8",
    )

    result = _run("validate_links.py", grimoire)

    # `sources_extra` shares a prefix with the skipped `sources` dir; it must
    # still be scanned, so the broken wikilink inside it is caught.
    assert result.returncode != 0
    assert "sources_extra" in result.stdout


def test_source_type_is_reserved_for_sources_layer(tmp_path):
    grimoire = tmp_path / "good_grimoire"
    shutil.copytree(GOOD, grimoire)
    (grimoire / "chapters/recipes/source_note.md").write_text(
        """---
type: source
title: "Misplaced Source Note"
tags: [type/source]
sources: ["https://example.com/source"]
authority: external
last_verified: 2026-05-25
---

# Misplaced Source Note
""",
        encoding="utf-8",
        newline="\n",
    )

    result = _run("validate_frontmatter.py", grimoire, "--format", "json")

    assert result.returncode != 0
    report = json.loads(result.stdout)
    codes = {diagnostic["code"] for diagnostic in report["diagnostics"]}
    assert "FRONTMATTER_SOURCE_OUTSIDE_SOURCES" in codes


def test_provenance_validates_source_wrappers(tmp_path):
    grimoire = tmp_path / "good_grimoire"
    shutil.copytree(GOOD, grimoire)
    (grimoire / "sources/example_source.md").write_text(
        """---
type: source
title: "Example Source"
tags: [type/source]
sources: ["https://example.com/source"]
authority: external
last_verified: 2026-05-25
---

# Example Source
""",
        encoding="utf-8",
        newline="\n",
    )

    result = _run("validate_provenance.py", grimoire, "--format", "json")

    assert result.returncode == 0, result.stdout
    report = json.loads(result.stdout)
    assert report["checked"]["source_wrappers"] == 1

    (grimoire / "sources/bad_source.md").write_text(
        """---
type: source
title: "Bad Source"
tags: [type/source]
sources: ["sources/bad_source.md"]
authority: grimoire
last_verified: 2026-05-25
---

# Bad Source
""",
        encoding="utf-8",
        newline="\n",
    )

    result = _run("validate_provenance.py", grimoire, "--format", "json")

    assert result.returncode != 0
    report = json.loads(result.stdout)
    codes = {diagnostic["code"] for diagnostic in report["diagnostics"]}
    assert "PROVENANCE_SOURCE_WRAPPER_AUTHORITY" in codes
    assert "PROVENANCE_SOURCE_WRAPPER_SELF_REFERENCE" in codes


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


def test_bad_links_structured_diagnostics_have_codes():
    result = _run("validate_links.py", BAD_LINKS, "--format", "json")

    assert result.returncode != 0
    report = json.loads(result.stdout)
    codes = [diagnostic["code"] for diagnostic in report["diagnostics"]]
    assert "LINK_MARKDOWN_INTERNAL" in codes
    assert "LINK_MARKDOWN_BROKEN" in codes
    assert "LINK_WIKILINK_BROKEN" in codes


def test_markdown_page_link_is_caught_in_vault_surface(tmp_path):
    grimoire = tmp_path / "good_grimoire"
    shutil.copytree(GOOD, grimoire)
    leaf = grimoire / "chapters/recipes/sourdough.md"
    leaf.write_text(
        leaf.read_text(encoding="utf-8") + "\nSee [recipes](recipes.md).\n",
        encoding="utf-8",
        newline="\n",
    )

    result = _run("validate_links.py", grimoire, "--format", "json")

    assert result.returncode != 0
    report = json.loads(result.stdout)
    codes = {diagnostic["code"] for diagnostic in report["diagnostics"]}
    assert "LINK_MARKDOWN_INTERNAL" in codes


def test_markdown_page_link_is_allowed_in_public_doc(tmp_path):
    grimoire = tmp_path / "good_grimoire"
    shutil.copytree(GOOD, grimoire)
    readme = grimoire / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\nSee [recipes](chapters/recipes/recipes.md).\n",
        encoding="utf-8",
        newline="\n",
    )

    result = _run("validate_links.py", grimoire, "--format", "json")

    assert result.returncode == 0, result.stdout


def test_wikilink_is_caught_in_public_doc(tmp_path):
    grimoire = tmp_path / "good_grimoire"
    shutil.copytree(GOOD, grimoire)
    readme = grimoire / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\nSee [[chapters/recipes/recipes|recipes]].\n",
        encoding="utf-8",
        newline="\n",
    )

    result = _run("validate_links.py", grimoire, "--format", "json")

    assert result.returncode != 0
    report = json.loads(result.stdout)
    codes = {diagnostic["code"] for diagnostic in report["diagnostics"]}
    assert "LINK_WIKILINK_PUBLIC_DOC" in codes


def test_verbose_wikilink_label_warns_without_failing():
    result = _run("validate_links.py", WARN_LABELS)
    assert result.returncode == 0, (
        "Verbose wikilink labels should warn but not fail validation\n"
        f"--- stdout ---\n{result.stdout}"
    )
    assert "WARN" in result.stdout
    assert "Display label should be target filename only" in result.stdout


def test_verbose_wikilink_label_structured_warning_does_not_fail():
    result = _run("validate_links.py", WARN_LABELS, "--format", "json")

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["summary"]["errors"] == 0
    assert report["summary"]["warnings"] == 1
    assert report["diagnostics"][0]["code"] == "LINK_LABEL_VERBOSE"


def test_structure_validator_catches_stale_obsidian_graph(tmp_path):
    grimoire = tmp_path / "good_grimoire"
    shutil.copytree(GOOD, grimoire)
    graph = grimoire / ".obsidian" / "graph.json"
    graph.write_text("{}\n", encoding="utf-8")

    result = _run("validate_grimoire_structure.py", grimoire)

    assert result.returncode != 0
    assert ".obsidian/graph.json" in result.stdout


# ---------------------------------------------------------------------------
# Arcana itself - meta-test that the suite still passes against the live tree
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


def test_full_validator_suite_emits_structured_aggregate_report():
    result = subprocess.run(
        [sys.executable, str(RITES / "validate.py"), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["validator"] == "validate"
    assert report["status"] == "pass"
    assert report["checked"]["validators"] == len(validate.ARCANA_RITES)
    assert len(report["reports"]) == len(validate.ARCANA_RITES)
    assert {
        validator_report["validator"] for validator_report in report["reports"]
    } == ARCANA_VALIDATOR_NAMES


def test_grimoire_validator_suite_passes_good_fixture():
    result = subprocess.run(
        [sys.executable, str(RITES / "validate.py"), "--grimoire", str(GOOD), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["validator"] == "validate"
    assert report["profile"] == "grimoire"
    assert report["status"] == "pass"
    assert report["checked"]["validators"] == len(validate.GRIMOIRE_RITES)
    assert len(report["reports"]) == len(validate.GRIMOIRE_RITES)
    assert {
        validator_report["validator"] for validator_report in report["reports"]
    } == GRIMOIRE_VALIDATOR_NAMES


def test_grimoire_validator_suite_fails_bad_fixture():
    result = subprocess.run(
        [sys.executable, str(RITES / "validate.py"), "--grimoire", str(BAD_FRONT), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode != 0
    report = json.loads(result.stdout)
    assert report["profile"] == "grimoire"
    assert report["status"] == "fail"
    assert report["summary"]["failed_validators"] >= 1
    failing = {
        validator_report["validator"]
        for validator_report in report["reports"]
        if validator_report["status"] == "fail"
    }
    assert "validate_frontmatter" in failing
