"""Per-grimoire naming convention and case-insensitive folder roles (AB-03).

Any casing is valid in a grimoire; the recorded convention (`naming` in
grimoire.json, snake_case by default) is advisory for agents, and the folder
roles the validators recognise (sources, templates, ...) must not depend on
case either.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import _lib
import validate_grimoire_structure  # noqa: F401  (import guard: module must load)

REPO_ROOT = Path(__file__).resolve().parent.parent
RITES = REPO_ROOT / "rites"
GOOD = Path(__file__).parent / "fixtures" / "good_grimoire"


def _manifest(tmp_path: Path, **fields) -> Path:
    data = {"name": "g", "skill_prefix": "gg", "description": "x"}
    data.update(fields)
    (tmp_path / "grimoire.json").write_text(json.dumps(data), encoding="utf-8")
    return tmp_path


def test_naming_defaults_to_snake_case_when_absent(tmp_path):
    manifest, errors = _lib.load_manifest(_manifest(tmp_path))
    assert errors == []
    assert _lib.naming_convention(manifest) == "snake_case"
    assert _lib.naming_convention(None) == "snake_case"


def test_naming_accepts_any_named_style(tmp_path):
    for style in ("snake_case", "preserve", "kebab-case", "PascalCase", "Title Case"):
        manifest, errors = _lib.load_manifest(_manifest(tmp_path, naming=style))
        assert errors == [], style
        assert _lib.naming_convention(manifest) == style


def test_naming_rejects_empty_or_non_string(tmp_path):
    for bad in ("", "   ", 3, ["snake_case"]):
        _, errors = _lib.load_manifest(_manifest(tmp_path, naming=bad))
        assert any("naming" in e for e in errors), bad


def test_source_folder_is_recognised_case_insensitively():
    assert _lib.is_colocated_source_path("chapters/travel/Sources/receipt.pdf")
    assert _lib.is_colocated_source_path("chapters/travel/SOURCES/receipt.pdf")
    assert _lib.is_inside_colocated_source_dir("chapters/travel/Sources")
    assert not _lib.is_colocated_source_path("chapters/sources/receipt.pdf")


def test_is_skipped_ignores_case():
    assert _lib.is_skipped("Sources/x.md", ["sources"])
    assert _lib.is_skipped("Inbox/x.md", {"sources", "inbox"})
    assert not _lib.is_skipped("sources_extra/x.md", ["sources"])


def test_capitalised_asset_folder_needs_no_hub(tmp_path):
    grimoire = tmp_path / "g"
    shutil.copytree(GOOD, grimoire)
    templates = grimoire / "chapters" / "recipes" / "Templates"
    templates.mkdir()
    (templates / "card.md").write_text("# card\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(RITES / "validate_grimoire_structure.py"), "--grimoire", str(grimoire)],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout


def test_adopt_records_naming(tmp_path):
    home = tmp_path / "grimoires"
    target = home / "notes-grimoire"
    (target / "chapters").mkdir(parents=True)
    result = subprocess.run(
        [sys.executable, str(RITES / "adopt_grimoire.py"), "notes-grimoire",
         "--skill-prefix", "nt", "--home", str(home), "--naming", "preserve", "--format", "json"],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    manifest = json.loads((target / "grimoire.json").read_text(encoding="utf-8"))
    assert manifest["naming"] == "preserve"
