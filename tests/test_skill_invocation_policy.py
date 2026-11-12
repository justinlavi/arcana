"""Auto-invocation policy: evaluation entry points stay model-invocable, the
destructive maintainer skill does not."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "skills"
FLAG = "disable-model-invocation: true"


def test_evaluation_entry_points_are_model_invocable():
    for path in (SKILLS / "arc" / "validate" / "SKILL.md", SKILLS / "grm" / "check" / "SKILL.md"):
        text = path.read_text(encoding="utf-8")
        assert FLAG not in text, f"{path.parent.name} should stay model-invocable"


def test_no_individual_validator_or_audit_skills_remain():
    for family in ("arc", "grm"):
        assert sorted((SKILLS / family).glob("validate-*")) == []
        assert sorted((SKILLS / family).glob("audit-*")) == []


def test_destructive_maintainer_skill_does_not_auto_invoke():
    text = (SKILLS / "arc" / "clean" / "SKILL.md").read_text(encoding="utf-8")
    assert FLAG in text, "arc/clean deletes artifacts and must not auto-invoke"
