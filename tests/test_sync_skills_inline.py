"""Registration inlines dynamic-context directives so generated skills are
self-contained (AB-17): no !`cat` survives, no shell runs at load time, and the
working directory of the session no longer matters."""

from pathlib import Path

import sync_skills as sync_skills


def _spec(source_dir: Path, grimoire_path: str = "") -> sync_skills.SkillSpec:
    return sync_skills.SkillSpec(
        command_name="grm-probe",
        command_slug="probe",
        skill_prefix="grm",
        source_dir=source_dir,
        source_label="Test",
        source_kind="arcana",
        source_key="grm",
        source_repo="arcana",
        grimoire_path=grimoire_path,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def test_render_inlines_invocation_and_leaves_no_directive(tmp_path):
    invocation = tmp_path / "invocations" / "grm" / "probe.md"
    _write(
        invocation,
        "---\ntype: playbook\ntitle: Probe\n---\n\n# Invocation: Probe\n\n"
        "Run `python3 ARCANA_HOME/rites/validate.py`.\n",
    )
    source = tmp_path / "skills" / "probe"
    _write(
        source / "SKILL.md",
        "---\nname: {{SKILL_PREFIX}}-probe\ndescription: probe\n---\n\n"
        "## Invocation\n\n!`cat " + invocation.as_posix() + "`\n\nDone.\n",
    )

    rendered = sync_skills.render_skill_files(_spec(source), pointer_only=True)
    body = rendered["SKILL.md"]

    assert "!`" not in body, body
    assert f"<!-- BEGIN INLINED: {invocation.as_posix()} -->" in body
    assert f"<!-- END INLINED: {invocation.as_posix()} -->" in body
    assert "# Invocation: Probe" in body
    # The inlined invocation's own frontmatter is dropped.
    assert "type: playbook" not in body
    # ARCANA_HOME/ becomes the concrete engine path, forward slashes everywhere.
    assert "ARCANA_HOME/" not in body
    assert f"{sync_skills.ARCANA_PATH.as_posix()}/rites/validate.py" in body
    assert "\\" not in sync_skills.ARCANA_PATH.as_posix()
    # Text after the directive survives in order.
    assert body.index("END INLINED") < body.index("Done.")


def test_render_inlines_quoted_directive_and_nested_files(tmp_path):
    inner = tmp_path / "inner.md"
    _write(inner, "INNER-TEXT\n")
    outer = tmp_path / "outer.md"
    _write(outer, "---\ntitle: Outer\n---\nOUTER-TEXT\n\n!`cat \"" + inner.as_posix() + "\"`\n")
    source = tmp_path / "skills" / "probe"
    _write(
        source / "SKILL.md",
        "---\nname: {{SKILL_PREFIX}}-probe\ndescription: probe\n---\n\n"
        "!`cat \"" + outer.as_posix() + "\"`\n",
    )

    body = sync_skills.render_skill_files(_spec(source), pointer_only=True)["SKILL.md"]

    assert "OUTER-TEXT" in body and "INNER-TEXT" in body
    assert "!`" not in body


def test_render_keeps_directive_and_warns_when_file_is_missing(tmp_path, capsys):
    missing = tmp_path / "nope.md"
    source = tmp_path / "skills" / "probe"
    _write(
        source / "SKILL.md",
        "---\nname: {{SKILL_PREFIX}}-probe\ndescription: probe\n---\n\n"
        "!`cat " + missing.as_posix() + "`\n",
    )

    body = sync_skills.render_skill_files(_spec(source), pointer_only=True)["SKILL.md"]

    assert "!`cat " + missing.as_posix() + "`" in body
    assert "cannot inline" in capsys.readouterr().out


def test_render_resolves_grimoire_path_before_inlining(tmp_path):
    grimoire = tmp_path / "cook-grimoire"
    playbook = grimoire / "chapters" / "ops" / "templates" / "playbook.md"
    _write(playbook, "PLAYBOOK-TEXT\n")
    source = grimoire / "skills" / "ops-run"
    _write(
        source / "SKILL.md",
        "---\nname: {{SKILL_PREFIX}}-ops-run\ndescription: run\n---\n\n"
        "!`cat {{GRIMOIRE_PATH}}/chapters/ops/templates/playbook.md`\n",
    )

    body = sync_skills.render_skill_files(
        _spec(source, grimoire_path=str(grimoire)), pointer_only=True
    )["SKILL.md"]

    assert "PLAYBOOK-TEXT" in body
    assert "!`" not in body


def test_every_shipped_skill_renders_without_a_directive():
    """The real catalog: every Arcana-shipped skill must come out self-contained."""
    specs = sync_skills.collect_arcana_skill_specs()
    assert specs, "no Arcana skills discovered"
    for spec in specs:
        body = sync_skills.render_skill_files(spec, pointer_only=True)["SKILL.md"]
        assert "!`" not in body, f"/{spec.command_name} still carries a dynamic-context directive"
        assert "{{ARCANA_PATH}}" not in body and "ARCANA_HOME/" not in body, f"/{spec.command_name}"
        assert body.count("\n") < 500, f"/{spec.command_name} exceeds the 500-line skill guidance"
