"""Contract tests for Arcana's mutating-rite profiles."""

from pathlib import Path

from rite_profiles import (
    discover_write_capable_rites,
    profile_entries,
    validate_rite_profiles,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_rite_profile_contract_covers_write_capable_rites():
    contract, errors = validate_rite_profiles(REPO_ROOT)

    assert not errors
    assert contract is not None
    profiled = {entry["path"] for entry in profile_entries(contract)}
    assert profiled == discover_write_capable_rites(REPO_ROOT)


def test_rite_profile_docs_list_every_profiled_rite():
    contract, errors = validate_rite_profiles(REPO_ROOT)
    assert not errors

    docs = (REPO_ROOT / "docs" / "rite_profiles.md").read_text(encoding="utf-8")
    for entry in profile_entries(contract):
        assert entry["path"] in docs
        assert entry["profile"] in docs
