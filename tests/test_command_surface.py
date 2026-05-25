"""Contract tests for the public command-surface matrix."""

import json
import subprocess
import sys
from pathlib import Path

from command_surface import (
    CONTRACT_PATH,
    command_entries,
    discover_skill_commands,
    validate_command_surface,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
RITES = REPO_ROOT / "rites"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def test_command_surface_contract_covers_public_skills():
    contract, errors = validate_command_surface(REPO_ROOT)

    assert not errors
    assert contract is not None
    entries = command_entries(contract)
    discovered = discover_skill_commands(REPO_ROOT)
    assert {entry["command"] for entry in entries} == set(discovered)
    assert len(entries) == len(discovered)


def test_command_surface_validator_reports_missing_public_skill(tmp_path):
    _write(
        tmp_path / "arcana.json",
        json.dumps({
            "skill_prefix": "arc",
            "skill_families": {
                "arcana": {
                    "skill_prefix": "arc",
                    "path": "skills/arcana",
                    "slug_prefix": "",
                }
            },
        }),
    )
    _write(
        tmp_path / "skills/arcana/example/SKILL.md",
        "---\nname: {{SKILL_PREFIX}}-example\ndescription: Example\n---\n",
    )
    _write(
        tmp_path / CONTRACT_PATH,
        json.dumps({
            "schema_version": 1,
            "commands": [],
        }),
    )

    _, errors = validate_command_surface(tmp_path)

    assert any(error["code"] == "COMMAND_SURFACE_MISSING" for error in errors)


def test_skill_ref_validator_reports_command_surface_counts():
    result = subprocess.run(
        [sys.executable, str(RITES / "validate_skill_refs.py"), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout
    report = json.loads(result.stdout)
    assert report["checked"]["command_surface_entries"] == len(discover_skill_commands(REPO_ROOT))
    assert report["checked"]["command_surface_errors"] == 0
