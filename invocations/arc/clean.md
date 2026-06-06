---
type: playbook
title: "Clean Workspace Artifacts"
aliases: ["workspace-clean", "clean-artifacts"]
tags: [arcana/invocations, type/playbook, scope/arcana]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Clean Workspace Artifacts

## Purpose

Remove the temporary artifacts the validator orchestrator writes under Arcana's `rites/.artifacts`.

## Invocation

```
/arc-clean
```

## Workflow

Mutation profile: `plan_apply` via `rites/clean_artifacts.py`. This
invocation may apply directly because it removes only managed transient
artifact directories; use `--dry-run` when the user asks to preview removals.

### 1. Run the cleanup rite

```bash
python3 ARCANA_HOME/rites/clean_artifacts.py
```

On Windows, use `python` instead of `python3`.

### 2. Report the result

Show what was cleaned.

### 3. Preview mode

If the user wants to preview without deleting:

```bash
python3 ARCANA_HOME/rites/clean_artifacts.py --dry-run
```

## Related

- Arcana maintenance: [[invocations/arc/arc|arc]]
