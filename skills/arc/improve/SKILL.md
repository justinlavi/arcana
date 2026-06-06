---
name: {{SKILL_PREFIX}}-improve
description: Improve Arcana itself - maintainer only
when_to_use: The Arcana maintainer or fork owner wants to audit, normalize, and upgrade Arcana itself - its docs, invocations, formulae, rites, and skills; before cutting a release; after bulk changes. Maintainer-only; for a grimoire use /grm-update and /grm-health-check.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read Write Edit
---

# Improve Arcana

You are the Arcana maintainer performing a comprehensive improvement. Follow the invocation guide below exactly.

**Important**: This should be run from the Arcana directory: `{{ARCANA_PATH}}`

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Rites**: `{{ARCANA_PATH}}/rites/`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/arc/improve_arcana.md`
