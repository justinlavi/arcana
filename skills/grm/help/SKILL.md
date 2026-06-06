---
name: {{SKILL_PREFIX}}-help
description: Display the grimoire command catalog (/grm-*) and the active grimoire's own skills
when_to_use: User asks what commands exist, what they can do here, how to operate the active grimoire, or "what can Grimoire do" / "list grimoire commands" / "what can I do". The everyday help command for grimoire users. For the full platform catalog across every installed grimoire, use /arc-help.
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
