#!/usr/bin/env python3
"""Load and validate the Summoning Rite behavior contract."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

CONTRACT_PATH = Path("rites/data/summon_contract.json")

REQUIRED_MODE_FIELDS = {
    "id",
    "label",
    "surface",
    "entrypoint",
    "owner",
    "required_behaviors",
}
REQUIRED_PIPELINE_FIELDS = {"id", "label", "owner", "required_for"}
REQUIRED_ENV_FIELDS = {"name", "purpose"}
REQUIRED_ASSET_FIELDS = {"platform", "archive", "checksum"}


def load_summon_contract(root: Path) -> dict[str, Any]:
    """Load the Summoning Rite contract JSON."""
    return json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))


def mode_entries(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """Return summon mode entries from the contract, or an empty list."""
    entries = contract.get("modes", [])
    return entries if isinstance(entries, list) else []


def pipeline_entries(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """Return required pipeline entries from the contract, or an empty list."""
    entries = contract.get("required_pipeline", [])
    return entries if isinstance(entries, list) else []


def bootstrap_environment_entries(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """Return bootstrap environment entries from the contract, or an empty list."""
    entries = contract.get("bootstrap_environment", [])
    return entries if isinstance(entries, list) else []


def release_asset_entries(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """Return release asset entries from the contract, or an empty list."""
    entries = contract.get("release_assets", [])
    return entries if isinstance(entries, list) else []


def _error(code: str, message: str, path: str, hint: str) -> dict[str, str]:
    return {
        "code": code,
        "message": message,
        "path": path,
        "hint": hint,
    }


def _top_level_symbols(path: Path) -> set[str]:
    """Return top-level function and class names from a Python file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return set()
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def _symbol_exists(root: Path, symbol: str) -> bool:
    """Return True when a contract symbol exists in a Python or shell rite."""
    if ":" in symbol:
        file_name, function_name = symbol.split(":", 1)
        path = root / "rites" / file_name
        if not path.is_file():
            return False
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return False
        return f"{function_name}()" in text

    module_name, _, attr_name = symbol.partition(".")
    if not module_name or not attr_name:
        return False
    path = root / "rites" / f"{module_name}.py"
    if not path.is_file():
        return False
    return attr_name in _top_level_symbols(path)


def _validate_required_fields(
    entry: dict[str, Any],
    required: set[str],
    path: str,
    label: str,
    errors: list[dict[str, str]],
) -> None:
    for field in sorted(required):
        value = entry.get(field)
        if field in {"required_behaviors", "required_for"}:
            if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
                errors.append(_error(
                    "SUMMON_CONTRACT_FIELD",
                    f"{label} must declare non-empty string items in {field}",
                    path,
                    f"Set {field} to a non-empty list of strings.",
                ))
        elif not isinstance(value, str) or not value.strip():
            errors.append(_error(
                "SUMMON_CONTRACT_FIELD",
                f"{label} must declare non-empty {field}",
                path,
                f"Add {field} to the summon contract entry.",
            ))


def validate_summon_contract(root: Path) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    """Return the loaded contract and structured validation errors."""
    try:
        contract = load_summon_contract(root)
    except (OSError, json.JSONDecodeError) as exc:
        return None, [_error(
            "SUMMON_CONTRACT_READ",
            f"could not read summon contract: {exc}",
            CONTRACT_PATH.as_posix(),
            "Create valid JSON at rites/data/summon_contract.json.",
        )]

    errors: list[dict[str, str]] = []
    if contract.get("schema_version") != 1:
        errors.append(_error(
            "SUMMON_CONTRACT_SCHEMA",
            "summon contract must declare schema_version 1",
            CONTRACT_PATH.as_posix(),
            "Set schema_version to 1.",
        ))

    modes = mode_entries(contract)
    if not isinstance(contract.get("modes"), list):
        errors.append(_error(
            "SUMMON_CONTRACT_MODES",
            "summon contract must contain a modes list",
            CONTRACT_PATH.as_posix(),
            "Add a top-level modes array.",
        ))

    seen_modes: dict[str, int] = {}
    for index, entry in enumerate(modes):
        path = f"{CONTRACT_PATH.as_posix()}#/modes/{index}"
        if not isinstance(entry, dict):
            errors.append(_error(
                "SUMMON_CONTRACT_ENTRY",
                "summon mode entry must be an object",
                path,
                "Replace this entry with an object keyed by mode metadata.",
            ))
            continue
        mode_id = entry.get("id") if isinstance(entry.get("id"), str) else f"<mode {index}>"
        seen_modes[mode_id] = seen_modes.get(mode_id, 0) + 1
        _validate_required_fields(entry, REQUIRED_MODE_FIELDS, path, mode_id, errors)

        surface = entry.get("surface")
        if isinstance(surface, str) and surface.strip() and not (root / surface).exists():
            errors.append(_error(
                "SUMMON_CONTRACT_PATH",
                f"{mode_id} surface does not exist: {surface}",
                path,
                "Point surface at an existing repository-relative path.",
            ))

        symbols = entry.get("code_symbols", [])
        if symbols is not None and (
            not isinstance(symbols, list)
            or not all(isinstance(symbol, str) and symbol.strip() for symbol in symbols)
        ):
            errors.append(_error(
                "SUMMON_CONTRACT_SYMBOLS",
                f"{mode_id} code_symbols must be a list of strings",
                path,
                "Set code_symbols to an empty list or valid symbol names.",
            ))
            continue
        for symbol in symbols:
            if not _symbol_exists(root, symbol):
                errors.append(_error(
                    "SUMMON_CONTRACT_SYMBOL",
                    f"{mode_id} code symbol does not exist: {symbol}",
                    path,
                    "Point code_symbols at top-level Python symbols or shell functions.",
                ))

    for mode_id, count in sorted(seen_modes.items()):
        if count > 1:
            errors.append(_error(
                "SUMMON_CONTRACT_DUPLICATE_MODE",
                f"{mode_id} appears {count} times in the summon contract",
                CONTRACT_PATH.as_posix(),
                "Keep exactly one mode entry per mode id.",
            ))

    mode_ids = set(seen_modes)
    for index, entry in enumerate(pipeline_entries(contract)):
        path = f"{CONTRACT_PATH.as_posix()}#/required_pipeline/{index}"
        if not isinstance(entry, dict):
            errors.append(_error(
                "SUMMON_CONTRACT_ENTRY",
                "required_pipeline entry must be an object",
                path,
                "Replace this entry with an object keyed by pipeline metadata.",
            ))
            continue
        label = entry.get("id") if isinstance(entry.get("id"), str) else f"<pipeline {index}>"
        _validate_required_fields(entry, REQUIRED_PIPELINE_FIELDS, path, label, errors)
        owner = entry.get("owner")
        if isinstance(owner, str) and owner.strip() and not _symbol_exists(root, owner):
            errors.append(_error(
                "SUMMON_CONTRACT_SYMBOL",
                f"{label} owner symbol does not exist: {owner}",
                path,
                "Point owner at a top-level Python symbol.",
            ))
        required_for = entry.get("required_for", [])
        if isinstance(required_for, list):
            for mode_id in required_for:
                if isinstance(mode_id, str) and mode_id not in mode_ids:
                    errors.append(_error(
                        "SUMMON_CONTRACT_MODE_REF",
                        f"{label} references unknown mode {mode_id}",
                        path,
                        "Use a mode id declared under modes.",
                    ))

    for index, entry in enumerate(bootstrap_environment_entries(contract)):
        path = f"{CONTRACT_PATH.as_posix()}#/bootstrap_environment/{index}"
        if not isinstance(entry, dict):
            errors.append(_error(
                "SUMMON_CONTRACT_ENTRY",
                "bootstrap_environment entry must be an object",
                path,
                "Replace this entry with an object keyed by environment metadata.",
            ))
            continue
        label = entry.get("name") if isinstance(entry.get("name"), str) else f"<env {index}>"
        _validate_required_fields(entry, REQUIRED_ENV_FIELDS, path, label, errors)

    for index, entry in enumerate(release_asset_entries(contract)):
        path = f"{CONTRACT_PATH.as_posix()}#/release_assets/{index}"
        if not isinstance(entry, dict):
            errors.append(_error(
                "SUMMON_CONTRACT_ENTRY",
                "release_assets entry must be an object",
                path,
                "Replace this entry with an object keyed by release asset metadata.",
            ))
            continue
        label = entry.get("platform") if isinstance(entry.get("platform"), str) else f"<asset {index}>"
        _validate_required_fields(entry, REQUIRED_ASSET_FIELDS, path, label, errors)

    return contract, errors
