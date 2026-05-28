---
type: reference
title: "Validate Grimoire All"
aliases: ["validate-grimoire-all", "grimoire-validate-all"]
tags: [arcana/invocations, type/reference, scope/grimoire, scope/validators]
authority: grimoire
last_verified: 2026-05-25
---

# Validate Grimoire (All)

## Purpose

Run the full deterministic validator profile against the active grimoire. Use
this before commits, after broad grimoire edits, after Arcana scaffold updates,
and before deciding whether the grimoire needs judgment workflows such as
`/grm-improve`, `/grm-lint`, or `/grm-analyze-semantics`.

This command is mechanical and read-only. It excludes judgment passes such as
boundary review and semantic analysis.

## Invocation

```
/grm-validate-all
```

## Preconditions

!`cat ARCANA_HOME/invocations/meta/grimoire_directory_guard.md`

## Mechanical Equivalent

```bash
python3 ARCANA_HOME/rites/validate.py --grimoire GRIMOIRE_ROOT
python3 ARCANA_HOME/rites/validate.py --grimoire GRIMOIRE_ROOT --format json
```

On Windows, use `python` instead of `python3`.

## Profile

The grimoire profile runs:

- `validate_grimoire_structure.py`
- `validate_encoding.py`
- `validate_portability.py`
- `validate_format.py`
- `validate_frontmatter.py`
- `validate_links.py`
- `validate_orphans.py`
- `validate_provenance.py`
- `validate_doc_trees.py`

## Workflow

1. Resolve the active grimoire through the shared guard.
2. Run the orchestrator with `--grimoire GRIMOIRE_ROOT`.
3. Use `--parallel` for a faster full pass when concise output is enough.
4. Use `--summary` for pass/fail status per validator.
5. Use `--format json` or `--format jsonl` when another rite or CI needs
   structured diagnostics.
6. If a validator fails, route to that validator's invocation leaf for fix
   guidance, then re-run `/grm-validate-all`.

## Related

- Validators hub: [[invocations/grimoire/validators/validators|validators]]
- Orchestrator rite: [`../../../rites/validate.py`](../../../rites/validate.py)
- Structure validator: [[invocations/grimoire/validate_structure|validate structure]]
- Grimoire improvement: [[invocations/grimoire/improve_grimoire|improve grimoire]]
