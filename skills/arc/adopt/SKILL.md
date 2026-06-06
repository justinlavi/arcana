---
name: {{SKILL_PREFIX}}-adopt
description: Adopt an unmanaged directory under ~/grimoires/ as a grimoire by writing its grimoire.json manifest
when_to_use: /arc-sync library reported an "unmanaged directory" the user wants to register; user has an existing folder under ~/grimoires/ without a grimoire.json that they want to make a real grimoire; user says "register this directory as a grimoire" or "adopt this folder". Use /grm-create instead if starting from scratch.
argument-hint: [directory-name]
arguments: directory
user-invocable: true
allowed-tools: Bash Read
---

# Adopt Grimoire

You are turning an unmanaged directory under `~/grimoires/` into a registered grimoire by writing its `grimoire.json` manifest.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Invocation**: `{{ARCANA_PATH}}/invocations/arc/adopt.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/arc/adopt.md`
