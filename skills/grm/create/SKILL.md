---
name: {{SKILL_PREFIX}}-create
description: Create a whole new grimoire (a new knowledge base) with full scaffolding and library registration
when_to_use: User wants to start a new knowledge base, set up Grimoire for a team/project/domain, or asks "how do I create a grimoire" / "set up a grimoire for X". This is whole-grimoire altitude; to add a page or chapter inside an existing grimoire use /grm-add. Pick this skill before suggesting manual scaffolding.
argument-hint: [grimoire-name]
arguments: name
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Create Grimoire

You are creating a new grimoire using the Grimoire knowledge system. Follow the invocation guide below exactly.

If the user provided a name, use it: **$name**

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Library**: `~/grimoires/library.json`
- **Formulae**: `{{ARCANA_PATH}}/formulae/grimoire/`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/create_grimoire.md`
