#!/usr/bin/env python3
"""Load and validate Arcana's mutating-rite profile contract."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

CONTRACT_PATH = Path("rites/data/rite_profiles.json")
ALLOWED_PROFILES = {"read_only", "plan_apply", "apply_only", "append_only"}
REQUIRED_STRING_FIELDS = {
    "path",
    "profile",
    "default_mode",
    "apply_command",
    "idempotency",
    "validation_profile",
}
REQUIRED_LIST_FIELDS = {"writes", "tests"}


_MUTATING_ATTRS = {
    "write_text", "write_bytes", "mkdir", "unlink", "rmtree", "copyfile", "copytree",
}
_OS_MUTATORS = {
    "replace", "rename", "remove", "removedirs", "makedirs", "mkdir", "rmdir",
    "symlink", "link", "write", "truncate",
}
_SHUTIL_MUTATORS = {"move", "copy", "copy2", "copyfile", "copytree", "rmtree"}
_PATH_MOVE_ATTRS = {"replace", "rename"}


class _WriteVisitor(ast.NodeVisitor):
    """Detect obvious file-system writes in a Python rite."""

    mutates = False

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Attribute):
            attr = func.attr
            if attr in _MUTATING_ATTRS:
                self.mutates = True
            elif attr == "open" and _mode_arg_writes(node):
                self.mutates = True
            elif _is_module_call(func, "os") and attr in _OS_MUTATORS:
                self.mutates = True
            elif _is_module_call(func, "shutil") and attr in _SHUTIL_MUTATORS:
                self.mutates = True
            elif attr in _PATH_MOVE_ATTRS and _is_single_positional(node):
                # Path.replace(target) / Path.rename(target); str.replace takes 2 args.
                self.mutates = True
        elif isinstance(func, ast.Name):
            if func.id == "open" and _mode_arg_writes(node):
                self.mutates = True
        self.generic_visit(node)


def _mode_arg_writes(node: ast.Call) -> bool:
    """Return True when an open-like call has a write/append/create mode."""
    mode: str | None = None
    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
        mode = node.args[1].value
    for keyword in node.keywords:
        if keyword.arg == "mode" and isinstance(keyword.value, ast.Constant):
            mode = keyword.value.value
    return isinstance(mode, str) and any(flag in mode for flag in ("w", "a", "x"))


def _is_module_call(func: ast.Attribute, module: str) -> bool:
    """True when an attribute call's receiver is the named module (e.g. os.rename)."""
    return isinstance(func.value, ast.Name) and func.value.id == module


def _is_single_positional(node: ast.Call) -> bool:
    """True when a call has exactly one positional arg and no keyword/star args.

    Distinguishes the file-system `Path.replace(target)` / `Path.rename(target)`
    from `str.replace(old, new)`, which takes two arguments.
    """
    return (
        len(node.args) == 1
        and not node.keywords
        and not any(isinstance(arg, ast.Starred) for arg in node.args)
    )


def load_rite_profiles(root: Path) -> dict[str, Any]:
    """Load the rite-profile contract JSON."""
    return json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))


def profile_entries(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """Return profile entries from the contract, or an empty list."""
    entries = contract.get("profiles", [])
    return entries if isinstance(entries, list) else []


def discover_write_capable_rites(root: Path) -> set[str]:
    """Return top-level rites that contain obvious write operations."""
    discovered: set[str] = set()
    for path in sorted((root / "rites").iterdir()):
        if path.parent.name != "rites" or path.name.startswith("_"):
            continue
        if path.suffix == ".py" and _python_rite_writes(path):
            discovered.add(path.relative_to(root).as_posix())
        elif path.suffix == ".sh" and _shell_rite_writes(path):
            discovered.add(path.relative_to(root).as_posix())
    return discovered


def _python_rite_writes(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return False
    visitor = _WriteVisitor()
    visitor.visit(tree)
    return visitor.mutates


def _shell_rite_writes(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    write_markers = (
        "git clone",
        "mkdir ",
        "mkdir -p",
        "rm -",
        "> ",
        'open(dest, "wb")',
    )
    return any(marker in text for marker in write_markers)


def validate_rite_profiles(root: Path) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    """Return the loaded contract and structured validation errors."""
    try:
        contract = load_rite_profiles(root)
    except (OSError, json.JSONDecodeError) as exc:
        return None, [{
            "code": "RITE_PROFILE_READ",
            "message": f"could not read rite-profile contract: {exc}",
            "path": CONTRACT_PATH.as_posix(),
            "hint": "Create valid JSON at rites/data/rite_profiles.json.",
        }]

    errors: list[dict[str, str]] = []
    if contract.get("schema_version") != 1:
        errors.append({
            "code": "RITE_PROFILE_SCHEMA",
            "message": "rite-profile contract must declare schema_version 1",
            "path": CONTRACT_PATH.as_posix(),
            "hint": "Set schema_version to 1.",
        })

    entries = profile_entries(contract)
    if not isinstance(contract.get("profiles"), list):
        errors.append({
            "code": "RITE_PROFILE_PROFILES",
            "message": "rite-profile contract must contain a profiles list",
            "path": CONTRACT_PATH.as_posix(),
            "hint": "Add a top-level profiles array.",
        })

    seen: dict[str, int] = {}
    for index, entry in enumerate(entries):
        entry_path = f"{CONTRACT_PATH.as_posix()}#/profiles/{index}"
        if not isinstance(entry, dict):
            errors.append({
                "code": "RITE_PROFILE_ENTRY",
                "message": "rite-profile entry must be an object",
                "path": entry_path,
                "hint": "Replace this entry with an object keyed by rite metadata.",
            })
            continue

        path_value = entry.get("path")
        if isinstance(path_value, str):
            seen[path_value] = seen.get(path_value, 0) + 1
        else:
            path_value = f"<entry {index}>"

        for field in sorted(REQUIRED_STRING_FIELDS):
            value = entry.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append({
                    "code": "RITE_PROFILE_FIELD",
                    "message": f"{path_value} must declare non-empty {field}",
                    "path": entry_path,
                    "hint": f"Add {field} to the rite-profile entry.",
                })

        for field in sorted(REQUIRED_LIST_FIELDS):
            value = entry.get(field)
            if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
                errors.append({
                    "code": "RITE_PROFILE_FIELD",
                    "message": f"{path_value} must declare non-empty string items in {field}",
                    "path": entry_path,
                    "hint": f"Set {field} to a list of strings.",
                })

        plan_command = entry.get("plan_command")
        if plan_command is not None and (not isinstance(plan_command, str) or not plan_command.strip()):
            errors.append({
                "code": "RITE_PROFILE_FIELD",
                "message": f"{path_value} plan_command must be null or a non-empty string",
                "path": entry_path,
                "hint": "Use null when a rite has no plan mode.",
            })

        profile = entry.get("profile")
        if isinstance(profile, str) and profile not in ALLOWED_PROFILES:
            errors.append({
                "code": "RITE_PROFILE_KIND",
                "message": f"{path_value} uses unsupported profile {profile}",
                "path": entry_path,
                "hint": f"Use one of: {', '.join(sorted(ALLOWED_PROFILES))}.",
            })

        if isinstance(entry.get("path"), str) and not (root / entry["path"]).exists():
            errors.append({
                "code": "RITE_PROFILE_PATH",
                "message": f"{entry['path']} does not exist",
                "path": entry_path,
                "hint": "Point the profile at an existing repository-relative path.",
            })

        if profile == "plan_apply" and not isinstance(plan_command, str):
            errors.append({
                "code": "RITE_PROFILE_PLAN",
                "message": f"{path_value} is plan_apply but has no plan_command",
                "path": entry_path,
                "hint": "Declare the dry-run or planning command.",
            })

    for path_value, count in sorted(seen.items()):
        if count > 1:
            errors.append({
                "code": "RITE_PROFILE_DUPLICATE",
                "message": f"{path_value} appears {count} times in the rite-profile contract",
                "path": CONTRACT_PATH.as_posix(),
                "hint": "Keep exactly one profile entry per rite.",
            })

    contract_paths = set(seen)
    discovered_paths = discover_write_capable_rites(root)
    for path_value in sorted(discovered_paths - contract_paths):
        errors.append({
            "code": "RITE_PROFILE_MISSING",
            "message": f"{path_value} contains write operations but has no rite profile",
            "path": CONTRACT_PATH.as_posix(),
            "hint": "Add a rite-profile entry or move the write behind an existing profiled rite.",
        })
    for path_value in sorted(contract_paths - discovered_paths):
        errors.append({
            "code": "RITE_PROFILE_EXTRA",
            "message": f"{path_value} has a write-capable profile but no write operations were detected",
            "path": CONTRACT_PATH.as_posix(),
            "hint": "Remove the profile entry or update the write-operation detector.",
        })

    return contract, errors
