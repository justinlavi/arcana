---
name: {{NAMESPACE}}-domain-improve
description: Comprehensive grimoire improvement — audit, normalize, and optimize the active domain grimoire
when_to_use: User asks to audit, polish, improve, or review a domain grimoire; user is preparing for a release; user mentions tech debt, drift, or stale content in their grimoire. Operates on the *active* grimoire (must be cd'd into a registered grimoire). For Arcana itself, use /grm-arcana-improve instead.
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Improve Grimoire

You are performing a comprehensive improvement on the active domain grimoire. Follow the invocation guide below exactly.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/improve_grimoire.md`
