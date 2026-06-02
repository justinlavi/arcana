---
name: {{SKILL_PREFIX}}-restore
description: Restore Arcana (and any grimoire) to a current, validated, synchronized state
when_to_use: An Arcana maintainer or fork owner wants to bring an Arcana install — engine, library, agent skills, agent block — and any grimoire back to a current, validated, synchronized state; skills are missing/old/renamed; or the user asks to "restore". Mirror of /grm-restore (the grimoire-user entry point).
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Restore

You are restoring an Arcana install (and any grimoire that references it) back to a current, validated, synchronized state.

## Context

- **Canonical procedure**: `{{ARCANA_PATH}}/RESTORATION.md` — the skill-less source of truth for restoration. It still works when installed skills are stale.
- **Arcana**: `{{ARCANA_PATH}}`
- **Grimoire library**: `~/grimoires/library.json`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/arcana/restore.md`
