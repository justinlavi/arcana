"""Model-in-the-loop invocation evals - the slower job beneath the fast gate.

These run a real agent (the `claude` CLI seam) against each seeded scenario and
assert the playbook produced the right judgment. They are deselected by default
(`addopts = -m "not eval"` in pyproject.toml) and additionally skip unless
ARCANA_EVAL_MODEL is set, so the mechanical CI gate never reaches a model. Run
the tier explicitly:

    ARCANA_EVAL_MODEL=1 python -m pytest -m eval
"""

import os

import pytest

import eval_harness as H

requires_model = pytest.mark.skipif(
    not os.environ.get(H.ARCANA_EVAL_MODEL),
    reason=f"{H.ARCANA_EVAL_MODEL} not set; model-in-the-loop eval skipped",
)


@pytest.mark.eval
@requires_model
@pytest.mark.parametrize("spec", H.load_specs(), ids=lambda s: s.eval_id)
def test_invocation_eval_passes(spec, tmp_path):
    result = H.run_one_eval(spec, tmp_path, H.claude_cli_seam)
    assert result.outcome == "pass", result.to_dict()
