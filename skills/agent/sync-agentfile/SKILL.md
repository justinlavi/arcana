---
name: {{SKILL_PREFIX}}-sync-agentfile
description: Sync the Grimoire instruction block in user agent files while preserving non-Grimoire content
when_to_use: User asks to update, refresh, sync, repair, or reinstall the Grimoire block in AGENTS.md, CLAUDE.md, Copilot instructions, custom agent instructions, or other agent configuration files.
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Sync Agent Grimoire Instructions

You are refreshing the user's agent instruction files so their Grimoire block matches the current Arcana canonical block.

This is AI-guided file editing, not a blind script. Preserve all non-Grimoire instructions.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Canonical block**: `{{ARCANA_PATH}}/rites/templates/grimoire_block.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/agent/sync_agentfile.md`
