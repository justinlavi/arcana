---
name: {{SKILL_PREFIX}}-workspace-clean
description: Remove temporary rite artifacts under Arcana's rites/.artifacts
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash
---

# Clean Artifacts

You are cleaning up the temporary artifacts the validator orchestrator writes under Arcana's `rites/.artifacts`.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Invocation**: `{{ARCANA_PATH}}/invocations/workspace/clean.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/workspace/clean.md`
