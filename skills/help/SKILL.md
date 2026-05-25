---
name: {{SKILL_PREFIX}}-help
description: Display the Grimoire skill catalog and usage guide
when_to_use: User asks what Grimoire skills exist, what commands are available, or how to discover the system. Run this before suggesting any specific skill if the user is new or unfamiliar. Also good when user asks "what can Grimoire do" or "list grimoire commands".
user-invocable: true
allowed-tools: Bash Read
---

# Grimoire Help

You are displaying the Grimoire skill catalog - Arcana's skills plus every grimoire's skills.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Canonical Arcana skill catalog**: `{{ARCANA_PATH}}/docs/skills.md` (auto-generated from `skills/<slug>/SKILL.md`)
- **Grimoire library**: `~/grimoires/library.json`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/meta/help.md`
