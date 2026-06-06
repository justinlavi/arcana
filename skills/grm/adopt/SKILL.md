---
name: {{SKILL_PREFIX}}-adopt
description: Register an existing folder under ~/grimoires/ as a grimoire by writing its grimoire.json - for a brand-new grimoire use /grm-create
when_to_use: User has a folder under ~/grimoires/ that has content but no grimoire.json (notes dragged in via Obsidian or a file manager, or a folder /grm-sync library flagged as unmanaged) and wants to make it a real grimoire. User says "register this folder as a grimoire" or "adopt this folder". To start from scratch use /grm-create.
argument-hint: "[directory-name]"
arguments: directory
user-invocable: true
allowed-tools: Bash Read
---

# Adopt an Existing Folder as a Grimoire

You are turning an existing folder under `~/grimoires/` into a registered grimoire by writing its `grimoire.json` manifest.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Invocation**: `{{ARCANA_PATH}}/invocations/grm/adopt.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/adopt.md`
