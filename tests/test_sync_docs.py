"""Tests for generated documentation sync."""

from pathlib import Path

import sync_docs

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_skill_catalog_renders_command_surface_metadata():
    skills = sync_docs.collect_skills()
    metadata = sync_docs.load_command_metadata()
    content = sync_docs.render_skills_doc(skills, metadata)

    assert (
        "| Skill | Description | Workflow | Owner | Mutation | Rite | Guard | Validation |"
        in content
    )
    assert "[`/grm-validate`](../skills/grimoire/validate/SKILL.md)" in content
    assert (
        "[`validate.md`](../invocations/grimoire/validators/validate.md)"
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
