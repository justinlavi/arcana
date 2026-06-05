---
name: {{SKILL_PREFIX}}-workspace-clean
description: Remove temporary rite artifacts under Arcana's rites/.artifacts
when_to_use: rites/.artifacts has accumulated transient validator output; before committing Arcana changes; user asks to clean up workspace artifacts.
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
