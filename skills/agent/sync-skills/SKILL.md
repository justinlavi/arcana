---
name: {{SKILL_PREFIX}}-agent-sync-skills
description: Sync Arcana skills and installed grimoire skills into supported agent skill directories
when_to_use: A skill isn't appearing in the slash-command picker; user just added, renamed, or edited a SKILL.md; user installed a new grimoire; user mentions "skill not recognized" or "after editing skills". Run after any change in skills/ that the agent needs to pick up.
user-invocable: true
allowed-tools: Bash Read
---

# Sync Agent Skills

You are syncing Arcana skills and every installed grimoire's skills into supported agent skill directories.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Invocation**: `{{ARCANA_PATH}}/invocations/agent/sync_skills.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/agent/sync_skills.md`
