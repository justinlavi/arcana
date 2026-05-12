---
name: {{NAMESPACE}}-meta-help
description: Display the Grimoire skill catalog and usage guide
user-invocable: true
allowed-tools: Bash Read
---

# Grimoire Help

You are displaying the Grimoire skill catalog. Follow the invocation guide below to dynamically generate the catalog.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Skills source**: `{{ARCANA_PATH}}/skills/`
- **Registered targets**: `~/.claude/skills/`, `~/.codex/skills/`
- **Invocations**: `{{ARCANA_PATH}}/invocations/`
- **Catalog**: `~/grimoire/catalog.json`

## Available Skills

Users invoke Grimoire operations as slash-command skills in supported agents. Arcana maintenance skills are scoped under `grm-arcana-*`:

**Domain grimoire operations:**
- `/grm-domain-create-grimoire` — Create a new domain grimoire
- `/grm-domain-create-chapter` — Create a new knowledge chapter
- `/grm-domain-improve` — Comprehensive grimoire improvement
- `/grm-domain-analyze-semantics` — Semantic analysis
- `/grm-domain-validate-structure` — Validate structure compliance

**Arcana maintenance:**
- `/grm-arcana-validate-boundaries` — Boundary validation
- `/grm-arcana-improve` — Improve Arcana (maintainer)
- `/grm-arcana-clean` — Remove temporary rite artifacts

**Meta:**
- `/grm-meta-help` — This help screen
- `/grm-skills-register` — Re-register all skills from Arcana and domain grimoires

Domain grimoires contribute additional skills with their explicit catalog namespace (e.g., `/jpn-travel-create-trip`). Run `/grm-skills-register` after pulling updates to refresh Claude Code and Codex/ChatGPT registrations.

## Invocation

!`cat {{ARCANA_PATH}}/invocations/meta/help.md`
