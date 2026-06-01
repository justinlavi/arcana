"""Harness for the invocation eval tier - behavioral coverage for the judgment
half of Arcana.

The deterministic validators and mutating rites cover the mechanical floor. The
invocations (`invocations/**/*.md`) are playbooks an AI agent follows to do
judgment work - classifying a file into the right storage layer, surfacing a
contradiction, placing a promoted answer. This harness checks whether an agent
following a playbook actually behaves correctly.

It is NOT a rite: it is not pure-stdlib-constrained in spirit (it shells to a
model) and it is never run by `rites/validate.py`. The single model boundary is
an injectable `model_fn(prompt, cwd) -> str` seam, mirroring the `git_fn` /
`skill_runner` / `validate_runner` seams in `rites/summon_state.py`. The default
seam shells to `claude` and refuses unless `ARCANA_EVAL_MODEL` is set, so the
fast pytest gate (which injects a fake seam, or never imports a model path) can
never reach a model. Eval scenario file contents are base64-encoded in the spec
JSON (the §5.5 inert-fixture rule) so deliberately-dirty fixtures never trip the
validators that scan `tests/`.
"""

from __future__ import annotations

import base64
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS_PATH = REPO_ROOT / "tests" / "fixtures" / "invocation_eval_specs.json"
SCHEMA_VERSION = 1
ARCANA_EVAL_MODEL = "ARCANA_EVAL_MODEL"

# A model seam takes the assembled prompt and the grimoire working directory and
# returns the agent's raw stdout (expected to contain a fenced json decision).
ModelFn = Callable[[str, str], str]

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*\n(.*?)\n```", re.DOTALL)


# ---------------------------------------------------------------------------
# Spec model
# ---------------------------------------------------------------------------

REQUIRED_SPEC_FIELDS = {
    "eval_id",
    "invocation",
    "grimoire_name",
    "user_request",
    "scenario_files",
    "decision_directive",
    "assertions",
}


@dataclass(frozen=True)
class EvalSpec:
    eval_id: str
    invocation: str
    grimoire_name: str
    user_request: str
    scenario_files: dict[str, str]   # {relpath: base64 content}
    decision_directive: str
    assertions: list[dict[str, Any]]
    judge_criteria: list[dict[str, Any]] = field(default_factory=list)
    expect_clean_background: bool = True
    expect_validator_codes: list[str] = field(default_factory=list)


def load_specs(path: Path = SPECS_PATH) -> list[EvalSpec]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    specs = []
    for entry in raw.get("evals", []):
        specs.append(EvalSpec(
            eval_id=entry["eval_id"],
            invocation=entry["invocation"],
            grimoire_name=entry["grimoire_name"],
            user_request=entry["user_request"],
            scenario_files=entry["scenario_files"],
            decision_directive=entry["decision_directive"],
            assertions=entry.get("assertions", []),
            judge_criteria=entry.get("judge_criteria", []),
            expect_clean_background=entry.get("expect_clean_background", True),
            expect_validator_codes=entry.get("expect_validator_codes", []),
        ))
    return specs


# ---------------------------------------------------------------------------
# Scenario materialization
# ---------------------------------------------------------------------------


def materialize(spec: EvalSpec, parent: Path) -> Path:
    """Decode the base64 scenario into `parent/<grimoire_name>`; return that root."""
    root = Path(parent) / spec.grimoire_name
    for rel, b64 in spec.scenario_files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(base64.b64decode(b64))
    return root


# ---------------------------------------------------------------------------
# Prompt assembly (pure, deterministic)
# ---------------------------------------------------------------------------


def assemble_prompt(spec: EvalSpec, repo_root: Path = REPO_ROOT) -> str:
    """Build the agent prompt: framing + the playbook text + the decision directive."""
    invocation_text = (Path(repo_root) / spec.invocation).read_text(encoding="utf-8")
    return (
        "You are an AI agent operating inside a grimoire rooted at your current "
        "working directory. Arcana rites live at the path in the ARCANA_HOME "
        "environment variable. Follow the playbook below exactly for the user's "
        f"request, then report your decision.\n\n"
        f"USER REQUEST: {spec.user_request}\n\n"
        f"----- PLAYBOOK: {spec.invocation} -----\n"
        f"{invocation_text}\n"
        f"----- END PLAYBOOK -----\n\n"
        f"{spec.decision_directive}\n"
    )


def parse_decision(stdout: str) -> dict[str, Any] | None:
    """Extract the last fenced json block from agent stdout and parse it."""
    blocks = _JSON_BLOCK_RE.findall(stdout or "")
    for block in reversed(blocks):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return None


# ---------------------------------------------------------------------------
# Deterministic assertions
# ---------------------------------------------------------------------------


def _scalar(decision: dict, dotted: str) -> Any:
    cur: Any = decision
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _item_matches(item: dict, where: dict) -> bool:
    if not isinstance(item, dict):
        return False
    for key, expected in where.items():
        if key.endswith("__contains"):
            actual = item.get(key[: -len("__contains")])
            if not isinstance(actual, str) or expected not in actual:
                return False
        elif key.endswith("__contains_all"):
            actual = item.get(key[: -len("__contains_all")])
            if not isinstance(actual, list):
                return False
            # Each needle must match some single element, not a join of all of
            # them - so one crafted element cannot satisfy several distinct needles.
            if not all(any(needle in str(el) for el in actual) for needle in expected):
                return False
        else:
            if item.get(key) != expected:
                return False
    return True


def check_assertion(assertion: dict, decision: dict, root: Path) -> tuple[bool, str]:
    """Return (passed, detail) for one deterministic assertion."""
    kind = assertion.get("type")
    if decision is None:
        return False, "no decision parsed from agent output"

    if kind == "list_any":
        items = decision.get(assertion["list"])
        if not isinstance(items, list):
            return False, f"decision.{assertion['list']} is not a list"
        ok = any(_item_matches(it, assertion["where"]) for it in items)
        return ok, f"list_any {assertion['list']} where {assertion['where']}"

    if kind == "field_equals":
        actual = _scalar(decision, assertion["field"])
        return actual == assertion["value"], f"{assertion['field']}={actual!r} expected {assertion['value']!r}"

    if kind == "field_in":
        actual = _scalar(decision, assertion["field"])
        return actual in assertion["values"], f"{assertion['field']}={actual!r} expected one of {assertion['values']}"

    if kind == "file_exists":
        return (root / assertion["path"]).exists(), f"file_exists {assertion['path']}"

    if kind == "file_absent":
        return not (root / assertion["path"]).exists(), f"file_absent {assertion['path']}"

    if kind == "glob_min":
        found = len(list(root.glob(assertion["pattern"])))
        return found >= assertion["min"], f"glob_min {assertion['pattern']} >= {assertion['min']} (found {found})"

    if kind == "file_from_decision_exists":
        rel = _scalar(decision, assertion["field"])
        if not isinstance(rel, str) or not rel:
            return False, f"decision.{assertion['field']} is not a path"
        return (root / rel).exists(), f"file_from_decision_exists {assertion['field']}={rel}"

    return False, f"unknown assertion type {kind!r}"


# ---------------------------------------------------------------------------
# LLM judge (one binary criterion per model call)
# ---------------------------------------------------------------------------


def build_judge_prompt(criterion: dict, agent_output: str) -> str:
    return (
        "You are grading one AI agent transcript against a single binary "
        "criterion. Be strict. Answer only about the criterion below.\n\n"
        f"CRITERION: {criterion['question']}\n"
        f"PASS IF: {criterion['pass_if']}\n"
        f"FAIL IF: {criterion['fail_if']}\n\n"
        "----- AGENT OUTPUT -----\n"
        f"{agent_output}\n"
        "----- END AGENT OUTPUT -----\n\n"
        "Emit exactly one fenced ```json block and nothing after it:\n"
        '{"verdict": "pass" | "fail", "evidence_quote": "<verbatim span from the '
        'agent output that justifies the verdict, or empty if none>", '
        '"reason": "<one sentence>"}'
    )


def run_judge(criterion: dict, agent_output: str, model_fn: ModelFn, cwd: str) -> tuple[bool, dict]:
    """Run one judge criterion. A pass requires a non-empty evidence quote."""
    raw = model_fn(build_judge_prompt(criterion, agent_output), cwd)
    verdict = parse_decision(raw) or {}
    passed = (
        verdict.get("verdict") == "pass"
        and isinstance(verdict.get("evidence_quote"), str)
        and verdict["evidence_quote"].strip() != ""
    )
    return passed, {
        "criterion_id": criterion.get("id"),
        "verdict": verdict.get("verdict"),
        "evidence_quote": verdict.get("evidence_quote", ""),
        "reason": verdict.get("reason", ""),
    }


# ---------------------------------------------------------------------------
# Default model seam
# ---------------------------------------------------------------------------


def claude_cli_seam(prompt: str, cwd: str, *, timeout: int = 600) -> str:
    """Default seam: drive the `claude` CLI headlessly in `cwd`.

    Refuses unless ARCANA_EVAL_MODEL is set, so it can never fire in the fast gate.
    """
    if not os.environ.get(ARCANA_EVAL_MODEL):
        raise RuntimeError(
            f"{ARCANA_EVAL_MODEL} is not set; refusing to call a model. "
            "Set it to opt into the model-in-the-loop eval tier."
        )
    env = dict(os.environ)
    env.setdefault("ARCANA_HOME", str(REPO_ROOT))
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "text"],
        cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env,
    )
    return (result.stdout or "") + (result.stderr or "")


def fake_seam(stdout: str) -> ModelFn:
    """A ModelFn returning a canned response, ignoring prompt and cwd."""
    return lambda prompt, cwd: stdout


# ---------------------------------------------------------------------------
# One eval run
# ---------------------------------------------------------------------------


@dataclass
class EvalResult:
    eval_id: str
    invocation: str
    outcome: str                 # pass | fail | error
    decision: dict | None
    assertion_results: list[dict]
    judge_results: list[dict]
    transcript: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "eval_id": self.eval_id,
            "invocation": self.invocation,
            "outcome": self.outcome,
            "decision": self.decision,
            "assertions": self.assertion_results,
            "judge": self.judge_results,
        }


def run_one_eval(spec: EvalSpec, parent: Path, model_fn: ModelFn) -> EvalResult:
    """Materialize, run the agent via the seam, then judge deterministically + by rubric."""
    root = materialize(spec, parent)
    prompt = assemble_prompt(spec)
    try:
        transcript = model_fn(prompt, str(root))
    except Exception as exc:  # seam failure (no model, timeout, ...)
        return EvalResult(spec.eval_id, spec.invocation, "error", None, [], [], f"seam error: {exc}")

    decision = parse_decision(transcript)
    assertion_results = []
    for assertion in spec.assertions:
        passed, detail = check_assertion(assertion, decision, root)
        assertion_results.append({"assertion": assertion, "passed": passed, "detail": detail})

    judge_results = []
    for criterion in spec.judge_criteria:
        passed, record = run_judge(criterion, transcript, model_fn, str(root))
        record["passed"] = passed
        judge_results.append(record)

    all_passed = (
        decision is not None
        and all(r["passed"] for r in assertion_results)
        and all(r["passed"] for r in judge_results)
    )
    return EvalResult(
        spec.eval_id, spec.invocation, "pass" if all_passed else "fail",
        decision, assertion_results, judge_results, transcript,
    )


def suite_report(results: list[EvalResult], *, mode: str, root: str) -> dict[str, Any]:
    """Aggregate envelope, reusing the ResultReporter vocabulary (schema_version/status/mode/summary)."""
    passed = sum(1 for r in results if r.outcome == "pass")
    failed = sum(1 for r in results if r.outcome == "fail")
    errors = sum(1 for r in results if r.outcome == "error")
    status = "pass" if (failed == 0 and errors == 0) else "fail"
    return {
        "schema_version": SCHEMA_VERSION,
        "rite": "invocation_evals",
        "status": status,
        "mode": mode,
        "root": root,
        "summary": {"total": len(results), "passed": passed, "failed": failed, "errors": errors},
        "results": [r.to_dict() for r in results],
    }
