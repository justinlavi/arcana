#!/usr/bin/env python3
"""Load and validate Arcana's public command-surface contract."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SKILL_PREFIX_PLACEHOLDER = "{{SKILL_PREFIX}}"
CONTRACT_PATH = Path("rites/data/command_surface.json")

REQUIRED_STRING_FIELDS = {
    "command",
    "family",
    "skill_source",
    "invocation",
    "owner_type",
    "mutation_profile",
    "mutation_behavior",
    "log_behavior",
    "validation_profile",
    "generated_docs_impact",
}
REQUIRED_LIST_FIELDS = {"preconditions"}
OPTIONAL_PATH_FIELDS = {"guard", "rite_owner"}
ALLOWED_OWNER_TYPES = {"rite", "judgment", "hybrid"}
ALLOWED_MUTATION_PROFILES = {
    "append_only",
    "read_only",
    "plan_apply",
    "apply_only",
    "judgment_gated",
}
COMMAND_RE = re.compile(r"^/[a-z][a-z0-9]*-[a-z][a-z0-9-]*$")


def read_frontmatter_name(skill_file: Path) -> str:
    """Return the frontmatter `name` from a skill file."""
    content = skill_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"(?m)^name:\s*(.+)$", content)
    return match.group(1).strip() if match else ""


def load_skill_families(root: Path) -> list[dict[str, Any]]:
    """Return normalized command-family definitions from arcana.json."""
    metadata = json.loads((root / "arcana.json").read_text(encoding="utf-8"))
    default_prefix = metadata.get("skill_prefix", "arc")
    raw_families = metadata.get("skill_families", {})
    if not isinstance(raw_families, dict):
        return []

    families = []
    for name, config in raw_families.items():
        if not isinstance(config, dict):
            continue
        families.append({
            "name": name,
            "skill_prefix": config.get("skill_prefix", default_prefix),
            "path": root / config.get("path", ""),
        })
    return families


def discover_skill_commands(root: Path) -> dict[str, dict[str, str]]:
    """Return every Arcana-shipped public command keyed by slash command."""
    commands: dict[str, dict[str, str]] = {}
    for family in load_skill_families(root):
        family_dir = family["path"]
        if not family_dir.is_dir():
            continue
        for skill_file in sorted(family_dir.glob("*/SKILL.md")):
            templated_name = read_frontmatter_name(skill_file)
            if not templated_name:
                continue
            command = "/" + templated_name.replace(
                SKILL_PREFIX_PLACEHOLDER,
                family["skill_prefix"],
            )
            commands[command] = {
                "family": family["name"],
                "skill_source": skill_file.relative_to(root).as_posix(),
            }
    return commands


def load_command_surface(root: Path) -> dict[str, Any]:
    """Load the command-surface contract JSON."""
    return json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))


def command_entries(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """Return command entries from the contract, or an empty list."""
    entries = contract.get("commands", [])
    return entries if isinstance(entries, list) else []


def validate_command_surface(root: Path) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Return the loaded contract and structured validation errors."""
    errors: list[dict[str, Any]] = []

    try:
        contract = load_command_surface(root)
    except (OSError, json.JSONDecodeError) as exc:
        return None, [{
            "code": "COMMAND_SURFACE_READ",
            "message": f"could not read command-surface contract: {exc}",
            "path": CONTRACT_PATH.as_posix(),
            "hint": "Create valid JSON at rites/data/command_surface.json.",
        }]

    if contract.get("schema_version") != 1:
        errors.append({
            "code": "COMMAND_SURFACE_SCHEMA",
            "message": "command-surface contract must declare schema_version 1",
            "path": CONTRACT_PATH.as_posix(),
            "hint": "Set schema_version to 1.",
        })

    entries = command_entries(contract)
    if not isinstance(contract.get("commands"), list):
        errors.append({
            "code": "COMMAND_SURFACE_COMMANDS",
            "message": "command-surface contract must contain a commands list",
            "path": CONTRACT_PATH.as_posix(),
            "hint": "Add a top-level commands array.",
        })

    discovered = discover_skill_commands(root)
    seen: dict[str, int] = {}

    for index, entry in enumerate(entries):
        path = f"{CONTRACT_PATH.as_posix()}#/commands/{index}"
        if not isinstance(entry, dict):
            errors.append({
                "code": "COMMAND_SURFACE_ENTRY",
                "message": "command-surface entry must be an object",
                "path": path,
                "hint": "Replace this entry with an object keyed by command metadata.",
            })
            continue

        command = entry.get("command")
        if isinstance(command, str):
            seen[command] = seen.get(command, 0) + 1
        else:
            command = f"<entry {index}>"

        missing_strings = [
            field
            for field in sorted(REQUIRED_STRING_FIELDS)
            if not isinstance(entry.get(field), str) or not entry.get(field).strip()
        ]
        for field in missing_strings:
            errors.append({
                "code": "COMMAND_SURFACE_FIELD",
                "message": f"{command} must declare non-empty {field}",
                "path": path,
                "hint": f"Add {field} to the command-surface entry.",
            })

        for field in sorted(REQUIRED_LIST_FIELDS):
            value = entry.get(field)
            if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
                errors.append({
                    "code": "COMMAND_SURFACE_FIELD",
                    "message": f"{command} must declare non-empty string items in {field}",
                    "path": path,
                    "hint": f"Set {field} to a list of precondition strings.",
                })

        if isinstance(entry.get("command"), str) and not COMMAND_RE.match(entry["command"]):
            errors.append({
                "code": "COMMAND_SURFACE_COMMAND",
                "message": f"{entry['command']} is not a valid slash-command name",
                "path": path,
                "hint": "Use /<prefix>-<kebab-slug>.",
            })

        owner_type = entry.get("owner_type")
        if isinstance(owner_type, str) and owner_type not in ALLOWED_OWNER_TYPES:
            errors.append({
                "code": "COMMAND_SURFACE_OWNER_TYPE",
                "message": f"{command} uses unsupported owner_type {owner_type}",
                "path": path,
                "hint": f"Use one of: {', '.join(sorted(ALLOWED_OWNER_TYPES))}.",
            })

        mutation_profile = entry.get("mutation_profile")
        if isinstance(mutation_profile, str) and mutation_profile not in ALLOWED_MUTATION_PROFILES:
            errors.append({
                "code": "COMMAND_SURFACE_MUTATION_PROFILE",
                "message": f"{command} uses unsupported mutation_profile {mutation_profile}",
                "path": path,
                "hint": f"Use one of: {', '.join(sorted(ALLOWED_MUTATION_PROFILES))}.",
            })

        for field in ("skill_source", "invocation"):
            value = entry.get(field)
            if isinstance(value, str) and value.strip():
                candidate = root / value
                if not candidate.exists():
                    errors.append({
                        "code": "COMMAND_SURFACE_PATH",
                        "message": f"{command} {field} does not exist: {value}",
                        "path": path,
                        "hint": "Point the contract at an existing repository-relative path.",
                    })

        for field in sorted(OPTIONAL_PATH_FIELDS):
            value = entry.get(field)
            if value is None:
                continue
            if not isinstance(value, str) or not value.strip():
                errors.append({
                    "code": "COMMAND_SURFACE_FIELD",
                    "message": f"{command} {field} must be null or a non-empty path",
                    "path": path,
                    "hint": f"Set {field} to null when no {field} exists.",
                })
                continue
            if not (root / value).exists():
                errors.append({
                    "code": "COMMAND_SURFACE_PATH",
                    "message": f"{command} {field} does not exist: {value}",
                    "path": path,
                    "hint": "Point the contract at an existing repository-relative path.",
                })

        discovered_entry = discovered.get(entry.get("command"))
        if discovered_entry:
            if entry.get("family") != discovered_entry["family"]:
                errors.append({
                    "code": "COMMAND_SURFACE_FAMILY",
                    "message": f"{command} family must be {discovered_entry['family']}",
                    "path": path,
                    "hint": "Match the family declared by arcana.json.",
                })
            if entry.get("skill_source") != discovered_entry["skill_source"]:
                errors.append({
                    "code": "COMMAND_SURFACE_SKILL_SOURCE",
                    "message": f"{command} skill_source must be {discovered_entry['skill_source']}",
                    "path": path,
                    "hint": "Match the discovered SKILL.md path.",
                })

    for command, count in sorted(seen.items()):
        if count > 1:
            errors.append({
                "code": "COMMAND_SURFACE_DUPLICATE",
                "message": f"{command} appears {count} times in the command-surface contract",
                "path": CONTRACT_PATH.as_posix(),
                "hint": "Keep exactly one command entry per public skill.",
            })

    contract_commands = set(seen)
    discovered_commands = set(discovered)
    for command in sorted(discovered_commands - contract_commands):
        errors.append({
            "code": "COMMAND_SURFACE_MISSING",
            "message": f"{command} is missing from the command-surface contract",
            "path": CONTRACT_PATH.as_posix(),
            "hint": "Add a command-surface entry for this skill.",
        })
    for command in sorted(contract_commands - discovered_commands):
        errors.append({
            "code": "COMMAND_SURFACE_EXTRA",
            "message": f"{command} is not backed by an Arcana-shipped SKILL.md",
            "path": CONTRACT_PATH.as_posix(),
            "hint": "Create the skill or remove this command entry.",
        })

    return contract, errors
