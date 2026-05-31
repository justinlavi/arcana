"""Tests for the shared mutating-rite outcome envelope."""

import json

from diagnostics import ResultReporter


def test_status_defaults_from_content():
    assert ResultReporter("x").status() == "noop"
    assert ResultReporter("x").exit_code() == 0

    wrote = ResultReporter("x")
    wrote.mutation("write", path="a")
    assert wrote.status() == "ok"
    assert wrote.exit_code() == 0

    failed = ResultReporter("x")
    failed.message("error", "boom")
    assert failed.status() == "error"
    assert failed.exit_code() == 1


def test_explicit_status_overrides():
    blocked = ResultReporter("x")
    blocked.set_status("blocked")
    assert blocked.status() == "blocked"
    assert blocked.exit_code() == 1


def test_json_envelope_shape(capsys):
    reporter = ResultReporter("append_log", mode="append")
    reporter.mutation("append", path="log.md", detail="1 entry")
    reporter.emit("json", summary={"entries": 1})

    out = json.loads(capsys.readouterr().out)
    assert out["rite"] == "append_log"
    assert out["mode"] == "append"
    assert out["status"] == "ok"
    assert out["summary"] == {"entries": 1}
    assert out["mutations"][0] == {"action": "append", "path": "log.md", "detail": "1 entry"}


def test_jsonl_emits_one_object_per_line_plus_summary(capsys):
    reporter = ResultReporter("clean_artifacts", mode="apply")
    reporter.mutation("remove", path="rites/.artifacts")
    reporter.emit("jsonl", summary={"removed": 3})

    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.strip()]
    assert lines[0]["type"] == "mutation"
    assert lines[-1] == {"type": "summary", "rite": "clean_artifacts", "status": "ok", "mode": "apply", "removed": 3}


def test_unknown_format_raises(capsys):
    reporter = ResultReporter("x")
    try:
        reporter.emit("human")
    except ValueError:
        return
    raise AssertionError("expected ValueError for human format")
