---
name: grm-help
description: Display the Grimoire skill catalog and usage guide
user-invocable: true
allowed-tools: Bash Read
---

# Grimoire Help

You are displaying the Grimoire skill catalog. Follow the invocation guide below to dynamically generate the catalog.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Skills source**: `{{ARCANA_PATH}}/skills/`
- **Invocations**: `{{ARCANA_PATH}}/invocations/`
- **Catalog**: `~/grimoire/catalog.json`

## Available Skills

Users invoke Grimoire operations as Claude Code skills. Arcana maintenance skills are scoped under `grm-arcana-*`:

**Grimoire operations:**
- `/grm-create-grimoire` — Create a new domain grimoire
- `/grm-create-chapter` — Create a new knowledge chapter
- `/grm-improve` — Comprehensive grimoire improvement
- `/grm-analyze-semantics` — Semantic analysis

**Arcana maintenance:**
- `/grm-arcana-validate` — Validate structure compliance
- `/grm-arcana-validate-boundaries` — Boundary validation
- `/grm-arcana-improve` — Improve Arcana (maintainer)
- `/grm-arcana-clean` — Remove temporary rite artifacts

**Meta:**
- `/grm-help` — This help screen
- `/grm-register-skills` — Re-register all skills from Arcana and domain grimoires

Domain grimoires contribute additional skills with their own namespace prefix (e.g., `/olympus-*`). Run `/grm-register-skills` after pulling updates to refresh.

## Invocation

!`cat {{ARCANA_PATH}}/invocations/meta/help.md`
