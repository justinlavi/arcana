---
name: {{SKILL_PREFIX}}-validate-frontmatter
description: Validate page frontmatter in the active grimoire
when_to_use: User asks to check grimoire page schema; after adding, importing, or editing pages; before committing grimoire changes.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Grimoire Frontmatter

You are validating frontmatter schema compliance in the active grimoire.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/validators/validate_frontmatter.md`
