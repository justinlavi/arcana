---
name: {{SKILL_PREFIX}}-validate-links
description: Validate grimoire links and enforce layer-aware internal link style
when_to_use: User asks about broken links in a grimoire; after moving or renaming grimoire pages; before committing grimoire changes.
user-invocable: true
allowed-tools: Bash Read
---

# Validate Grimoire Links

You are validating links and layer-specific internal page style in the active grimoire.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/validators/validate_links.md`
