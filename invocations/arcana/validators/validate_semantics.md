---
type: reference
title: "Validate Semantics"
aliases: ["validate-semantics"]
tags: [arcana/invocations, type/reference, scope/validators]
authority: grimoire
last_verified: 2026-05-15
---

# Invocation: Validate Arcana Semantics

## Purpose

Mechanical scan of Arcana for **hyphenated path examples** written in prose. Fast, deterministic, no judgment required.

For *intelligent* semantic analysis (naming quality, organizational discoverability, terminology design), use `/grm-analyze-semantics` - this rite is intentionally not that. Filename validation lives in [[invocations/arcana/validators/validate_naming|validate naming]].

## Invocation

```
/arc-validate-semantics
```

Also runs as part of `/arc-improve` (alongside the other validators).

## What the Rite Checks

The rite is `rites/validate_semantics.py`.

**Hyphenated path examples** - paths like `chapters/example-name/` or `file-name.md` written in markdown body text are flagged. Arcana convention is `snake_case` for filesystem paths. Headings and code fences are exempt; the check applies only to prose lines that aren't headers.

## Workflow

```bash
python3 rites/validate_semantics.py
```

Exit code: 0 if no violations, 1 if any violation is found.

## Exclusions

- `validate_semantics.md` (this file)
- `validate_naming.md` (documents naming-violation examples)
- `script_vs_ai.md` (demos validator behavior)
- `invocations/arcana/quality/` (quality docs may discuss historical terms)
- `sources/` (imported source artifacts may have hyphens in their original names)

## Fixing Violations

Convert each hyphenated example to snake_case (`chapters/example_name/`, `file_name.md`). If the path appears inside a code block, no fix is needed - only prose lines are flagged.

## Related

- **Rite**: [`rites/validate_semantics.py`](../../../rites/validate_semantics.py)
- **Naming counterpart**: [[invocations/arcana/validators/validate_naming|validate naming]] (snake_case enforcement on actual filenames)
- **Smart analysis**: `/grm-analyze-semantics` (judgment-based, not mechanical)
- **Orchestrator**: [[invocations/arcana/improve_arcana|improve arcana]]
