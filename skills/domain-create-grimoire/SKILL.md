---
name: grm-domain-create-grimoire
description: Create a new domain grimoire with full scaffolding and catalog registration
argument-hint: [grimoire-name]
arguments: [name]
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Create Grimoire

You are creating a new domain grimoire using the Grimoire knowledge system. Follow the invocation guide below exactly.

If the user provided a name, use it: **$name**

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Catalog**: `~/grimoire/catalog.json`
- **Formulae**: `{{ARCANA_PATH}}/formulae/grimoire/`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/create_grimoire.md`
