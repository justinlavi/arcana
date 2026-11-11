"""Seeded scaffold files and the Codex skill-root move."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import agent_targets
import scaffold_contract as sc
import sync_skills
import update_grimoires

REPO_ROOT = Path(__file__).resolve().parent.parent
RITES = REPO_ROOT / "rites"
GOOD = Path(__file__).parent / "fixtures" / "good_grimoire"


def _structure(grimoire: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(RITES / "validate_grimoire_structure.py"), "--grimoire", str(grimoire), "--format", "json"],
        capture_output=True, text=True, timeout=60,
    )
    return {"returncode": result.returncode, "report": json.loads(result.stdout)}


def test_gitignore_is_seeded_not_managed():
    contract = sc.load_scaffold_contract(REPO_ROOT)
    assert ".gitignore" in sc.seeded_scaffold_files(contract)
    assert ".gitignore" not in sc.managed_scaffold_files(contract)
    assert ".gitignore" not in sc.required_customized_files(contract)
    assert (REPO_ROOT / "formulae" / "grimoire" / "gitignore").is_file()


def test_missing_seeded_file_is_a_warning_only(tmp_path):
    grimoire = tmp_path / "g"
    shutil.copytree(GOOD, grimoire)
    (grimoire / ".gitignore").unlink(missing_ok=True)

    out = _structure(grimoire)
    diags = out["report"]["diagnostics"]
    seeded = [d for d in diags if d["code"] == "GRIMOIRE_STRUCTURE_MISSING_SEEDED"]

    assert out["returncode"] == 0
    assert seeded and seeded[0]["severity"] == "warning"


def test_heal_seeds_gitignore_when_absent_and_keeps_a_customised_one(tmp_path):
    grimoire = tmp_path / "g"
    shutil.copytree(GOOD, grimoire)
    subprocess.run(["git", "init", "-q", str(grimoire)], check=True)
    (grimoire / ".gitignore").unlink(missing_ok=True)

    result = update_grimoires.default_heal(grimoire, REPO_ROOT)
    assert ".gitignore" in result["scaffold_synced"]
    seeded = (grimoire / ".gitignore").read_text(encoding="utf-8")
    assert ".obsidian/*" in seeded

    (grimoire / ".gitignore").write_text("# mine\n", encoding="utf-8")
    result = update_grimoires.default_heal(grimoire, REPO_ROOT)
    assert ".gitignore" not in result["scaffold_synced"]
    assert (grimoire / ".gitignore").read_text(encoding="utf-8") == "# mine\n"
    assert _structure(grimoire)["returncode"] == 0


def test_codex_registry_moved_to_agents_skills():
    targets = agent_targets.skill_registration_targets(REPO_ROOT)
    codex = targets["codex"]
    assert codex["path"] == Path.home() / ".agents" / "skills"
    assert codex["deprecated_paths"] == [Path.home() / ".codex" / "skills"]
    _, errors = agent_targets.validate_agent_targets(REPO_ROOT)
    assert errors == []


def test_deprecated_location_is_cleaned_of_managed_skills_only(tmp_path, monkeypatch):
    old = tmp_path / "codex" / "skills"
    (old / "grm-stale").mkdir(parents=True)
    (old / "grm-stale" / "SKILL.md").write_text("old\n", encoding="utf-8")
    (old / "mine").mkdir()
    (old / "mine" / "SKILL.md").write_text("keep\n", encoding="utf-8")
    new = tmp_path / "agents" / "skills"
    monkeypatch.setattr(sync_skills, "LOCAL_LIBRARY", tmp_path / "missing-library.json")

    config = {"label": "Codex Test", "path": new, "pointer_only": True, "deprecated_paths": [old]}
    planned = sync_skills.register_target("codex", dict(config), dry_run=True)
    assert (old / "grm-stale").is_dir()  # plan mode writes nothing
    assert planned["cleaned"] >= 1

    applied = sync_skills.register_target("codex", dict(config), dry_run=False)
    assert applied["cleaned"] >= 1
    assert not (old / "grm-stale").exists()
    assert (old / "mine" / "SKILL.md").read_text(encoding="utf-8") == "keep\n"
    assert (new / "grm-help" / "SKILL.md").is_file()
