"""Contract tests for the Summoning Rite behavior matrix."""

import json
import re
from pathlib import Path

from summon_contract import (
    CONTRACT_PATH,
    bootstrap_environment_entries,
    mode_entries,
    pipeline_entries,
    release_asset_entries,
    validate_summon_contract,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_summon_contract_is_valid():
    contract, errors = validate_summon_contract(REPO_ROOT)

    assert not errors
    assert contract is not None
    assert {entry["id"] for entry in mode_entries(contract)} == {
        "shell_bootstrap",
        "python_dispatcher",
        "python_cli",
        "python_gui",
        "release_binary",
        "release_workflow",
        "agent_reconcile",
    }


def test_summon_contract_names_required_pipeline():
    contract = json.loads((REPO_ROOT / CONTRACT_PATH).read_text(encoding="utf-8"))
    steps = {entry["id"]: entry for entry in pipeline_entries(contract)}

    assert list(steps) == [
        "check_git",
        "install_arcana",
        "discover_grimoires",
        "install_grimoires",
        "update_library",
        "inject_agent_blocks",
        "sync_skills",
    ]
    for step in steps.values():
        assert {"python_cli", "python_gui"} <= set(step["required_for"])


def test_summon_contract_release_assets_match_release_docs():
    contract = json.loads((REPO_ROOT / CONTRACT_PATH).read_text(encoding="utf-8"))
    release_docs = (REPO_ROOT / "docs" / "release.md").read_text(encoding="utf-8")

    for asset in release_asset_entries(contract):
        assert asset["archive"] in release_docs
        assert asset["checksum"] in release_docs


def test_summon_contract_environment_controls_match_bootstrap():
    contract = json.loads((REPO_ROOT / CONTRACT_PATH).read_text(encoding="utf-8"))
    bootstrap = (REPO_ROOT / "rites" / "summon.sh").read_text(encoding="utf-8")

    documented = {entry["name"] for entry in bootstrap_environment_entries(contract)}
    for name in documented:
        assert name in bootstrap, f"{name} is in the contract but not used in summon.sh"

    # Reverse direction: every GRIMOIRE_SUMMON_* the shell assigns a default to
    # must be documented in the contract, so new knobs can't escape the surface.
    assigned = set(re.findall(r"(GRIMOIRE_SUMMON_[A-Z_]+):=", bootstrap))
    undocumented = sorted(assigned - documented)
    assert not undocumented, f"summon.sh assigns env vars absent from the contract: {undocumented}"
