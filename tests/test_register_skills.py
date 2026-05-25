"""Temp-target tests for the skill registration rite."""

from pathlib import Path

import register_skills


def _snapshot(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_register_skills_dry_run_plans_without_writing(tmp_path, monkeypatch, capsys):
    target = tmp_path / "codex" / "skills"
    existing = target / "arc-existing"
    existing.mkdir(parents=True)
    (existing / "SKILL.md").write_text("user-authored\n", encoding="utf-8", newline="\n")
    monkeypatch.setattr(register_skills, "LOCAL_LIBRARY", tmp_path / "missing-library.json")

    result = register_skills.register_target(
        "codex",
        {
            "label": "Codex Test",
            "path": target,
            "pointer_only": True,
        },
        dry_run=True,
    )

    output = capsys.readouterr().out
    assert result["mode"] == "plan"
    assert result["registered"] > 0
    assert "would register" in output
    assert "would clean" in output
    assert (existing / "SKILL.md").read_text(encoding="utf-8") == "user-authored\n"
    assert not (target / "arc-help").exists()


def test_register_skills_apply_is_idempotent_for_pointer_target(tmp_path, monkeypatch):
    target = tmp_path / "codex" / "skills"
    monkeypatch.setattr(register_skills, "LOCAL_LIBRARY", tmp_path / "missing-library.json")
    config = {
        "label": "Codex Test",
        "path": target,
        "pointer_only": True,
    }

    first = register_skills.register_target("codex", config, dry_run=False)
    first_snapshot = _snapshot(target)
    second = register_skills.register_target("codex", config, dry_run=False)
    second_snapshot = _snapshot(target)

    assert first["mode"] == "apply"
    assert second["mode"] == "apply"
    assert first["registered"] == second["registered"]
    assert first_snapshot == second_snapshot
    assert (target / "arc-help" / "SKILL.md").is_file()
    assert all(path.name == "SKILL.md" for path in target.rglob("*") if path.is_file())
