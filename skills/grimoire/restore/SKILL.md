---
name: {{SKILL_PREFIX}}-restore
description: Restore the active grimoire and its Arcana to a current, validated, synchronized state
when_to_use: User wants to bring their grimoire and Arcana up to date; says Arcana or the grimoire may be stale, skills are missing/old/renamed, or asks to "restore" / "update everything". The one grimoire-side command to re-sync the engine, library, agent skills, agent block, and the active grimoire. Mirror of /arc-restore.
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Restore

You are restoring the active grimoire and the Arcana it references back to a current, validated, synchronized state, from the grimoire user's point of view.

## Context

- **Canonical procedure**: `{{ARCANA_PATH}}/RESTORATION.md` — the skill-less source of truth for restoration. It still works when installed skills are stale.
- **Arcana**: `{{ARCANA_PATH}}`
- **Active grimoire**: resolve from `~/grimoires/library.json`; cwd does not have to be the grimoire root

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/restore.md`
