"""Tests for the branch-aware, pull-before-heal grimoire update rite.

The git seam, heal, and re-validate subprocesses are injected so the suite stays
offline and deterministic. The load-bearing property under test is the
heal-eligibility gate: a grimoire that could not be brought current is never
validated-and-modified.
"""

from pathlib import Path

import pytest

import summon_core
import summon_state as S
import update_grimoires as U

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Fake git seam: map a git subcommand (by a distinguishing arg substring) to
# its (returncode, stdout, stderr). Anything unspecified returns success/empty.
# ---------------------------------------------------------------------------


def make_git(responses):
    def git(*args, cwd=None):
        argstr = " ".join(str(a) for a in args)
        for key, resp in responses.items():
            if key in argstr:
                return resp
        return (0, "", "")
    return git


_UP_TO_DATE = {
    "symbolic-ref": (0, "main", ""),
    "rev-parse --abbrev-ref": (0, "origin/main", ""),
    "status --porcelain": (0, "", ""),
    "fetch": (0, "", ""),
    "rev-list": (0, "0\t0", ""),
}


def _git(**overrides):
    table = dict(_UP_TO_DATE)
    table.update(overrides)
    return make_git(table)


def _repo(tmp_path, name="g"):
    d = tmp_path / name
    (d / ".git").mkdir(parents=True)
    return d


# ---------------------------------------------------------------------------
# git_capture seam (the only new primitive) + error classification
# ---------------------------------------------------------------------------


def test_git_capture_returns_three_tuple():
    rc, out, err = summon_core.git_capture("--version")
    assert rc == 0
    assert "git version" in out
    assert isinstance(err, str)


@pytest.mark.parametrize("stderr,expected", [
    ("remote: HTTP 403 ... The requested URL returned error: 403", "auth_failed"),
    ("remote: insufficient_scope", "auth_failed"),
    ("fatal: Authentication failed for 'https://host/x.git'", "auth_failed"),
    ("fatal: unable to access 'https://h/': Could not resolve host: h", "offline"),
    ("ssh: connect to host h port 22: Connection timed out", "offline"),
    ("fatal: something unexpected went wrong", "fetch_error"),
])
def test_classify_fetch_error(stderr, expected):
    assert U.classify_fetch_error(stderr) == expected


# ---------------------------------------------------------------------------
# Classification ladder
# ---------------------------------------------------------------------------


def test_missing_local_and_not_a_repo(tmp_path):
    missing = U.classify_grimoire(tmp_path / "nope", fetch=True, git=_git())
    assert missing["status"] == "missing_local"
    plain = tmp_path / "plain"
    plain.mkdir()
    assert U.classify_grimoire(plain, fetch=True, git=_git())["status"] == "not_a_repo"


def test_detached_and_no_upstream(tmp_path):
    d = _repo(tmp_path)
    assert U.classify_grimoire(d, fetch=True, git=_git(**{"symbolic-ref": (1, "", "")}))["status"] == "detached"
    no_up = U.classify_grimoire(d, fetch=True, git=_git(**{"rev-parse --abbrev-ref": (1, "", "no upstream")}))
    assert no_up["status"] == "no_upstream"


def test_dirty_tree_skips_before_fetch(tmp_path):
    d = _repo(tmp_path)
    rec = U.classify_grimoire(d, fetch=True, git=_git(**{"status --porcelain": (0, " M README.md", "")}))
    assert rec["status"] == "dirty"


@pytest.mark.parametrize("revlist,status,behind,ahead", [
    ("0\t0", "up_to_date", 0, 0),
    ("3\t0", "behind", 3, 0),
    ("0\t2", "ahead", 0, 2),
    ("2\t3", "diverged", 2, 3),
])
def test_ahead_behind_classification(tmp_path, revlist, status, behind, ahead):
    d = _repo(tmp_path)
    rec = U.classify_grimoire(d, fetch=True, git=_git(**{"rev-list": (0, revlist, "")}))
    assert rec["status"] == status
    assert rec["behind"] == behind and rec["ahead"] == ahead


def test_auth_failed_sets_creds_present(tmp_path):
    d = _repo(tmp_path)
    git = _git(**{"fetch": (1, "", "remote: HTTP 403 insufficient_scope")})
    rec = U.classify_grimoire(d, fetch=True, git=git, credential_probe=lambda host: "", host="gitlab.example")
    assert rec["status"] == "auth_failed"
    assert rec["creds_present"] is False


def test_fetch_false_is_offline(tmp_path):
    d = _repo(tmp_path)
    calls = []

    def git(*args, cwd=None):
        calls.append(args)  # token tuple, not a joined string (the tmp path contains "fetch")
        argstr = " ".join(str(a) for a in args)
        return _UP_TO_DATE.get(next((k for k in _UP_TO_DATE if k in argstr), ""), (0, "0\t0", ""))

    U.classify_grimoire(d, fetch=False, git=git)
    assert not any("fetch" in args for args in calls)  # no network when fetch=False


# ---------------------------------------------------------------------------
# Fast-forward
# ---------------------------------------------------------------------------


def test_bring_current_fast_forwards(tmp_path):
    d = _repo(tmp_path)
    rec = {"status": "behind", "behind": 3}
    U.bring_current(d, rec, git=_git(**{"pull --ff-only": (0, "", "")}))
    assert rec["status"] == "fast_forwarded" and rec["behind"] == 0


def test_bring_current_blocked(tmp_path):
    d = _repo(tmp_path)
    rec = {"status": "behind", "behind": 3}
    U.bring_current(d, rec, git=_git(**{"pull --ff-only": (1, "", "fatal: Not possible to fast-forward")}))
    assert rec["status"] == "behind_blocked"


# ---------------------------------------------------------------------------
# The heal-eligibility gate (the load-bearing invariant)
# ---------------------------------------------------------------------------


class HealSpy:
    def __init__(self):
        self.calls = []

    def __call__(self, local_path, arcana_root):
        self.calls.append(str(local_path))
        return {"status": "ok", "scaffold_synced": [], "readme_block": "unchanged", "messages": []}


def _process(tmp_path, git, *, apply, heal):
    d = _repo(tmp_path)
    entry = {"local_path": str(d), "online_path": "https://h/g.git"}
    return U.process_grimoire("g", entry, REPO_ROOT, apply=apply, git=git,
                              heal_fn=heal, revalidate_fn=lambda a, l: (True, "ok"))


def test_heal_runs_only_for_current_grimoire(tmp_path):
    heal = HealSpy()
    rec = _process(tmp_path, _git(), apply=True, heal=heal)  # up_to_date
    assert rec["heal_eligible"] is True
    assert heal.calls == [rec["local_path"]]


@pytest.mark.parametrize("override,status", [
    ({"status --porcelain": (0, " M x", "")}, "dirty"),
    ({"rev-list": (0, "2\t3", "")}, "diverged"),
    ({"symbolic-ref": (1, "", "")}, "detached"),
    ({"fetch": (1, "", "Could not resolve host: h")}, "offline"),
])
def test_heal_never_runs_for_non_current(tmp_path, override, status):
    heal = HealSpy()
    rec = _process(tmp_path, _git(**override), apply=True, heal=heal)
    assert rec["status"] == status
    assert rec["heal_eligible"] is False
    assert heal.calls == []  # the bug under repair: never modify a stale tree


def test_plan_mode_never_heals(tmp_path):
    heal = HealSpy()
    rec = _process(tmp_path, _git(), apply=False, heal=heal)  # up_to_date but plan
    assert rec["heal_eligible"] is True
    assert heal.calls == []
    assert rec["heal"]["status"] == "planned"


def test_behind_is_pulled_then_healed(tmp_path):
    heal = HealSpy()
    git = _git(**{"rev-list": (0, "3\t0", ""), "pull --ff-only": (0, "", "")})
    rec = _process(tmp_path, git, apply=True, heal=heal)
    assert rec["status"] == "fast_forwarded" and rec["pulled"] is True
    assert heal.calls == [rec["local_path"]]


# ---------------------------------------------------------------------------
# Library-wide processing + manual-pull fallback
# ---------------------------------------------------------------------------


def test_process_all_summary_and_needs_manual_pull(tmp_path):
    a = _repo(tmp_path, "a-grimoire")
    b = _repo(tmp_path, "b-grimoire")
    library = {"grimoires": {
        "a-grimoire": {"local_path": str(a), "online_path": "https://pub/a.git"},
        "b-grimoire": {"local_path": str(b), "online_path": "https://private/b.git"},
    }}

    def git(*args, cwd=None):
        argstr = " ".join(str(x) for x in args)
        if str(b) in argstr and "fetch" in argstr:
            return (1, "", "remote: HTTP 403 insufficient_scope")
        for key, resp in _UP_TO_DATE.items():
            if key in argstr:
                return resp
        return (0, "", "")

    result = U.process_all(tmp_path, REPO_ROOT, apply=True, library=library, git=git,
                           heal_fn=HealSpy(), revalidate_fn=lambda a, l: (True, "ok"))
    s = result["summary"]
    assert s["total"] == 2
    assert s["already_current"] == 1          # a is up_to_date
    assert s["needs_manual_pull"] == 1        # b auth_failed
    assert [n["key"] for n in result["needs_manual_pull"]] == ["b-grimoire"]
    assert result["needs_manual_pull"][0]["status"] == "auth_failed"
    assert result["needs_manual_pull"][0]["suggested_command"].startswith("git -C")


# ---------------------------------------------------------------------------
# README update-block injector (deterministic v1.2.0 migration)
# ---------------------------------------------------------------------------


BLOCK = "<!-- BEGIN ARCANA UPDATE -->\n## Out of date? Update.\nbody\n<!-- END ARCANA UPDATE -->"


def _write(tmp_path, text):
    p = tmp_path / "README.md"
    p.write_text(text, encoding="utf-8")
    return p


def test_injector_inserts_before_first_heading(tmp_path):
    p = _write(tmp_path, "# G\n\nintro\n\n## Installation\n\nsteps\n")
    assert U.inject_update_readme_block(p, BLOCK) is True
    out = p.read_text(encoding="utf-8")
    assert out.count(U.UPDATE_BEGIN) == 1
    assert out.index(U.UPDATE_BEGIN) < out.index("## Installation")


def test_injector_is_idempotent(tmp_path):
    p = _write(tmp_path, "# G\n\nintro\n\n## Installation\n")
    U.inject_update_readme_block(p, BLOCK)
    once = p.read_text(encoding="utf-8")
    assert U.inject_update_readme_block(p, BLOCK) is False
    assert p.read_text(encoding="utf-8") == once


def test_injector_replaces_block_in_place(tmp_path):
    p = _write(tmp_path, f"# G\n\nintro\n\n{U.UPDATE_BEGIN}\nstale body\n{U.UPDATE_END}\n\n## Installation\n")
    assert U.inject_update_readme_block(p, BLOCK) is True
    out = p.read_text(encoding="utf-8")
    assert out.count(U.UPDATE_BEGIN) == 1
    assert "stale body" not in out


# ---------------------------------------------------------------------------
# Orchestration: reconcile(pull_grimoires=True) runs grimoires before skills
# ---------------------------------------------------------------------------


def test_reconcile_runs_grimoire_step_before_skills(tmp_path):
    home = tmp_path / "grimoires"
    home.mkdir()
    order = []

    def fake_processor(h, a, *, apply, fetch):
        order.append("grimoires")
        return {"grimoires": [], "needs_manual_pull": [],
                "summary": {"total": 0, "already_current": 0, "brought_current": 0,
                            "ahead": 0, "healed": 0, "heal_skipped": 0, "needs_manual_pull": 0}}

    def fake_skill_runner(script):
        order.append("skills")
        return (0, "ok")

    result = S.reconcile(
        home, REPO_ROOT, apply=True, pull_grimoires=True,
        instruction_targets=[], skill_targets=[],
        git_fn=lambda *a, **k: (False, ""),
        skill_runner=fake_skill_runner,
        validate_runner=lambda r: (True, "ok"),
        grimoire_processor=fake_processor,
    )
    assert order == ["grimoires", "skills"]            # pull before re-register
    assert result["grimoires"] is not None
    assert any(step["id"] == "grimoires" for step in result["steps"])
