"""Contract tests for the Arcana agent target registry."""

import json
from pathlib import Path

import agent_targets
import register_skills

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_agent_target_registry_is_valid():
    contract, errors = agent_targets.validate_agent_targets(REPO_ROOT)

    assert not errors
    assert contract is not None
    assert agent_targets.agent_target_ids(REPO_ROOT) == [
        "claude",
        "codex",
        "chatgpt-hosted",
        "github-copilot",
        "cursor",
    ]


def test_agent_target_registry_drives_registration_targets():
    expected = agent_targets.skill_registration_targets(REPO_ROOT)

    assert register_skills.SKILL_TARGETS == expected
    assert expected["claude"]["pointer_only"] is False
    assert expected["codex"]["pointer_only"] is True


def test_agent_target_docs_cover_registry_entries():
    contract = json.loads((REPO_ROOT / agent_targets.CONTRACT_PATH).read_text(encoding="utf-8"))
    docs = (REPO_ROOT / "docs" / "agent_targets.md").read_text(encoding="utf-8")

    for entry in agent_targets.target_entries(contract):
        assert entry["label"] in docs
        assert str(entry["instruction_target"]) in docs
        if entry["skill_target"] is not None:
            assert entry["skill_target"] in docs


def test_summon_source_bootstrap_downloads_agent_target_contract():
    bootstrap = (REPO_ROOT / "rites" / "summon.sh").read_text(encoding="utf-8")

    assert "rites/agent_targets.py" in bootstrap
    assert "rites/data/agent_targets.json" in bootstrap
    assert '"$SCRIPT_DIR/data/agent_targets.json"' in bootstrap


def test_summon_binary_bundles_agent_target_contract():
    build_script = (REPO_ROOT / "rites" / "build_summon_binary.py").read_text(encoding="utf-8")

    assert '"rites" / "data"' in build_script
    assert "rites/data" in build_script
