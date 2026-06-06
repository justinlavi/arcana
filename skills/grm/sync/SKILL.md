---
name: {{SKILL_PREFIX}}-sync
description: Reconcile your local Grimoire setup with reality - register skills, fix the library after you move or rename a grimoire folder, and repair the agent routing block
when_to_use: A grimoire-owned slash command is missing or you added/renamed skills (skills); you moved or renamed a grimoire folder and the agent can't find it (library); your agent stopped recognizing /grm- commands or its routing block is stale or missing (agentfile). Run bare to reconcile all three, or with one sub-target. This is the everyday user mirror of /arc-sync.
argument-hint: "[skills | library | agentfile]"
arguments: target
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Sync Active Grimoire Setup

You are reconciling the user's local Grimoire setup with reality: skills, the library, and the agent routing block. Resolve the optional positional sub-target `$target`; with no sub-target, run all three.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Active grimoire**: resolve from `~/grimoires/library.json`; cwd does not have to be the grimoire root
- **Invocation**: `{{ARCANA_PATH}}/invocations/grm/sync.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/sync.md`
