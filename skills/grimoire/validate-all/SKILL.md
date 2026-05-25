---
name: {{SKILL_PREFIX}}-validate-all
description: Run the full deterministic validator profile against the active grimoire
when_to_use: User asks to validate, audit, check, or health-check the active grimoire mechanically; before committing grimoire changes; after Arcana scaffold updates; before deciding whether deeper /grm-improve or /grm-lint judgment work is needed. Cheap and read-only.
user-invocable: true
allowed-tools: Bash Read
---

# Validate Grimoire (All)

You are running the full deterministic validator profile against the active grimoire. Follow the invocation guide below.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/validators/validate_all.md`
