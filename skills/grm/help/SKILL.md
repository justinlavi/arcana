---
name: {{SKILL_PREFIX}}-help
description: Display the grimoire command catalog (/grm-*) and the active grimoire's own skills
when_to_use: Author working inside a grimoire asks what grimoire commands exist, how to operate on the active grimoire, or "what can I do here". Use when the user knows the /grm- prefix. For the full Arcana/platform catalog and every installed grimoire, use /arc-help.
user-invocable: true
allowed-tools: Bash Read
---

# Grimoire Help

You are showing the grimoire-author command catalog: the `/grm-*` operations that act on a grimoire, plus the active grimoire's own skills.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Canonical skill catalog**: `{{ARCANA_PATH}}/docs/skills.md` (auto-generated from `skills/<family>/<slug>/SKILL.md`)
- **Grimoire library**: `~/grimoires/library.json`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/help.md`
