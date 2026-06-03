---
name: {{SKILL_PREFIX}}-update
description: Update Arcana (and every grimoire) to a current, validated, synchronized state
when_to_use: An Arcana maintainer or fork owner wants to bring an Arcana install — engine, library, agent skills, agent block — and every grimoire in the library back to a current, validated, synchronized state; skills are missing/old/renamed; or the user asks to "update". Mirror of /grm-update (the grimoire-user entry point).
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Update

You are updating an Arcana install (and every grimoire that references it) back to a current, validated, synchronized state.

## Context

- **Canonical procedure**: `{{ARCANA_PATH}}/UPDATE.md` — the skill-less source of truth for the update. It still works when installed skills are stale.
- **Arcana**: `{{ARCANA_PATH}}`
- **Grimoire library**: `~/grimoires/library.json`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/arcana/update.md`
