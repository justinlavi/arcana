"""Auto-invocation policy for validator skills.

Per docs/agent_configuration.md: the orchestrators (`/arc-validate-all`,
`/grm-validate-all`) are the auto-invoke entry points, while individual
validators set `disable-model-invocation: true` so they do not over-activate.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "skills"
FLAG = "disable-model-invocation: true"


def test_individual_validators_disable_model_invocation():
    for family in ("arcana", "grimoire"):
        for skill_dir in sorted((SKILLS / family).glob("validate-*")):
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            if skill_dir.name == "validate-all":
                # The orchestrator is the intended auto-invoke entry point.
                assert FLAG not in text, f"{family}/{skill_dir.name} should stay model-invocable"
            else:
                assert FLAG in text, f"{family}/{skill_dir.name} should set disable-model-invocation"
