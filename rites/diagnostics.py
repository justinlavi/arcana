#!/usr/bin/env python3
"""Structured diagnostics for Arcana validators."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

OUTPUT_FORMATS = ("human", "json", "jsonl")


@dataclass(frozen=True)
class Diagnostic:
    """One validator finding."""

    code: str
    severity: str
    message: str
    validator: str
    path: str | None = None
    line: int | None = None
    hint: str | None = None
    docs_reference: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "path": self.path,
            "line": self.line,
            "message": self.message,
            "hint": self.hint,
            "validator": self.validator,
            "docs_reference": self.docs_reference,
        }


class DiagnosticReporter:
    """Collect and emit validator diagnostics."""

    def __init__(self, validator: str, root: Path | None = None) -> None:
        self.validator = validator
        self.root = root
        self.diagnostics: list[Diagnostic] = []

    def error(
        self,
        code: str,
        message: str,
        path: str | Path | None = None,
        line: int | None = None,
        hint: str | None = None,
        docs_reference: str | None = None,
    ) -> Diagnostic:
        return self.add(
            code=code,
            severity="error",
            message=message,
            path=path,
            line=line,
            hint=hint,
            docs_reference=docs_reference,
        )

    def warning(
        self,
        code: str,
        message: str,
        path: str | Path | None = None,
        line: int | None = None,
        hint: str | None = None,
        docs_reference: str | None = None,
    ) -> Diagnostic:
        return self.add(
            code=code,
            severity="warning",
            message=message,
            path=path,
            line=line,
            hint=hint,
            docs_reference=docs_reference,
        )

    def add(
        self,
        code: str,
        severity: str,
        message: str,
        path: str | Path | None = None,
        line: int | None = None,
        hint: str | None = None,
        docs_reference: str | None = None,
    ) -> Diagnostic:
        diagnostic = Diagnostic(
            code=code,
            severity=severity,
            message=message,
            validator=self.validator,
            path=self._normalize_path(path),
            line=line,
            hint=hint,
            docs_reference=docs_reference,
        )
        self.diagnostics.append(diagnostic)
        return diagnostic

    def error_count(self) -> int:
        return sum(1 for diagnostic in self.diagnostics if diagnostic.severity == "error")

    def warning_count(self) -> int:
        return sum(1 for diagnostic in self.diagnostics if diagnostic.severity == "warning")

    def exit_code(self) -> int:
        return 1 if self.error_count() else 0

    def status(self) -> str:
        return "fail" if self.error_count() else "pass"

    def report(self, checked: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "validator": self.validator,
            "status": self.status(),
            "root": str(self.root) if self.root is not None else None,
            "checked": checked or {},
            "summary": {
                "errors": self.error_count(),
                "warnings": self.warning_count(),
                "diagnostics": len(self.diagnostics),
            },
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }

    def emit(self, output_format: str, checked: dict[str, Any] | None = None) -> None:
        report = self.report(checked=checked)
        if output_format == "json":
            print(json.dumps(report, indent=2, sort_keys=True))
            return
        if output_format == "jsonl":
            for diagnostic in report["diagnostics"]:
                print(json.dumps(diagnostic, sort_keys=True))
            print(json.dumps({"type": "summary", **report["summary"]}, sort_keys=True))
            return
        raise ValueError(f"unknown diagnostic output format: {output_format}")

    def _normalize_path(self, path: str | Path | None) -> str | None:
        if path is None:
            return None
        if isinstance(path, Path):
            try:
                if self.root is not None:
                    return path.relative_to(self.root).as_posix()
            except ValueError:
                pass
            return path.as_posix()
        return path.replace("\\", "/")


def add_output_format_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        choices=OUTPUT_FORMATS,
        default="human",
        help="Diagnostic output format",
    )


def human_location(diagnostic: dict[str, Any] | Diagnostic) -> str:
    data = diagnostic.to_dict() if isinstance(diagnostic, Diagnostic) else diagnostic
    path = data.get("path")
    line = data.get("line")
    if path and line:
        return f"{path}:{line}"
    if path:
        return path
    return "-"


def human_label(severity: str) -> str:
    return "ERROR" if severity == "error" else "WARN"


# ---------------------------------------------------------------------------
# Mutating-rite outcomes
# ---------------------------------------------------------------------------

RESULT_STATUSES = ("ok", "noop", "blocked", "error")


def normalize_path(path: str | Path | None, root: Path | None) -> str | None:
    """Return a root-relative POSIX path string, or the path as-is."""
    if path is None:
        return None
    if isinstance(path, Path):
        if root is not None:
            try:
                return path.relative_to(root).as_posix()
            except ValueError:
                pass
        return path.as_posix()
    return str(path).replace("\\", "/")


class ResultReporter:
    """Collect and emit the outcome of a mutating rite.

    Validators report findings via DiagnosticReporter; mutating rites report an
    outcome - what changed, under which mode, and whether it succeeded. The JSON
    envelope lets an orchestrator run a rite and verify the result instead of
    parsing human prose. Human output stays the rite's own concern; this only
    emits the `json`/`jsonl` envelope.
    """

    def __init__(self, rite: str, root: Path | None = None, mode: str | None = None) -> None:
        self.rite = rite
        self.root = root
        self.mode = mode  # "plan" | "apply" | "append" | None
        self.mutations: list[dict[str, Any]] = []
        self.messages: list[dict[str, Any]] = []
        self._status: str | None = None

    def mutation(self, action: str, path: str | Path | None = None, detail: str | None = None) -> None:
        self.mutations.append({
            "action": action,
            "path": normalize_path(path, self.root),
            "detail": detail,
        })

    def message(self, severity: str, text: str, path: str | Path | None = None) -> None:
        self.messages.append({
            "severity": severity,
            "message": text,
            "path": normalize_path(path, self.root),
        })

    def set_status(self, status: str) -> None:
        self._status = status

    def status(self) -> str:
        if self._status is not None:
            return self._status
        if any(message["severity"] == "error" for message in self.messages):
            return "error"
        return "ok" if self.mutations else "noop"

    def exit_code(self) -> int:
        """Default exit code; rites with richer conventions may override."""
        return 0 if self.status() in ("ok", "noop") else 1

    def report(self, summary: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "rite": self.rite,
            "status": self.status(),
            "mode": self.mode,
            "root": str(self.root) if self.root is not None else None,
            "summary": summary or {},
            "mutations": self.mutations,
            "messages": self.messages,
        }

    def emit(self, output_format: str, summary: dict[str, Any] | None = None) -> None:
        report = self.report(summary=summary)
        if output_format == "json":
            print(json.dumps(report, indent=2, sort_keys=True))
            return
        if output_format == "jsonl":
            for mutation in report["mutations"]:
                print(json.dumps({"type": "mutation", **mutation}, sort_keys=True))
            for message in report["messages"]:
                print(json.dumps({"type": "message", **message}, sort_keys=True))
            print(json.dumps({
                "type": "summary",
                "rite": report["rite"],
                "status": report["status"],
                "mode": report["mode"],
                **report["summary"],
            }, sort_keys=True))
            return
        raise ValueError(f"unknown result output format: {output_format}")
