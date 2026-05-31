"""Generative negative coverage: every validator must fail-on-dirty.

For each validator, `tests/fixtures/negative_specs.json` carries a minimal
violating tree (file contents base64-encoded so the spec is inert to the
validators that scan `tests/`) plus the diagnostic codes that tree must trigger.
This module materializes each tree in a temp dir, runs the validator in
`--format json`, and asserts every promised code fires - so a refactor that
silently stops detecting a violation is caught.

A completeness gate (`test_declared_codes_are_covered`) statically enumerates
every diagnostic code each validator can emit and asserts each is either
triggered by a fixture or listed in that validator's documented allowlist
(I/O-only or mutually-exclusive codes). Adding a new code without coverage fails
the gate.
"""

import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS = json.loads((REPO_ROOT / "tests" / "fixtures" / "negative_specs.json").read_text())

# Codes emitted via shared contract-loader helpers rather than a literal
# reporter.error("CODE", ...) call in the validator's own source; the static
# scan below cannot see them, so they are not part of the completeness contract.
_HELPER_EMITTED = {
    "AGENT_TARGETS_READ", "RITE_PROFILE_READ", "SUMMON_CONTRACT_READ",
    "COMMAND_SURFACE_READ",
}


def _materialize(root: Path, files: dict) -> None:
    for rel, b64 in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(base64.b64decode(b64))


def _run(validator: str, run_mode: str, root: Path) -> tuple[int, set]:
    cmd = [sys.executable, str(REPO_ROOT / "rites" / f"{validator}.py")]
    env = dict(os.environ)
    if run_mode == "grimoire":
        cmd += ["--grimoire", str(root)]
    else:  # arcana_home: point the Arcana-only validator at the fixture tree
        env["ARCANA_HOME"] = str(root)
    cmd += ["--format", "json"]
    result = subprocess.run(
        cmd, capture_output=True, text=True, env=env, timeout=60, cwd=str(REPO_ROOT)
    )
    codes = set()
    try:
        report = json.loads(result.stdout)
        for diag in report.get("diagnostics", []):
            codes.add(diag.get("code"))
    except json.JSONDecodeError:
        pass
    return result.returncode, codes


def _declared_codes(validator: str) -> set:
    txt = (REPO_ROOT / "rites" / f"{validator}.py").read_text()
    pat = re.compile(r'reporter\.(?:error|warning)\(\s*["\']([A-Z][A-Z0-9_]+)["\']', re.S)
    return set(pat.findall(txt))


@pytest.mark.parametrize("validator", sorted(SPECS))
def test_validator_fails_on_dirty(validator, tmp_path):
    spec = SPECS[validator]
    _materialize(tmp_path, spec["files"])
    returncode, emitted = _run(validator, spec["run_mode"], tmp_path)

    assert returncode != 0, (
        f"{validator} should exit non-zero on its negative fixture"
    )
    missing = sorted(set(spec["expected_codes"]) - emitted)
    assert not missing, (
        f"{validator} no longer emits expected codes {missing}; "
        f"emitted {sorted(emitted)}"
    )


@pytest.mark.parametrize("validator", sorted(SPECS))
def test_expected_and_allowlist_are_disjoint(validator):
    spec = SPECS[validator]
    overlap = set(spec["expected_codes"]) & set(spec.get("allowlist", {}))
    assert not overlap, f"{validator}: codes both expected and allowlisted: {overlap}"


def test_declared_codes_are_covered():
    """Every diagnostic code a validator declares is triggered by a fixture or
    documented in that validator's allowlist. Forces new codes into coverage."""
    uncovered = {}
    for validator, spec in SPECS.items():
        declared = _declared_codes(validator) - _HELPER_EMITTED
        covered = set(spec["expected_codes"]) | set(spec.get("allowlist", {}))
        gap = sorted(declared - covered)
        if gap:
            uncovered[validator] = gap
    assert not uncovered, (
        "Declared diagnostic codes with no fixture and no allowlist entry "
        f"(add a fixture or an allowlist reason): {uncovered}"
    )
