---
name: {{SKILL_PREFIX}}-improve
description: Comprehensive grimoire upgrade and improvement - align with current Arcana, audit, normalize, and optimize the active grimoire
when_to_use: User asks to upgrade, update, audit, polish, improve, or review a grimoire; user pulled a newer Arcana version; user is preparing for a release; user mentions schema drift, scaffold drift, tech debt, or stale content in their grimoire. Operates on the *active* grimoire (must be cd'd into a registered grimoire). For Arcana itself, use /arc-improve instead.
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Improve Grimoire

You are performing a comprehensive improvement on the active grimoire. Follow the invocation guide below exactly.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/improve_grimoire.md`
