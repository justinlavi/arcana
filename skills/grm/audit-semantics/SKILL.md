---
name: {{SKILL_PREFIX}}-audit-semantics
description: Advanced, opt-in review of page and chapter naming so things stay easy to find (a deeper pass than /grm-health-check's checkup)
when_to_use: User asks about naming quality, discoverability, or organization of a grimoire; user mentions chapter or page names feel awkward, redundant, or hard to find; user wants a judgment-based audit of naming and organization. Operates on the active grimoire.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read Write Edit
---

# Audit Semantics

You are performing a judgment-based semantic audit on the active grimoire. Follow the invocation guide below.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Reference**: `{{ARCANA_PATH}}/docs/reference.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/audit_semantics.md`
