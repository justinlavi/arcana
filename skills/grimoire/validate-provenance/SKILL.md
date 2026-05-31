---
name: {{SKILL_PREFIX}}-validate-provenance
description: Validate source provenance in the active grimoire
when_to_use: User asks whether sourced grimoire pages cite real artifacts; after ingesting sources or editing pages with external/hybrid authority; before committing grimoire changes.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Grimoire Provenance

You are validating source provenance in the active grimoire.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/validators/validate_provenance.md`
