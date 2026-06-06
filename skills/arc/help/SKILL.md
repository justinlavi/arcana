---
name: {{SKILL_PREFIX}}-help
description: Display the Arcana skill catalog and installed grimoire skill guide
when_to_use: Maintainer or power user wants the complete platform catalog - every /arc-* and /grm-* command plus every installed grimoire's own skills. Use when the user explicitly asks for the full Arcana platform catalog or all installed grimoires. For everyday grimoire-user help, use /grm-help.
user-invocable: true
allowed-tools: Bash Read
---

# Arcana Help

You are displaying the Arcana skill catalog plus any skills installed by registered grimoires.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Canonical Arcana skill catalog**: `{{ARCANA_PATH}}/docs/skills.md` (auto-generated from `skills/<family>/<slug>/SKILL.md`)
- **Grimoire library**: `~/grimoires/library.json`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/arc/help.md`
