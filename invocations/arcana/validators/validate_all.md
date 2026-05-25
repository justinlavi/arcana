---
type: reference
title: "Validate Arcana All"
aliases: ["validate-all", "arcana-validate-all"]
tags: [arcana/invocations, type/reference, scope/validators]
authority: grimoire
last_verified: 2026-05-25
---

# Validate Arcana (All)

## Purpose

Run the full Arcana validator suite through the orchestrator rite. Use this
before commits, releases, broad documentation edits, and `/arc-improve`.

## Invocation

```
/arc-validate-all
```

Mechanical equivalent:

```bash
python3 ARCANA_HOME/rites/validate.py
python3 ARCANA_HOME/rites/validate.py --format json
```

On Windows, use `python` instead of `python3`.

## Workflow

1. Prefer the orchestrator over running individual validators manually.
2. Choose the mode that matches the task:
   - `--parallel` - run all validators concurrently.
   - `--summary` - show only pass/fail status per validator.
   - `--smart` - inspect git changes and list relevant validators.
   - `--auto` - run the validators selected by `--smart`.
   - `--format json` or `--format jsonl` - emit structured diagnostics.
3. Report aggregate pass/fail status and the failing validator names.
4. If a validator fails, route to that validator's invocation leaf for fix
   guidance, then re-run the orchestrator.

## Related

- Validators hub: [`validators.md`](validators.md)
- Orchestrator rite: [`../../../rites/validate.py`](../../../rites/validate.py)
- Architecture review: [`../quality/review_architecture.md`](../quality/review_architecture.md)
