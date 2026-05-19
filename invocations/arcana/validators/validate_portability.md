---
type: reference
title: "Validate Portability"
aliases: ["validate-portability", "validate-windows-paths"]
tags: [arcana/invocations, type/reference, scope/quality]
authority: grimoire
last_verified: 2026-05-19
---

# Validate Portability

## Purpose

Detect filesystem-portability violations in any grimoire path — specifically the characters and naming patterns that fail on Windows. Catching these at validation time prevents a `git checkout` failure on the first Windows consumer who tries to clone the grimoire (a failure that leaves a partial working tree and which subsequent clones silently inherit).

## Invocation

```
/grm-arcana-validate-portability
```

Or directly:

```bash
python3 GRIMOIRE_ARCANA/rites/validate_portability.py [--grimoire <path>]
```

## What it rejects

1. **Windows-reserved characters in any path segment**: `<`, `>`, `:`, `"`, `|`, `?`, `*`. These are filename-illegal on Windows (the OS rejects them at the filesystem layer). Forward slash `/` and backslash `\` are also reserved but are path separators, not filename characters, so they're not flagged.
2. **Windows reserved basenames** (case-insensitive, with or without extension): `CON`, `PRN`, `AUX`, `NUL`, `COM1`-`COM9`, `LPT1`-`LPT9`. These map to historical device handles and cannot be used as file or directory names on Windows.
3. **Trailing dot or space** in a path segment. Windows silently strips trailing dots and spaces from filenames, causing checkout mismatches.

The scan walks every path under the grimoire root, skipping `.git/` (which is not part of the working-tree distribution).

## Why this matters

When `git clone` on Windows hits an invalid path during checkout, it aborts with:

```
error: invalid path '<path>'
fatal: unable to checkout working tree
warning: Clone succeeded, but checkout failed.
```

The `.git/` directory is left in place. Any subsequent `git pull` or `git fetch` against that directory succeeds (no fetch error), but the working tree stays partial. The summon rite's "already installed — pulling latest" path sees `.git/` exists and reports success, masking the underlying problem.

The cheap fix is to catch the bad path before it ever lands in the repository.

## When to run

- As part of the full validator suite (`/grm-arcana-validate-all`).
- Before pushing a chapter that introduces placeholder-driven template files.
- After bulk renames or template scaffolding.
- After ingesting external content whose filenames you don't control.

## Resolutions

For each violation, two paths:

1. **Rename to a portable equivalent.** For placeholders, prefer curly braces (`{target_app}` instead of `<target_app>`) — they're cross-platform safe and visually similar. For optional placeholder segments, use an `_opt` suffix in the placeholder name (`{variant_opt}` instead of `<variant?>`).
2. **Remove the offending file.** If the bad name was unintentional (e.g., a Windows-illegal name from an external import), delete it.

Do not work around the validator by suppressing the warning — the path *will* break on Windows.

## Related

- Full validator suite hub: [[invocations/arcana/validators/validators|validators]]
- Aggregate runner: [[invocations/arcana/validators/validate_all|validate_all]]
- Naming convention validator (snake_case / kebab-case): [[invocations/arcana/validators/validate_naming|validate_naming]]
