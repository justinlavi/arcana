---
name: {{SKILL_PREFIX}}-update-arcana
description: Update Arcana, refresh agent integration, re-register skills, and check active-grimoire compatibility
when_to_use: User wants to update Arcana while working in a grimoire; user asks to pull the latest Arcana; user says Arcana may be stale; user wants one command to refresh the engine, agent skills, agent block, and current grimoire compatibility.
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Update Arcana

You are updating Arcana from the active grimoire user's point of view.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Active grimoire**: resolve from `~/grimoires/library.json`; cwd does not have to be the grimoire root
- **Invocation**: `{{ARCANA_PATH}}/invocations/grimoire/update_arcana.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/update_arcana.md`
