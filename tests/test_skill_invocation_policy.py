"""Auto-invocation policy for validation and judgment-audit skills."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "skills"
FLAG = "disable-model-invocation: true"


def test_validation_entry_points_are_model_invocable():
    for family in ("arcana", "grimoire"):
        text = (SKILLS / family / "validate" / "SKILL.md").read_text(encoding="utf-8")
        assert FLAG not in text, f"{family}/validate should stay model-invocable"


def test_no_individual_validator_skills_remain():
    for family in ("arcana", "grimoire"):
        assert sorted((SKILLS / family).glob("validate-*")) == []


def test_judgment_audits_do_not_auto_invoke():
    for audit in ("audit-boundaries", "audit-semantics"):
        text = (SKILLS / "grimoire" / audit / "SKILL.md").read_text(encoding="utf-8")
        assert FLAG in text, f"judgment audit {audit} should not auto-invoke"
