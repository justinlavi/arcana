---
name: {{SKILL_PREFIX}}-check
description: Check the active grimoire - the full health pass (broken links, orphans, stale or contradictory pages, structure), or a scope - quick, a validator name, naming, boundaries, fix
when_to_use: User asks whether the grimoire is healthy or valid, wants broken links, orphans, stale pages, or contradictions found, asks about naming quality or discoverability, wants the magical/practical boundary reviewed, or wants broken wikilinks repaired. Before saving changes; after a batch of adds; periodic hygiene. "check the grimoire", "health check", "validate", "find orphans", "fix wikilinks", "audit naming".
argument-hint: "[quick | <validator> | naming | boundaries | fix]"
arguments: scope
user-invocable: true
allowed-tools: Bash Read Edit
---

# Check

You are evaluating the active grimoire. The scope, if given, is: **$scope**. Follow the invocation below exactly; route on the scope and run only that section.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Grimoire root**: resolved active grimoire (`GRIMOIRE_ROOT`)
- **Validator orchestrator**: `{{ARCANA_PATH}}/rites/validate.py`
- **Wikilink repair engine**: `{{ARCANA_PATH}}/rites/repair_links.py`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/check.md`
