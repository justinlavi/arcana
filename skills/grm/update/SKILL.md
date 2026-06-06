---
name: {{SKILL_PREFIX}}-update
description: Update Arcana and every grimoire in the library to a current, validated, synchronized state
when_to_use: User wants to bring their grimoires and Arcana up to date; says Arcana or a grimoire may be stale, skills are missing/old/renamed, or asks to "update" / "update everything". The one grimoire-side command to pull and re-sync the engine, library, agent skills, agent block, and every grimoire. Mirror of /arc-update.
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Update

You are updating Arcana and every grimoire it manages back to a current, validated, synchronized state, from the grimoire user's point of view.

## Context

- **Canonical procedure**: `{{ARCANA_PATH}}/UPDATE.md` — the skill-less source of truth for the update. It still works when installed skills are stale.
- **Arcana**: `{{ARCANA_PATH}}`
- **Grimoire library**: `~/grimoires/library.json` — the update pulls and brings current every grimoire listed there, not only the one you are in

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/update.md`
