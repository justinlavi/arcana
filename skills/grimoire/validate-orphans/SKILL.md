---
name: {{SKILL_PREFIX}}-validate-orphans
description: Detect orphan pages in the active grimoire
when_to_use: User asks whether grimoire pages are reachable; after moving, adding, or deleting grimoire pages; before committing grimoire changes.
user-invocable: true
allowed-tools: Bash Read
---

# Validate Grimoire Orphans

You are detecting orphan pages in the active grimoire.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/validators/validate_orphans.md`
