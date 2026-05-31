---
name: {{SKILL_PREFIX}}-validate-format
description: Validate Markdown formatting in the active grimoire
when_to_use: User asks whether grimoire Markdown is well-formed; after editing tables, code fences, or directory tree examples; before committing grimoire changes.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Grimoire Format

You are validating portable Markdown formatting in the active grimoire.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/validators/validate_format.md`
