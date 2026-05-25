---
name: {{SKILL_PREFIX}}-help
description: Display the Arcana skill catalog and installed grimoire skill guide
when_to_use: User asks what Arcana skills exist, what commands are available, or how to discover the system. Run this before suggesting any specific skill if the user is new or unfamiliar. Also good when user asks "what can Arcana do", "what can Grimoire do", or "list grimoire commands".
user-invocable: true
allowed-tools: Bash Read
---

# Arcana Help

You are displaying the Arcana skill catalog plus any skills installed by registered grimoires.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Canonical Arcana skill catalog**: `{{ARCANA_PATH}}/docs/skills.md` (auto-generated from `skills/<slug>/SKILL.md`)
- **Grimoire library**: `~/grimoires/library.json`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/meta/help.md`
