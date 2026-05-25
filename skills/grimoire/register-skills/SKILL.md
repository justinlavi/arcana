---
name: {{SKILL_PREFIX}}-register-skills
description: Register Arcana skills and the active grimoire's own skills into supported agent skill directories
when_to_use: User added, renamed, or edited skills in the active grimoire; a grimoire-owned slash command is missing; user asks to register or refresh this grimoire's skills; user wants to update skill registration while working inside one grimoire.
user-invocable: true
allowed-tools: Bash Read
---

# Register Active Grimoire Skills

You are registering Arcana skills and the active grimoire's own skills into supported agent skill directories.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Active grimoire**: resolve from `~/grimoires/library.json`; cwd does not have to be the grimoire root
- **Invocation**: `{{ARCANA_PATH}}/invocations/grimoire/register_skills.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/register_skills.md`
