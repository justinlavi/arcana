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
                "arc": {
                    "skill_prefix": "arc",
                    "path": "skills/arc",
                    "slug_prefix": "",
                }
            },
        }),
    )
    _write(
        tmp_path / "skills/arc/example/SKILL.md",
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


def test_mutation_profile_mismatches_flags_only_disagreements():
    from validate_skill_refs import mutation_profile_mismatches

    surface = [
        {"command": "/a", "owner_type": "rite", "rite_owner": "rites/w.py", "mutation_profile": "apply_only"},
        {"command": "/b", "owner_type": "rite", "rite_owner": "rites/w.py", "mutation_profile": "plan_apply"},
        {"command": "/c", "owner_type": "rite", "rite_owner": "rites/ro.py", "mutation_profile": "read_only"},
        {"command": "/d", "owner_type": "rite", "rite_owner": "rites/ro.py", "mutation_profile": "apply_only"},
        {"command": "/e", "owner_type": "judgment", "rite_owner": None, "mutation_profile": "read_only"},
    ]
    rite_profiles = [{"path": "rites/w.py", "profile": "apply_only"}]

    flagged = {m[0] for m in mutation_profile_mismatches(surface, rite_profiles)}
    # /b disagrees with its profiled rite; /d is unprofiled so must be read_only.
    assert flagged == {"/b", "/d"}


def test_real_contracts_have_no_mutation_profile_drift():
    import rite_profiles
    from validate_skill_refs import mutation_profile_mismatches

    contract, _ = validate_command_surface(REPO_ROOT)
    rp = rite_profiles.profile_entries(rite_profiles.load_rite_profiles(REPO_ROOT))
    assert mutation_profile_mismatches(command_entries(contract), rp) == []


def test_skill_ref_report_includes_mutation_profile_drift():
    result = subprocess.run(
        [sys.executable, str(RITES / "validate_skill_refs.py"), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout
    report = json.loads(result.stdout)
    assert report["checked"]["mutation_profile_drift"] == 0
