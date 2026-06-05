---
type: reference
title: "Invocation Eval Tier"
aliases: ["evals", "invocation-evals"]
tags: [type/reference, arcana/docs, scope/testing]
authority: grimoire
last_verified: 2026-06-01
---

# Invocation Eval Tier

## Purpose

The deterministic validators and mutating rites cover Arcana's mechanical floor.
The **invocations** (`invocations/**/*.md`) are playbooks an AI agent follows to
do *judgment* work — classifying a file into the right storage layer, surfacing a
contradiction, placing a promoted answer. That judgment has no deterministic
analog, so it needs a different kind of test: run an agent against a seeded
scenario and check whether the playbook produced the right outcome.

This is the **slower job beneath the fast gate** ([script vs ai](script_vs_ai.md)
explains the rite/invocation split this tier tests the second half of). It is
model-in-the-loop, so it never runs in the mechanical CI gate.

## How it relates to the deterministic gate

The fast gate (`pytest -q` + `python rites/validate.py`) stays model-free. The
eval tier keeps the floor deterministic in three ways:

- It is **not a rite** — `rites/` stays pure-stdlib and the eval harness is never
  run by `rites/validate.py` or listed in `validators.json`.
- The single model boundary is an **injectable seam**, `model_fn(prompt, cwd)`,
  mirroring the `git_fn` / `skill_runner` / `validate_runner` seams in
  `rites/summon_state.py`. The default seam shells to `claude` and **refuses
  unless `ARCANA_EVAL_MODEL` is set**.
- The model-in-the-loop tests carry the `eval` marker, which `pyproject.toml`
  **deselects by default** (`-m "not eval"`). Only the deterministic *scaffolding*
  tests run in the fast gate.

## Running the evals

```bash
# Fast gate (default): deterministic scaffolding only, no model.
python -m pytest -q

# Opt in to the model-in-the-loop tier:
ARCANA_EVAL_MODEL=1 python -m pytest -m eval
```

Without `ARCANA_EVAL_MODEL`, the `eval`-marked tests skip cleanly, so the tier is
green-by-skip on any machine without model access.

## What an eval checks

Each eval materializes a small, **validate-clean** fixture grimoire in a seeded
state, runs the playbook through the seam, and asks the agent to emit one fenced
`json` decision block. The harness then judges that decision two ways:

- **Structured assertions (primary).** Deterministic checks on the decision and
  the resulting disk state — `list_any`, `field_equals`, `field_in`,
  `file_exists` / `file_absent`, `file_from_decision_exists`. Used whenever the
  expected outcome is a closed set (which layer, which `authority`, which pages).
- **LLM judge (fallback, tagged).** One binary criterion per model call, each
  requiring a verbatim evidence quote to pass. Reserved for outcomes that resist
  a structured check — e.g. "did the findings identify *the* seeded
  contradiction?".

## Eval spec format

Specs live in [`tests/fixtures/invocation_eval_specs.json`](../tests/fixtures/invocation_eval_specs.json).
Every scenario file's contents are **base64-encoded** — the same inert-fixture
rule as the [negative-coverage gate](../tests/test_negative_coverage.py) — because
the content validators (`validate_security`, `validate_encoding`, and others)
scan `tests/`; a deliberately-shaped fixture stored raw would trip the very
gate it tests against. Each spec carries:

| Field | Meaning |
|---|---|
| `eval_id` | unique id |
| `invocation` | the playbook under test (`invocations/**/*.md`) |
| `grimoire_name` | the materialized fixture's root directory |
| `user_request` | the simulated slash-command the agent receives |
| `scenario_files` | `{relpath: base64}` — the fixture grimoire |
| `decision_directive` | the structured-output instruction appended to the prompt |
| `assertions` | deterministic checks on the decision and disk |
| `judge_criteria` | binary LLM-judge criteria (may be empty) |
| `expect_clean_background` | whether the fixture passes `validate.py` as-is |

The harness lives in [`tests/eval_harness.py`](../tests/eval_harness.py); the
deterministic scaffolding (specs valid, invocations exist, scenarios materialize
clean, prompt assembly, assertion and judge wiring) is in
[`tests/test_eval_scaffolding.py`](../tests/test_eval_scaffolding.py), and the
model run is in [`tests/test_eval_live.py`](../tests/test_eval_live.py).

## Scope

The first cut ships the harness, the opt-in runner, the deterministic
scaffolding, and starter scenarios for `/grm-import` (layer classification),
`/grm-health-check` (seeded contradiction), and `/grm-capture-answer` (placement +
faithfulness). An always-on GitHub Actions job that runs the model evals is
deferred: it needs a reliable model gateway and a secret, and a flaky required
check would erode the "leave the tree green" discipline. When that exists, it is
a zero-refactor upgrade — the workflow sets `ARCANA_EVAL_MODEL` and runs
`pytest -m eval`.

## Adding an eval

1. Build a clean fixture grimoire (model it on `tests/fixtures/good_grimoire/`),
   seed exactly one judgment-level defect, and base64-encode every file into a
   new entry in `invocation_eval_specs.json`.
2. Write a `decision_directive` that forces a structured decision, and prefer
   `assertions` over `judge_criteria` wherever the outcome is a closed set.
3. Run `python -m pytest tests/test_eval_scaffolding.py` — it fails until the
   spec is well-formed, the invocation exists, and the fixture is validate-clean.
4. Run `ARCANA_EVAL_MODEL=1 python -m pytest -m eval` to confirm the playbook
   passes against a real model.

## Related

- [Script vs AI](script_vs_ai.md) — the rite/invocation boundary this tier tests
- [Governance](governance.md) — the autonomy tiers maintenance work honors
- [Reference](reference.md) — terminology and schemas
