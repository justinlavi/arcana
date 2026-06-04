---
name: {{SKILL_PREFIX}}-repair-links
description: Promote filename-only wikilinks to canonical full-path form across the active grimoire
when_to_use: After a structural migration or when /grm-health-check reports a wave of broken wikilinks of the form "must resolve as a repository path". User mentions "fix wikilinks", "repair links", "promote wikilinks", or "broken wikilinks".
user-invocable: true
allowed-tools: Bash Read Edit
---

# Repair Wikilinks

You are bulk-rewriting filename-only wikilinks in the active grimoire to the canonical full-path form `[[chapters/path/to/page|label]]`. The mechanical engine is `repair_links.py`; your job is to dry-run, surface findings, get user approval, apply, and resolve any ambiguous cases by reading surrounding context.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Grimoire root**: resolved active grimoire (`GRIMOIRE_ROOT`)
- **Engine**: `{{ARCANA_PATH}}/rites/repair_links.py`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/repair_links.md`
