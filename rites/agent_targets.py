#!/usr/bin/env python3
"""Load and validate Arcana's agent target registry."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

CONTRACT_PATH = Path("rites/data/agent_targets.json")
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
INSTRUCTION_MODES = {"auto", "manual"}
SKILL_MODES = {"full", "pointer", "none"}
REQUIRED_FIELDS = {
    "id",
    "label",
    "instruction_target",
    "instruction_mode",
    "skill_mode",
    "auto_configured",
    "supports_model_invocation",
    "summary",
    "limitations",
}


def contract_path_candidates(root: Path) -> list[Path]:
    """Return candidate locations for the agent target registry."""
    candidates = [root / CONTRACT_PATH]
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        bundle_root = Path(meipass)
        candidates.extend([
            bundle_root / CONTRACT_PATH,
            bundle_root / "data" / "agent_targets.json",
        ])
    return candidates


def load_agent_targets(root: Path) -> dict[str, Any]:
    """Load the agent target registry JSON."""
    for path in contract_path_candidates(root):
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    checked = ", ".join(str(path) for path in contract_path_candidates(root))
    raise FileNotFoundError(f"Could not find agent target registry. Checked: {checked}")


def agent_target_ids(root: Path) -> list[str]:
    """Return target ids in registry order."""
    return [
        entry["id"]
        for entry in target_entries(load_agent_targets(root))
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    ]


def target_entries(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """Return agent target entries from the registry, or an empty list."""
    entries = contract.get("targets", [])
    return entries if isinstance(entries, list) else []


def resolve_user_path(path_text: str | None) -> Path | None:
    """Resolve a registry path rooted at the user's home directory."""
    if not path_text:
        return None
    if path_text.startswith("~/"):
        return Path.home() / path_text[2:]
    return Path(path_text).expanduser()


def skill_registration_targets(root: Path) -> dict[str, dict[str, Any]]:
    """Return sync_skills target configs keyed by agent id."""
    contract = load_agent_targets(root)
    targets: dict[str, dict[str, Any]] = {}
    for entry in target_entries(contract):
        if entry.get("skill_mode") not in {"full", "pointer"}:
            continue
        skill_path = resolve_user_path(entry.get("skill_target"))
        if skill_path is None:
            continue
        targets[entry["id"]] = {
            "label": entry["label"],
            "path": skill_path,
            "pointer_only": entry["skill_mode"] == "pointer",
        }
    return targets


def automatic_instruction_targets(root: Path) -> list[dict[str, Any]]:
    """Return auto-configured instruction targets with resolved paths."""
    contract = load_agent_targets(root)
    targets = []
    for entry in target_entries(contract):
        if entry.get("instruction_mode") != "auto":
            continue
        instruction_path = resolve_user_path(entry.get("instruction_target"))
        if instruction_path is None:
            continue
        targets.append({
            "id": entry["id"],
            "label": entry["label"],
            "path": instruction_path,
            "title": instruction_path.name,
            "skill_mode": entry.get("skill_mode"),
            "skill_target": resolve_user_path(entry.get("skill_target")),
        })
    return targets


def automatic_instruction_target_ids(root: Path) -> list[str]:
    """Return auto-configured instruction target ids in registry order."""
    return [entry["id"] for entry in automatic_instruction_targets(root)]


def target_by_id(root: Path, target_id: str) -> dict[str, Any] | None:
    """Return one target entry by id."""
    for entry in target_entries(load_agent_targets(root)):
        if entry.get("id") == target_id:
            return entry
    return None


def _error(code: str, message: str, path: str, hint: str) -> dict[str, str]:
    return {
        "code": code,
        "message": message,
        "path": path,
        "hint": hint,
    }


def validate_agent_targets(root: Path) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    """Return the loaded registry and structured validation errors."""
    try:
        contract = load_agent_targets(root)
    except (OSError, json.JSONDecodeError) as exc:
        return None, [_error(
            "AGENT_TARGETS_READ",
            f"could not read agent target registry: {exc}",
            CONTRACT_PATH.as_posix(),
            "Create valid JSON at rites/data/agent_targets.json.",
        )]

    errors: list[dict[str, str]] = []
    if contract.get("schema_version") != 1:
        errors.append(_error(
            "AGENT_TARGETS_SCHEMA",
            "agent target registry must declare schema_version 1",
            CONTRACT_PATH.as_posix(),
            "Set schema_version to 1.",
        ))

    entries = target_entries(contract)
    if not isinstance(contract.get("targets"), list):
        errors.append(_error(
            "AGENT_TARGETS_LIST",
            "agent target registry must contain a targets list",
            CONTRACT_PATH.as_posix(),
            "Add a top-level targets array.",
        ))

    seen: dict[str, int] = {}
    for index, entry in enumerate(entries):
        path = f"{CONTRACT_PATH.as_posix()}#/targets/{index}"
        if not isinstance(entry, dict):
            errors.append(_error(
                "AGENT_TARGETS_ENTRY",
                "agent target entry must be an object",
                path,
                "Replace this entry with an object keyed by target metadata.",
            ))
            continue

        target_id = entry.get("id") if isinstance(entry.get("id"), str) else f"<target {index}>"
        if isinstance(entry.get("id"), str):
            seen[target_id] = seen.get(target_id, 0) + 1
            if not ID_RE.fullmatch(target_id):
                errors.append(_error(
                    "AGENT_TARGETS_ID",
                    f"{target_id} is not a valid target id",
                    path,
                    "Use lowercase kebab-case ids.",
                ))

        for field in sorted(REQUIRED_FIELDS):
            value = entry.get(field)
            if field in {"auto_configured", "supports_model_invocation"}:
                if not isinstance(value, bool):
                    errors.append(_error(
                        "AGENT_TARGETS_FIELD",
                        f"{target_id} must declare boolean {field}",
                        path,
                        f"Set {field} to true or false.",
                    ))
            elif field == "limitations":
                if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                    errors.append(_error(
                        "AGENT_TARGETS_FIELD",
                        f"{target_id} must declare limitations as a string list",
                        path,
                        "Use an empty list when there are no limitations.",
                    ))
            elif not isinstance(value, str) or not value.strip():
                errors.append(_error(
                    "AGENT_TARGETS_FIELD",
                    f"{target_id} must declare non-empty {field}",
                    path,
                    f"Add {field} to this target.",
                ))

        if "skill_target" not in entry:
            errors.append(_error(
                "AGENT_TARGETS_FIELD",
                f"{target_id} must declare skill_target",
                path,
                "Use null when the target has no local skill directory.",
            ))

        instruction_mode = entry.get("instruction_mode")
        if isinstance(instruction_mode, str) and instruction_mode not in INSTRUCTION_MODES:
            errors.append(_error(
                "AGENT_TARGETS_INSTRUCTION_MODE",
                f"{target_id} uses unsupported instruction_mode {instruction_mode}",
                path,
                f"Use one of: {', '.join(sorted(INSTRUCTION_MODES))}.",
            ))

        skill_mode = entry.get("skill_mode")
        if isinstance(skill_mode, str) and skill_mode not in SKILL_MODES:
            errors.append(_error(
                "AGENT_TARGETS_SKILL_MODE",
                f"{target_id} uses unsupported skill_mode {skill_mode}",
                path,
                f"Use one of: {', '.join(sorted(SKILL_MODES))}.",
            ))

        skill_target = entry.get("skill_target")
        if skill_mode in {"full", "pointer"}:
            if not isinstance(skill_target, str) or not skill_target.strip():
                errors.append(_error(
                    "AGENT_TARGETS_SKILL_TARGET",
                    f"{target_id} must declare skill_target when skill_mode is {skill_mode}",
                    path,
                    "Set skill_target to a user-relative directory.",
                ))
        elif skill_target is not None:
            errors.append(_error(
                "AGENT_TARGETS_SKILL_TARGET",
                f"{target_id} must use null skill_target when skill_mode is none",
                path,
                "Set skill_target to null.",
            ))

        if entry.get("auto_configured") is True and instruction_mode != "auto":
            errors.append(_error(
                "AGENT_TARGETS_AUTO_CONFIG",
                f"{target_id} is auto_configured but instruction_mode is not auto",
                path,
                "Use instruction_mode auto for automatic agent configuration.",
            ))

        instruction_target = entry.get("instruction_target")
        if instruction_mode == "auto":
            if not isinstance(instruction_target, str) or not instruction_target.startswith("~/"):
                errors.append(_error(
                    "AGENT_TARGETS_INSTRUCTION_TARGET",
                    f"{target_id} automatic instruction targets must be user-relative",
                    path,
                    "Use a ~/... instruction path for automatic writes.",
                ))

    for target_id, count in sorted(seen.items()):
        if count > 1:
            errors.append(_error(
                "AGENT_TARGETS_DUPLICATE",
                f"{target_id} appears {count} times in the agent target registry",
                CONTRACT_PATH.as_posix(),
                "Keep exactly one entry per target id.",
            ))

    if contract.get("targets") == []:
        errors.append(_error(
            "AGENT_TARGETS_EMPTY",
            "agent target registry must declare at least one target",
            CONTRACT_PATH.as_posix(),
            "Add supported or documented agent targets.",
        ))

    try:
        auto_targets = automatic_instruction_targets(root)
        skill_targets = skill_registration_targets(root)
    except (KeyError, TypeError):
        auto_targets = []
        skill_targets = {}
    if not auto_targets:
        errors.append(_error(
            "AGENT_TARGETS_NO_AUTO",
            "agent target registry must declare at least one automatic instruction target",
            CONTRACT_PATH.as_posix(),
            "Set instruction_mode auto and auto_configured true for local instruction-file targets.",
        ))
    if not skill_targets:
        errors.append(_error(
            "AGENT_TARGETS_NO_SKILLS",
            "agent target registry must declare at least one skill registration target",
            CONTRACT_PATH.as_posix(),
            "Set skill_mode full or pointer with a skill_target.",
        ))

    return contract, errors
