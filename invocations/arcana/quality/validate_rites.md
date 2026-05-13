---
type: playbook
title: "Validate Rites"
aliases: ["validate-rites", "rite-quality"]
tags: [arcana/invocations, type/playbook, scope/quality]
authority: grimoire
last_verified: 2026-05-12
---

# Invocation: Validate Arcana Rites

## Purpose

Judgment-based quality review of rite scripts (Python files under `rites/`). Covers error handling, exit codes, idempotency, portability, docstrings, and size limits.

Pairs with `/grm-arcana-validate-security` (mechanical credential/unsafe-construct scan). This invocation is the human-judgment counterpart — no rite automates it. See [`docs/script_vs_ai.md`](../../../docs/script_vs_ai.md) for the split.

## Invocation

Runs as a phase of `/grm-arcana-improve`. No standalone slash command.

## When to cast

- After creating or modifying a rite
- Before an Arcana release
- During `/grm-arcana-improve`

## Workflow

### 1. Inventory

```bash
ls rites/*.py
```

Skip `__pycache__/`, `data/`, `templates/`. Treat `validate_*.py`, `sync_*.py`, and orchestrators (`validate.py`, `summon.py`, `register_skills.py`) as in scope.

### 2. Per-rite checks

Read each rite top-to-bottom and judge:

**Docstring**
- Module docstring present, one-line summary first
- States purpose, usage (`python3 rites/<name>.py [args]`), and exit codes
- Non-obvious behaviour (env vars consumed, paths written, side effects) called out

**Error handling**
- No bare `except:` — catch specific exceptions
- File I/O wrapped or guarded; missing files produce a clear message, not a traceback
- Subprocess calls check return codes (`subprocess.run(..., check=True)` or explicit branching)
- External tool absence (e.g. `git`, `python3 -m`) degrades gracefully or fails with a remediation hint

**Exit codes**
- `0` = clean / success
- `1` = violations found or recoverable failure
- `2` (optional) = misuse / bad arguments
- Documented in the docstring; `sys.exit(...)` called explicitly, not implicit

**Idempotency**
- Re-running on an unchanged tree produces identical output and exit code
- Mutating rites (`sync_library.py`, `sync_docs.py`, `register_skills.py`) support a dry-run / `--apply` split or are obviously read-only when not given a flag
- No accumulating side effects (appending to logs without rotation, etc.)

**Portability**
- Resolves Arcana root via `GRIMOIRE_ARCANA` env var with a sensible fallback (see existing rites for the pattern)
- No hard-coded `/home/...` or user-specific paths
- Uses `pathlib.Path` rather than string concatenation
- No GNU-only CLI flags via subprocess (`grep -P`, `sed -i ''` differences) without a fallback

**Size**
- Soft cap: 300 lines per rite. If larger, look for extractable helpers or data files (see `rites/data/` for the data-driven pattern used by `validate_semantics.py`)
- Functions: prefer < 50 lines

### 3. Output style

Rite stdout should be greppable and consistent across the suite:

- File issues printed as `path:line: message` (so editors can jump to them)
- Final summary line, e.g. `3 violations in 2 files` or `OK`
- Paths relative to Arcana root, not absolute
- Plain ASCII for machine-readable output; emoji acceptable in summary lines only

### 4. Compact good/bad reference

```python
# Bad: silent failure, opaque exit, absolute path
try:
    data = open("/home/me/grimoire/foo.md").read()
except:
    pass
```

```python
# Good: explicit, relative, documented
"""Validate foo. Exit 0 clean, 1 on violations."""
path = ARCANA_ROOT / "foo.md"
if not path.exists():
    print(f"{path.relative_to(ARCANA_ROOT)}: missing", file=sys.stderr)
    sys.exit(1)
```

### 5. Apply fixes

For each issue, edit the rite, re-run it on a clean tree to confirm exit 0, then re-run on a known-bad fixture (or temporary violation) to confirm exit 1. Run `/grm-arcana-validate-all` afterward to make sure nothing else regressed.

## What this invocation is NOT

- Not a security scan — that's `/grm-arcana-validate-security`
- Not a structural / naming / link / format check — those are separate `/grm-arcana-validate-*` rites
- Not a benchmark suite. If a rite feels slow, profile it; otherwise leave performance alone

## Related

- **Security scan**: [`../validators/validate_security.md`](../validators/validate_security.md)
- **Validator suite**: `/grm-arcana-validate-all`
- **Script vs AI split**: [`../../../docs/script_vs_ai.md`](../../../docs/script_vs_ai.md)
- **Rites directory**: [`rites/`](../../../rites/)
- **Orchestrator**: [`../improve_arcana.md`](../improve_arcana.md)
