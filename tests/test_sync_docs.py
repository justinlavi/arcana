"""Tests for generated documentation sync."""

from pathlib import Path

import sync_docs

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_skill_catalog_leads_with_user_facing_table():
    skills = sync_docs.collect_skills()
    metadata = sync_docs.load_command_metadata()
    content = sync_docs.render_skills_doc(skills, metadata)

    # The user catalog leads; the engineering matrix lives under the contract.
    assert "| Command | What it does | Input |" in content
    assert "## Command contract" in content
    catalog_pos = content.index("| Command | What it does | Input |")
    contract_pos = content.index("## Command contract")
    assert catalog_pos < contract_pos, "user catalog must precede the command contract"


def test_skill_catalog_renders_command_surface_metadata():
    skills = sync_docs.collect_skills()
    metadata = sync_docs.load_command_metadata()
    content = sync_docs.render_skills_doc(skills, metadata)

    assert (
        "| Command | Workflow | Owner | Mutation | Rite | Guard | Validation |"
        in content
    )
    assert "[`/grm-validate`](../skills/grm/validate/SKILL.md)" in content
    assert (
        "[`validate.md`](../invocations/grm/validators/validate.md)"
        in content
    )
    assert "[`validate.py`](../rites/validate.py)" in content
    assert (
        "[`grimoire_directory_guard.md`](../invocations/meta/grimoire_directory_guard.md)"
        in content
    )
    assert (
        "`python rites/validate.py --grimoire GRIMOIRE_ROOT [all"
        in content
    )


def test_skill_catalog_file_is_synced():
    skills = sync_docs.collect_skills()
    metadata = sync_docs.load_command_metadata()
    expected = sync_docs.render_skills_doc(skills, metadata)
    current = (REPO_ROOT / "docs/skills.md").read_text(encoding="utf-8")

    assert current == expected
