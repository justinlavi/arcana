"""Tests for the agent-legible summon state surface (summon_state.py).

Every entry point is exercised against a temp grimoires home with the
instruction/skill targets injected as explicit lists, so no test ever reads or
writes the real `~`. The git, skill-registration, and validator subprocesses are
injected too, so the suite stays fully offline.
"""

import json
import types
from pathlib import Path

import pytest

import summon_state as S

REPO_ROOT = Path(__file__).resolve().parent.parent

NO_GIT = lambda *a, **k: (False, "")
OK_VALIDATE = lambda root: (True, "ok")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_home(tmp_path, *, with_grimoire=True):
    home = tmp_path / "grimoires"
    home.mkdir()
    if with_grimoire:
        g = home / "cooking-grimoire"
        g.mkdir()
        (g / "grimoire.json").write_text(
            json.dumps({"name": "cooking-grimoire", "skill_prefix": "cook"}),
            encoding="utf-8",
        )
    return home


def _instruction_targets(tmp_path, content=None):
    path = tmp_path / "CLAUDE.md"
    if content is not None:
        path.write_text(content, encoding="utf-8")
    return [{"id": "claude", "label": "Claude", "path": str(path)}]


def _skill_targets(tmp_path, registered=0):
    skills = tmp_path / ".claude" / "skills"
    skills.mkdir(parents=True)
    for i in range(registered):
        d = skills / f"arc-skill-{i}"
        d.mkdir()
        (d / "SKILL.md").write_text("ARCANA_SKILL_OWNERSHIP\n", encoding="utf-8")
    return [{"id": "claude", "label": "Claude", "path": str(skills)}]


def _inspect(tmp_path, *, home=None, arcana_root=REPO_ROOT, block=None, registered=0):
    return S.inspect_install(
        home or _make_home(tmp_path),
        arcana_root,
        instruction_targets=_instruction_targets(tmp_path, block),
        skill_targets=_skill_targets(tmp_path, registered),
        git_fn=NO_GIT,
    )


# ---------------------------------------------------------------------------
# inspect_install
# ---------------------------------------------------------------------------


def test_inspect_reports_library_drift_against_disk(tmp_path):
    state = _inspect(tmp_path, registered=1)
    assert state["library"]["in_sync"] is False
    assert "cooking-grimoire" in state["library"]["missing"]
    assert state["arcana"]["working_tree_populated"] is True  # real Arcana checkout


def test_inspect_in_sync_when_library_matches_disk(tmp_path):
    home = _make_home(tmp_path, with_grimoire=False)
    state = S.inspect_install(
        home, REPO_ROOT,
        instruction_targets=_instruction_targets(tmp_path, S.HEADING_SENTINEL),
        skill_targets=_skill_targets(tmp_path, registered=2),
        git_fn=NO_GIT,
    )
    assert state["library"]["in_sync"] is True
    assert S.drift_detected(state) is False


@pytest.mark.parametrize(
    "content,expected",
    [
        ("just a file\n", "none"),
        (f"# Title\n{S.HEADING_SENTINEL}\n", "heading"),
        (f"# Title\n{S.BEGIN_SENTINEL}\n...\n", "markers"),
        (f"{S.HEADING_SENTINEL}\n{S.BEGIN_SENTINEL}\n", "both"),
    ],
)
def test_inspect_detects_both_block_sentinels(tmp_path, content, expected):
    state = _inspect(tmp_path, block=content, registered=1)
    target = state["agent_targets"][0]
    assert target["block_marker"] == expected
    assert target["block_present"] is (expected != "none")


def test_block_present_via_markers_is_not_drift(tmp_path):
    """A block written with BEGIN/END markers must not be flagged as missing."""
    home = _make_home(tmp_path, with_grimoire=False)
    state = S.inspect_install(
        home, REPO_ROOT,
        instruction_targets=_instruction_targets(tmp_path, S.BEGIN_SENTINEL),
        skill_targets=_skill_targets(tmp_path, registered=1),
        git_fn=NO_GIT,
    )
    assert state["agent_targets"][0]["block_marker"] == "markers"
    assert S._missing_block_ids(state) == []
    assert S.drift_detected(state) is False


def test_inspect_counts_registered_skills(tmp_path):
    state = _inspect(tmp_path, registered=3)
    assert state["skills"][0]["arcana_managed_count"] == 3


def test_inspect_network_pull_is_human_gated(tmp_path):
    state = _inspect(tmp_path)
    assert "UPDATE.md step 2" in state["network_pull"]


# ---------------------------------------------------------------------------
# next_actions / residual
# ---------------------------------------------------------------------------


def test_next_actions_are_tier_tagged(tmp_path):
    state = _inspect(tmp_path, block="none", registered=0)
    actions = S.next_actions(state, REPO_ROOT)
    kinds = {a["kind"]: a["tier"] for a in actions}
    assert kinds["library_reconcile"] == "amber"
    assert kinds["agent_block_update"] == "amber"
    assert kinds["skill_sync"] == "amber"
    for a in actions:
        assert a["command"] and a["reason"]


def test_stale_entry_is_red_tier_prune_action(tmp_path):
    home = _make_home(tmp_path, with_grimoire=False)
    (home / "library.json").write_text(
        json.dumps({"grimoires": {"ghost": {"local_path": str(home / "ghost"), "online_path": ""}}}),
        encoding="utf-8",
    )
    state = S.inspect_install(
        home, REPO_ROOT,
        instruction_targets=_instruction_targets(tmp_path, S.HEADING_SENTINEL),
        skill_targets=_skill_targets(tmp_path, registered=1),
        git_fn=NO_GIT,
    )
    assert [s["key"] for s in state["library"]["stale"]] == ["ghost"]
    prune_action = next(a for a in S.next_actions(state, REPO_ROOT) if a["kind"] == "library_prune")
    assert prune_action["tier"] == "red"
    res = S.residual(state, prune=False)
    assert any(r["kind"] == "library_stale" for r in res)
    assert S.residual(state, prune=True) == [] or all(
        r["kind"] != "library_stale" for r in S.residual(state, prune=True)
    )


# ---------------------------------------------------------------------------
# reconcile - plan
# ---------------------------------------------------------------------------


def test_reconcile_plan_makes_no_writes(tmp_path):
    home = _make_home(tmp_path)
    out = S.reconcile(
        home, REPO_ROOT, apply=False,
        instruction_targets=_instruction_targets(tmp_path, "none"),
        skill_targets=_skill_targets(tmp_path, 0),
        git_fn=NO_GIT,
    )
    assert not (home / "library.json").exists()
    lib_step = next(s for s in out["steps"] if s["id"] == "library")
    assert lib_step["status"] == "drift"
    assert lib_step["mutations"] == []


# ---------------------------------------------------------------------------
# reconcile - apply
# ---------------------------------------------------------------------------


def test_reconcile_apply_writes_library_and_registers_skills(tmp_path):
    home = _make_home(tmp_path)
    calls = []
    out = S.reconcile(
        home, REPO_ROOT, apply=True,
        instruction_targets=_instruction_targets(tmp_path, S.HEADING_SENTINEL),
        skill_targets=_skill_targets(tmp_path, 0),
        git_fn=NO_GIT,
        skill_runner=lambda script: (calls.append(script) or (0, "Registered: 3")),
        validate_runner=OK_VALIDATE,
    )
    assert (home / "library.json").is_file()
    lib = json.loads((home / "library.json").read_text())
    assert "cooking-grimoire" in lib["grimoires"]
    assert len(calls) == 1
    assert out["reporter"].status() == "ok"
    skill_step = next(s for s in out["steps"] if s["id"] == "skills")
    assert skill_step["status"] == "ok"


def test_reconcile_apply_preserves_stale_without_prune(tmp_path):
    home = _make_home(tmp_path)
    (home / "library.json").write_text(
        json.dumps({"grimoires": {"ghost": {"local_path": str(home / "ghost"), "online_path": ""}}}),
        encoding="utf-8",
    )
    S.reconcile(
        home, REPO_ROOT, apply=True, prune=False,
        instruction_targets=_instruction_targets(tmp_path, S.HEADING_SENTINEL),
        skill_targets=_skill_targets(tmp_path, 1),
        git_fn=NO_GIT,
        skill_runner=lambda script: (0, ""),
        validate_runner=OK_VALIDATE,
    )
    lib = json.loads((home / "library.json").read_text())
    assert "ghost" in lib["grimoires"]  # stale entry NOT deleted
    assert "cooking-grimoire" in lib["grimoires"]  # missing entry added


def test_reconcile_apply_prune_removes_stale(tmp_path):
    home = _make_home(tmp_path)
    (home / "library.json").write_text(
        json.dumps({"grimoires": {"ghost": {"local_path": str(home / "ghost"), "online_path": ""}}}),
        encoding="utf-8",
    )
    out = S.reconcile(
        home, REPO_ROOT, apply=True, prune=True,
        instruction_targets=_instruction_targets(tmp_path, S.HEADING_SENTINEL),
        skill_targets=_skill_targets(tmp_path, 1),
        git_fn=NO_GIT,
        skill_runner=lambda script: (0, ""),
        validate_runner=OK_VALIDATE,
    )
    lib = json.loads((home / "library.json").read_text())
    assert "ghost" not in lib["grimoires"]  # pruned
    removals = [m for m in out["reporter"].mutations if m["action"] == "remove"]
    assert any("ghost" in (m["detail"] or "") for m in removals)


def test_reconcile_apply_blocked_on_broken_base(tmp_path):
    home = _make_home(tmp_path)
    out = S.reconcile(
        home, REPO_ROOT, apply=True,
        instruction_targets=_instruction_targets(tmp_path, S.HEADING_SENTINEL),
        skill_targets=_skill_targets(tmp_path, 0),
        git_fn=NO_GIT,
        skill_runner=lambda script: (0, ""),
        validate_runner=lambda root: (False, "FAILED validators"),
    )
    assert out["reporter"].status() == "blocked"
    assert not (home / "library.json").exists()  # refused to write on a red base
    assert out["steps"][0]["id"] == "validate"
    assert out["steps"][0]["status"] == "blocked"


def test_reconcile_apply_partial_failure_degrades_status(tmp_path):
    home = _make_home(tmp_path)
    out = S.reconcile(
        home, REPO_ROOT, apply=True,
        instruction_targets=_instruction_targets(tmp_path, S.HEADING_SENTINEL),
        skill_targets=_skill_targets(tmp_path, 0),
        git_fn=NO_GIT,
        skill_runner=lambda script: (1, "collision"),  # skills fail
        validate_runner=OK_VALIDATE,
    )
    # library write still happened, but skills failed -> overall error
    assert (home / "library.json").is_file()
    assert out["reporter"].status() == "error"
    skill_step = next(s for s in out["steps"] if s["id"] == "skills")
    assert skill_step["status"] == "error"


# ---------------------------------------------------------------------------
# transcript
# ---------------------------------------------------------------------------


def test_transcript_is_envelope_superset_without_nesting(tmp_path):
    state = _inspect(tmp_path)
    from diagnostics import ResultReporter
    reporter = ResultReporter("summon", root=tmp_path, mode="plan")
    summary = S.build_summary(
        state, operation="check", drift=True,
        res=[], actions=S.next_actions(state, REPO_ROOT),
    )
    t = S.build_transcript(
        reporter, operation="check", state=state, steps=[], summary=summary,
        run_id="rid", started_at="t0", ended_at="t1",
    )
    # envelope keys present at top level (superset), no nested "result"
    for key in ("rite", "status", "mode", "root", "summary", "mutations", "messages"):
        assert key in t
    assert "result" not in t
    assert t["schema_version"] == S.SCHEMA_VERSION
    assert t["operation"] == "check" and t["run_id"] == "rid"
    assert t["final_state"] is state


def test_write_transcript_roundtrips_atomically(tmp_path):
    path = tmp_path / "cache" / "summon-last.json"
    S.write_transcript(path, {"rite": "summon", "schema_version": 1})
    assert json.loads(path.read_text())["rite"] == "summon"


# ---------------------------------------------------------------------------
# run_state_command
# ---------------------------------------------------------------------------


def _args(**kw):
    base = dict(check=False, reconcile=False, apply=False, prune=False,
                home=None, arcana_root=str(REPO_ROOT), format="json")
    base.update(kw)
    return types.SimpleNamespace(**base)


def test_run_check_exits_1_on_drift_and_writes_transcript(tmp_path, capsys):
    home = _make_home(tmp_path)
    tp = tmp_path / "summon-last.json"
    rc = S.run_state_command(
        _args(check=True, home=str(home)),
        transcript_path=tp,
        instruction_targets=_instruction_targets(tmp_path, "none"),
        skill_targets=_skill_targets(tmp_path, 0),
        git_fn=NO_GIT,
        now=lambda: "2026-06-01T00:00:00+00:00", run_id="rid",
    )
    assert rc == 1
    env = json.loads(capsys.readouterr().out)
    assert env["rite"] == "summon" and env["summary"]["drift"] is True
    assert env["summary"]["schema_version"] == S.SCHEMA_VERSION
    t = json.loads(tp.read_text())
    assert t["operation"] == "check" and t["run_id"] == "rid"


def test_run_check_exits_0_when_clean(tmp_path, capsys):
    home = _make_home(tmp_path, with_grimoire=False)
    rc = S.run_state_command(
        _args(check=True, home=str(home)),
        transcript_path=tmp_path / "t.json",
        instruction_targets=_instruction_targets(tmp_path, S.HEADING_SENTINEL),
        skill_targets=_skill_targets(tmp_path, 2),
        git_fn=NO_GIT,
        now=lambda: "t", run_id="rid",
    )
    assert rc == 0


def test_run_reconcile_apply_converges_to_exit_0(tmp_path, capsys):
    home = _make_home(tmp_path)
    rc = S.run_state_command(
        _args(reconcile=True, apply=True, home=str(home)),
        transcript_path=tmp_path / "t.json",
        instruction_targets=_instruction_targets(tmp_path, S.HEADING_SENTINEL),
        skill_targets=_skill_targets(tmp_path, 1),
        git_fn=NO_GIT,
        skill_runner=lambda script: (0, ""),
        validate_runner=OK_VALIDATE,
        now=lambda: "t", run_id="rid",
    )
    capsys.readouterr()
    assert rc == 0
    assert (home / "library.json").is_file()


def test_run_reconcile_apply_blocked_exits_1(tmp_path, capsys):
    home = _make_home(tmp_path)
    rc = S.run_state_command(
        _args(reconcile=True, apply=True, home=str(home)),
        transcript_path=tmp_path / "t.json",
        instruction_targets=_instruction_targets(tmp_path, S.HEADING_SENTINEL),
        skill_targets=_skill_targets(tmp_path, 0),
        git_fn=NO_GIT,
        skill_runner=lambda script: (0, ""),
        validate_runner=lambda root: (False, "red"),
        now=lambda: "t", run_id="rid",
    )
    capsys.readouterr()
    assert rc == 1


def test_run_reconcile_plan_exits_1_on_drift(tmp_path, capsys):
    """--reconcile without --apply (propose) signals fixable drift via exit code."""
    home = _make_home(tmp_path)  # on-disk grimoire missing from library -> fixable drift
    rc = S.run_state_command(
        _args(reconcile=True, apply=False, home=str(home)),
        transcript_path=tmp_path / "t.json",
        instruction_targets=_instruction_targets(tmp_path, S.HEADING_SENTINEL),
        skill_targets=_skill_targets(tmp_path, 1),
        git_fn=NO_GIT,
        now=lambda: "t", run_id="rid",
    )
    capsys.readouterr()
    assert rc == 1  # drift, even though no residual and no writes
    assert not (home / "library.json").exists()


def test_transcript_path_arg_overrides_default(tmp_path, capsys):
    home = _make_home(tmp_path)
    tp = tmp_path / "elsewhere" / "mine.json"
    S.run_state_command(
        _args(check=True, home=str(home), transcript_path=str(tp)),
        instruction_targets=_instruction_targets(tmp_path, S.HEADING_SENTINEL),
        skill_targets=_skill_targets(tmp_path, 1),
        git_fn=NO_GIT,
        now=lambda: "t", run_id="rid",
    )
    capsys.readouterr()
    assert tp.is_file()  # honored args.transcript_path, not the ~/.cache default


def test_reconcile_library_never_deletes_without_prune_even_if_diff_stale_desyncs(tmp_path):
    """Structural guarantee: any dropped key is re-added when not pruning,
    independent of the passed-in stale list."""
    from diagnostics import ResultReporter
    home = _make_home(tmp_path)  # cooking-grimoire on disk, absent from library
    (home / "library.json").write_text(
        json.dumps({"grimoires": {"ghost": {"local_path": str(home / "ghost"), "online_path": ""}}}),
        encoding="utf-8",
    )
    reporter = ResultReporter("summon", root=home, mode="apply")
    # Desynced diff: a write is triggered by `missing`, but the stale `ghost`
    # entry is (wrongly) absent from the stale list. The structural re-add must
    # still preserve it.
    desynced_diff = {"missing": ["cooking-grimoire"], "mismatched": [], "stale": []}
    S._reconcile_library(home, desynced_diff, apply=True, prune=False, reporter=reporter)
    lib = json.loads((home / "library.json").read_text())
    assert "ghost" in lib["grimoires"]  # preserved despite the desynced stale list
    assert "cooking-grimoire" in lib["grimoires"]  # the genuine change still applied


def test_is_state_invocation(tmp_path):
    assert S.is_state_invocation(_args(check=True)) is True
    assert S.is_state_invocation(_args(reconcile=True)) is True
    assert S.is_state_invocation(_args()) is False


# ---------------------------------------------------------------------------
# record_install_transcript
# ---------------------------------------------------------------------------


def test_record_install_transcript_writes_install_operation(tmp_path):
    home = _make_home(tmp_path)
    tp = tmp_path / "summon-last.json"
    t = S.record_install_transcript(
        home, REPO_ROOT, ["cooking-grimoire"], True,
        transcript_path=tp, git_fn=NO_GIT,
        now=lambda: "2026-06-01T00:00:00+00:00", run_id="rid",
    )
    assert t["operation"] == "install"
    assert t["status"] == "ok"
    on_disk = json.loads(tp.read_text())
    assert on_disk["operation"] == "install"
    grim_step = next(s for s in on_disk["steps"] if s["id"] == "grimoires")
    assert any(m["path"] == "cooking-grimoire" for m in grim_step["mutations"])


def test_record_install_transcript_marks_skill_failure(tmp_path):
    home = _make_home(tmp_path)
    tp = tmp_path / "summon-last.json"
    t = S.record_install_transcript(
        home, REPO_ROOT, [], False,
        transcript_path=tp, git_fn=NO_GIT,
        now=lambda: "t", run_id="rid",
    )
    assert t["status"] == "error"
