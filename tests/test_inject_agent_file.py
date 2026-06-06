"""Tests for the deterministic agent instruction-block injector.

Every case runs against a temp file so no test reads or writes the real `~`.
The canonical block text and sentinels are single-sourced from the rite, which
loads them from summon_core, so the fixtures cannot drift from the template.
"""

from pathlib import Path

import inject_agent_file as I

BEGIN = I.BEGIN_SENTINEL
END = I.END_SENTINEL
HEADING = I.HEADING_SENTINEL
CANON = I.canonical_marked_block()


# ---------------------------------------------------------------------------
# plan_block classification
# ---------------------------------------------------------------------------


def test_plan_absent_is_create():
    assert I.plan_block(None)[0] == "create"


def test_plan_blockless_is_insert():
    assert I.plan_block("# AGENTS\nsome personal notes\n")[0] == "insert"


def test_plan_canonical_region_is_present():
    content = f"# AGENTS\nintro\n{CANON}\ntail\n"
    assert I.plan_block(content)[0] == "present"


def test_plan_stale_marked_region_is_replace():
    content = f"# AGENTS\n{BEGIN}\nold body\n{END}\n"
    assert I.plan_block(content)[0] == "replace"


def test_plan_legacy_heading_only_is_present():
    assert I.plan_block(f"# AGENTS\n{HEADING}\nold body\n")[0] == "present"


def test_plan_duplicate_markers_is_ambiguous():
    content = f"{BEGIN}\na\n{END}\n{BEGIN}\nb\n{END}\n"
    assert I.plan_block(content)[0] == "ambiguous"


def test_plan_begin_without_end_is_ambiguous():
    assert I.plan_block(f"# AGENTS\n{BEGIN}\nbody but no end marker\n")[0] == "ambiguous"


# ---------------------------------------------------------------------------
# apply_block writes
# ---------------------------------------------------------------------------


def test_apply_creates_absent_file(tmp_path):
    target = tmp_path / "AGENTS.md"
    result = I.apply_block(target, "AGENTS", apply=True)
    assert result["action"] == "create" and result["status"] == "ok"
    content = target.read_text(encoding="utf-8")
    assert content.startswith("# AGENTS")
    assert content.count(BEGIN) == 1 and content.count(END) == 1


def test_apply_is_idempotent_on_rerun(tmp_path):
    target = tmp_path / "AGENTS.md"
    I.apply_block(target, "AGENTS", apply=True)
    first = target.read_text(encoding="utf-8")
    second = I.apply_block(target, "AGENTS", apply=True)
    assert second["action"] == "present" and second["status"] == "noop"
    assert target.read_text(encoding="utf-8") == first
    assert first.count(BEGIN) == 1


def test_apply_inserts_into_blockless_file(tmp_path):
    target = tmp_path / "CLAUDE.md"
    target.write_text("# CLAUDE\n\nmy own project rules\n", encoding="utf-8")
    result = I.apply_block(target, "CLAUDE", apply=True)
    assert result["action"] == "insert" and result["status"] == "ok"
    content = target.read_text(encoding="utf-8")
    assert content.count(BEGIN) == 1
    assert "my own project rules" in content  # user content preserved


def test_apply_refreshes_stale_region_and_preserves_surrounding(tmp_path):
    target = tmp_path / "CLAUDE.md"
    target.write_text(
        f"# CLAUDE\nintro line\n{BEGIN}\nstale body\n{END}\nmy own tail\n",
        encoding="utf-8",
    )
    result = I.apply_block(target, "CLAUDE", apply=True)
    assert result["action"] == "replace" and result["status"] == "ok"
    content = target.read_text(encoding="utf-8")
    assert CANON in content and "stale body" not in content
    assert "intro line" in content and "my own tail" in content
    assert content.count(BEGIN) == 1


def test_apply_skips_ambiguous_without_writing(tmp_path):
    target = tmp_path / "CLAUDE.md"
    original = f"{BEGIN}\na\n{END}\n{BEGIN}\nb\n{END}\n"
    target.write_text(original, encoding="utf-8")
    result = I.apply_block(target, "CLAUDE", apply=True)
    assert result["action"] == "ambiguous" and result["status"] == "skipped"
    assert target.read_text(encoding="utf-8") == original  # untouched


def test_plan_mode_writes_nothing(tmp_path):
    target = tmp_path / "AGENTS.md"
    result = I.apply_block(target, "AGENTS", apply=False)
    assert result["action"] == "create" and result["status"] == "planned"
    assert not target.exists()


def test_apply_writes_lf_and_utf8(tmp_path):
    target = tmp_path / "AGENTS.md"
    I.apply_block(target, "AGENTS", apply=True)
    raw = target.read_bytes()
    assert b"\r\n" not in raw  # LF only
    assert not raw.startswith(b"\xef\xbb\xbf")  # no BOM


# ---------------------------------------------------------------------------
# target resolution
# ---------------------------------------------------------------------------


def test_resolve_targets_filters_by_agent():
    root = Path(__file__).resolve().parent.parent
    all_targets = I.resolve_targets(root, "all")
    assert all_targets, "expected at least one automatic instruction target"
    one = I.resolve_targets(root, all_targets[0]["id"])
    assert len(one) == 1 and one[0]["id"] == all_targets[0]["id"]
    assert I.resolve_targets(root, "no-such-agent") == []
