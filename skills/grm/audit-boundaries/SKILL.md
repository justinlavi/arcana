---
name: {{SKILL_PREFIX}}-audit-boundaries
description: Advanced, opt-in check that a grimoire's pages don't reuse Arcana's internal command and system words (for maintainers and pre-release review)
when_to_use: Before publishing or releasing a grimoire; after restructuring chapters; during PR review of grimoire changes; user mentions "magical boundary", "system vs content terminology", or "is my grimoire using Arcana words it shouldn't".
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read Write Edit
---

# Audit Boundaries

You are auditing magical boundary compliance for the active grimoire. Follow the invocation guide below.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Reference**: `{{ARCANA_PATH}}/docs/reference.md` A "The Magical Boundary"

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/audit_boundaries.md`
