"""Deterministic scaffolding for the invocation eval tier - runs in the fast gate.

These tests prove the eval harness works WITHOUT calling a model: specs are
well-formed and reference real invocations, scenarios materialize into
validate-clean grimoires, prompts assemble, the deterministic assertions and the
LLM-judge wiring behave, and the end-to-end run is driven by a fake seam. The
actual model-in-the-loop run lives in test_eval_live.py behind the `eval` marker.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

import eval_harness as H

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = H.load_specs()
SPEC_IDS = [s.eval_id for s in SPECS]


# ---------------------------------------------------------------------------
# Spec integrity
# ---------------------------------------------------------------------------


def test_specs_load_and_are_nonempty():
    assert SPECS, "no eval specs loaded"
    raw = json.loads(H.SPECS_PATH.read_text(encoding="utf-8"))
    assert raw["schema_version"] == H.SCHEMA_VERSION


def test_eval_ids_are_unique():
    assert len(SPEC_IDS) == len(set(SPEC_IDS))


@pytest.mark.parametrize("spec", SPECS, ids=SPEC_IDS)
def test_spec_has_required_fields(spec):
    assert spec.eval_id and spec.invocation and spec.grimoire_name
    assert spec.user_request and spec.decision_directive
    assert spec.scenario_files, "scenario has no files"
    # A non-vacuous eval asserts something - deterministically or via judge.
    assert spec.assertions or spec.judge_criteria


@pytest.mark.parametrize("spec", SPECS, ids=SPEC_IDS)
def test_invocation_under_test_exists(spec):
    assert (REPO_ROOT / spec.invocation).is_file(), f"missing playbook {spec.invocation}"


@pytest.mark.parametrize("spec", SPECS, ids=SPEC_IDS)
def test_judge_criteria_are_well_formed(spec):
    for c in spec.judge_criteria:
        assert {"id", "question", "pass_if", "fail_if"} <= set(c), f"bad criterion in {spec.eval_id}"


# ---------------------------------------------------------------------------
# Scenario materialization + clean background
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("spec", SPECS, ids=SPEC_IDS)
def test_scenario_materializes(spec, tmp_path):
    root = H.materialize(spec, tmp_path)
    assert (root / "grimoire.json").is_file()
    assert root.name == spec.grimoire_name


@pytest.mark.parametrize("spec", SPECS, ids=SPEC_IDS)
def test_scenario_background_matches_expectation(spec, tmp_path):
    """A fixture must be in exactly its intended state: clean, or failing only the
    declared validator codes - so an eval isolates judgment from incidental noise."""
    root = H.materialize(spec, tmp_path)
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "rites" / "validate.py"), "--grimoire", str(root), "--format", "json"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    if spec.expect_clean_background:
        assert result.returncode == 0, (
            f"{spec.eval_id} fixture is not validate-clean:\n{result.stdout[-1500:]}"
        )
    else:
        assert result.returncode != 0
        codes = {d.get("code") for line in result.stdout.splitlines() if line.strip()
                 for d in (json.loads(line).get("diagnostics", []) if line.strip().startswith("{") else [])}
        for expected in spec.expect_validator_codes:
            assert expected in codes


# ---------------------------------------------------------------------------
# Prompt assembly + decision parsing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("spec", SPECS, ids=SPEC_IDS)
def test_prompt_assembles(spec):
    prompt = H.assemble_prompt(spec)
    assert spec.user_request in prompt
    assert spec.decision_directive in prompt
    # The actual playbook text is embedded.
    assert "PLAYBOOK" in prompt and spec.invocation in prompt


def test_parse_decision_extracts_last_json_block():
    out = "blah\n```json\n{\"a\": 1}\n```\nmid\n```json\n{\"a\": 2}\n```\nend"
    assert H.parse_decision(out) == {"a": 2}


def test_parse_decision_returns_none_on_garbage():
    assert H.parse_decision("no json here") is None
    assert H.parse_decision("```json\nnot valid json\n```") is None


# ---------------------------------------------------------------------------
# Deterministic assertions
# ---------------------------------------------------------------------------


def test_check_assertion_list_any(tmp_path):
    decision = {"classifications": [{"file": "a_interview.txt", "layer": "source"}]}
    ok, _ = H.check_assertion(
        {"type": "list_any", "list": "classifications", "where": {"file__contains": "interview", "layer": "source"}},
        decision, tmp_path)
    assert ok
    bad, _ = H.check_assertion(
        {"type": "list_any", "list": "classifications", "where": {"file__contains": "interview", "layer": "junk"}},
        decision, tmp_path)
    assert not bad


def test_check_assertion_contains_all(tmp_path):
    decision = {"findings": [{"pages": ["chapters/protocols/storage.md", "chapters/protocols/handling.md"]}]}
    ok, _ = H.check_assertion(
        {"type": "list_any", "list": "findings",
         "where": {"pages__contains_all": ["protocols/storage", "protocols/handling"]}},
        decision, tmp_path)
    assert ok
    bad, _ = H.check_assertion(
        {"type": "list_any", "list": "findings",
         "where": {"pages__contains_all": ["protocols/storage", "protocols/missing"]}},
        decision, tmp_path)
    assert not bad


def test_check_assertion_field_in_and_equals(tmp_path):
    decision = {"type": "concept", "authority": "grimoire"}
    assert H.check_assertion({"type": "field_in", "field": "type", "values": ["concept", "entity"]}, decision, tmp_path)[0]
    assert H.check_assertion({"type": "field_equals", "field": "authority", "value": "grimoire"}, decision, tmp_path)[0]
    assert not H.check_assertion({"type": "field_equals", "field": "authority", "value": "external"}, decision, tmp_path)[0]


def test_check_assertion_contains_all_matches_per_element_not_join(tmp_path):
    """A needle is matched against single elements, so it cannot span the gap
    between two joined elements (the pre-hardening false-positive)."""
    pages = {"findings": [{"pages": ["chapters/protocols/storage.md", "chapters/protocols/handling.md"]}]}
    # Genuine: each needle matches its own element.
    assert H.check_assertion(
        {"type": "list_any", "list": "findings",
         "where": {"pages__contains_all": ["protocols/storage", "protocols/handling"]}},
        pages, tmp_path)[0]
    # A needle that only existed across the old space-join of two elements is rejected.
    assert not H.check_assertion(
        {"type": "list_any", "list": "findings",
         "where": {"pages__contains_all": ["storage.md chapters/protocols/handling"]}},
        pages, tmp_path)[0]


def test_check_assertion_glob_min(tmp_path):
    (tmp_path / "chapters" / "a").mkdir(parents=True)
    (tmp_path / "chapters" / "a" / "one.md").write_text("x")
    (tmp_path / "chapters" / "a" / "two.md").write_text("x")
    assert H.check_assertion({"type": "glob_min", "pattern": "chapters/**/*.md", "min": 2}, {}, tmp_path)[0]
    assert not H.check_assertion({"type": "glob_min", "pattern": "chapters/**/*.md", "min": 3}, {}, tmp_path)[0]


def test_check_assertion_file_existence(tmp_path):
    (tmp_path / "kept.txt").write_text("x")
    assert H.check_assertion({"type": "file_exists", "path": "kept.txt"}, {}, tmp_path)[0]
    assert H.check_assertion({"type": "file_absent", "path": "gone.txt"}, {}, tmp_path)[0]
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters" / "p.md").write_text("x")
    assert H.check_assertion(
        {"type": "file_from_decision_exists", "field": "page_path"},
        {"page_path": "chapters/p.md"}, tmp_path)[0]
    assert not H.check_assertion(
        {"type": "file_from_decision_exists", "field": "page_path"},
        {"page_path": "chapters/missing.md"}, tmp_path)[0]


def test_check_assertion_none_decision_fails(tmp_path):
    ok, detail = H.check_assertion({"type": "list_any", "list": "x", "where": {}}, None, tmp_path)
    assert not ok and "no decision" in detail


# ---------------------------------------------------------------------------
# LLM judge wiring (fake seam, no model)
# ---------------------------------------------------------------------------


def test_run_judge_passes_with_evidence():
    crit = {"id": "c", "question": "q", "pass_if": "p", "fail_if": "f"}
    seam = H.fake_seam('```json\n{"verdict":"pass","evidence_quote":"the proof","reason":"r"}\n```')
    passed, rec = H.run_judge(crit, "agent output", seam, ".")
    assert passed and rec["criterion_id"] == "c"


def test_run_judge_fails_without_evidence_or_on_fail_verdict():
    crit = {"id": "c", "question": "q", "pass_if": "p", "fail_if": "f"}
    no_ev = H.fake_seam('```json\n{"verdict":"pass","evidence_quote":"","reason":"r"}\n```')
    assert not H.run_judge(crit, "x", no_ev, ".")[0]
    failed = H.fake_seam('```json\n{"verdict":"fail","evidence_quote":"q","reason":"r"}\n```')
    assert not H.run_judge(crit, "x", failed, ".")[0]


# ---------------------------------------------------------------------------
# Default seam refuses without the opt-in env var
# ---------------------------------------------------------------------------


def test_claude_seam_refuses_without_env(monkeypatch):
    monkeypatch.delenv(H.ARCANA_EVAL_MODEL, raising=False)
    with pytest.raises(RuntimeError):
        H.claude_cli_seam("prompt", ".")


# ---------------------------------------------------------------------------
# End-to-end run_one_eval driven by a fake seam
# ---------------------------------------------------------------------------


def _ingest_spec():
    return next(s for s in SPECS if s.eval_id == "ingest_layer_classification")


def test_run_one_eval_passes_on_correct_fake(tmp_path):
    spec = _ingest_spec()
    decision = {"classifications": [
        {"file": "interview_chef.txt", "layer": "source"},
        {"file": "braising_notes.md", "layer": "chapter"},
        {"file": "scratch.tmp", "layer": "junk"}]}

    def correct_agent(prompt, cwd):
        # Simulate a correct ingest: promote the draft (move it out of inbox into
        # a new chapter page) and leave the junk in place.
        root = Path(cwd)
        (root / "inbox" / "braising_notes.md").unlink()
        (root / "chapters" / "recipes" / "braising.md").write_text(
            "---\ntype: concept\ntitle: Braising\naliases: []\n"
            "tags: [grimoire/cook, type/concept]\nauthority: grimoire\n"
            "last_verified: 2026-06-01\n---\n\nBraising sears then simmers.\n",
            encoding="utf-8")
        return "```json\n" + json.dumps(decision) + "\n```"

    result = H.run_one_eval(spec, tmp_path, correct_agent)
    assert result.outcome == "pass", result.to_dict()


def test_run_one_eval_fails_when_agent_deletes_junk(tmp_path):
    """The junk-not-deleted disk invariant must fail an agent that removes junk."""
    spec = _ingest_spec()
    decision = {"classifications": [
        {"file": "interview_chef.txt", "layer": "source"},
        {"file": "braising_notes.md", "layer": "chapter"},
        {"file": "scratch.tmp", "layer": "junk"}]}

    def deletes_junk(prompt, cwd):
        root = Path(cwd)
        (root / "inbox" / "braising_notes.md").unlink()
        (root / "chapters" / "recipes" / "braising.md").write_text("x", encoding="utf-8")
        (root / "inbox" / "scratch.tmp").unlink()  # WRONG: never auto-delete junk
        return "```json\n" + json.dumps(decision) + "\n```"

    assert H.run_one_eval(spec, tmp_path, deletes_junk).outcome == "fail"


def test_run_one_eval_fails_on_wrong_fake(tmp_path):
    spec = _ingest_spec()
    decision = {"classifications": [
        {"file": "interview_chef.txt", "layer": "junk"},  # wrong
        {"file": "braising_notes.md", "layer": "chapter"},
        {"file": "scratch.tmp", "layer": "junk"}]}
    seam = H.fake_seam("```json\n" + json.dumps(decision) + "\n```")
    assert H.run_one_eval(spec, tmp_path, seam).outcome == "fail"


def test_run_one_eval_errors_on_seam_failure(tmp_path):
    def boom(prompt, cwd):
        raise RuntimeError("no model available")
    assert H.run_one_eval(_ingest_spec(), tmp_path, boom).outcome == "error"


def test_suite_report_shape():
    report = H.suite_report([], mode="dry-run", root="x")
    assert report["rite"] == "invocation_evals"
    assert set(report["summary"]) == {"total", "passed", "failed", "errors"}
    assert report["schema_version"] == H.SCHEMA_VERSION
