---
name: {{NAMESPACE}}-domain-validate-structure
description: Validate grimoire structure compliance against Arcana formulae
when_to_use: User asks if their grimoire is correctly structured, after creating or restructuring chapters, before committing grimoire changes, or as a quick sanity check. Mechanical/deterministic — no judgment. For Arcana itself, use /grm-arcana-validate-structure.
user-invocable: true
allowed-tools: Bash Read
---

# Validate Structure

You are validating grimoire structure compliance. Follow the invocation guide below.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Chapter formula**: `{{ARCANA_PATH}}/formulae/chapter_hub.formula.md`
- **Page formula**: `{{ARCANA_PATH}}/formulae/page.formula.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/validate_structure.md`
