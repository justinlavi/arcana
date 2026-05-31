---
name: {{SKILL_PREFIX}}-validate-portability
description: Validate filesystem portability for paths in the active grimoire
when_to_use: User asks whether a grimoire will clone cleanly across Windows, Linux, and macOS; after adding or renaming files; before publishing or committing grimoire changes.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Grimoire Portability

You are validating filesystem portability for the active grimoire.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/validators/validate_portability.md`
