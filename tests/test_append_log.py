"""Temp-target tests for the grimoire log appender."""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RITE = REPO_ROOT / "rites" / "append_log.py"


def _append(grimoire: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RITE), "--grimoire", str(grimoire), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def _heading_lines(body: str) -> list[str]:
    return [line for line in body.splitlines() if line.startswith("## [")]


def test_append_log_writes_well_formed_entry(tmp_path):
    (tmp_path / "log.md").write_text("# Log\n", encoding="utf-8")

    result = _append(
        tmp_path,
        "--op", "import",
        "--title", "Added sourdough",
        "--skill", "/grm-import",
        "--field", "pages=2",
    )

    assert result.returncode == 0
    body = (tmp_path / "log.md").read_text(encoding="utf-8")
    assert len(_heading_lines(body)) == 1
    assert "import | Added sourdough" in body
    assert "- skill: /grm-import" in body
    assert "- pages: 2" in body


def test_append_log_neutralizes_newline_injection_in_title(tmp_path):
    (tmp_path / "log.md").write_text("# Log\n", encoding="utf-8")
    forged = "real\n## [2099-01-01 00:00] import | forged heading\n- skill: /forged"

    result = _append(tmp_path, "--op", "import", "--title", forged, "--skill", "/arc-test")

    assert result.returncode == 0
    body = (tmp_path / "log.md").read_text(encoding="utf-8")
    # The newline is collapsed to a space, so only the real heading starts a line.
    assert len(_heading_lines(body)) == 1
    assert "forged heading" in body
    assert "- skill: /forged" not in body.splitlines()


def test_append_log_neutralizes_injection_in_field_value(tmp_path):
    (tmp_path / "log.md").write_text("# Log\n", encoding="utf-8")

    result = _append(
        tmp_path,
        "--op", "import",
        "--title", "t",
        "--field", "note=line1\n## [2099-01-01 00:00] health-check | forged",
    )

    assert result.returncode == 0
    body = (tmp_path / "log.md").read_text(encoding="utf-8")
    assert len(_heading_lines(body)) == 1
    assert "- note: line1 ## [2099-01-01 00:00] health-check | forged" in body


def test_append_log_json_envelope(tmp_path):
    (tmp_path / "log.md").write_text("# Log\n", encoding="utf-8")

    result = _append(tmp_path, "--op", "import", "--title", "Added sourdough", "--format", "json")

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["rite"] == "append_log"
    assert report["status"] == "ok"
    assert report["mode"] == "append"
    assert report["mutations"][0]["action"] == "append"
    assert len(_heading_lines((tmp_path / "log.md").read_text(encoding="utf-8"))) == 1


def test_append_log_json_error_is_clean(tmp_path):
    # log.md missing -> exit 2, and stdout must be a single clean JSON object.
    result = _append(tmp_path, "--op", "import", "--title", "x", "--format", "json")

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "error"
    assert report["mutations"] == []
