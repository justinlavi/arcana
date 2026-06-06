---
type: hub
title: "Grimoire Invocations"
aliases: ["grimoire-invocations", "grimoire-ops"]
tags: [arcana/invocations, type/hub, scope/grimoire, hub/chapter]
---

# Grimoire Invocations

Grimoire operations that create, update, validate, or improve a grimoire. Arcana maintenance routes through [[invocations/arcana/arcana|arcana]].

## Available

| Invocation | Skill | What it does |
|---|---|---|
| [[invocations/grimoire/help|help]] | `/grm-help` | Show the grimoire command catalog and the active grimoire's own skills |
| [[invocations/grimoire/create_grimoire|create grimoire]] | `/grm-create` | Create a new grimoire |
| [[invocations/grimoire/add|add]] | `/grm-add` | Add knowledge to the grimoire as a page or a chapter, fresh or captured from the chat session |
| [[invocations/grimoire/update|update]] | `/grm-update` | Update Arcana and every grimoire in the library to a current, validated, synchronized state |
| [[invocations/grimoire/sync_skills|sync skills]] | `/grm-sync-skills` | Sync Arcana skills and the active grimoire's own skills |
| [[invocations/grimoire/import|import]] | `/grm-import` | File source artifacts and update affected wiki pages |
| [[invocations/grimoire/health_check|health check]] | `/grm-health-check` | Health-check the grimoire |
| [[invocations/grimoire/repair_links|repair links]] | `/grm-repair-links` | Promote filename-only wikilinks to canonical full-path form |
| [[invocations/grimoire/improve_grimoire|improve grimoire]] | `/grm-improve` | Comprehensive grimoire improvement |
| [[invocations/grimoire/audit_semantics|audit semantics]] | `/grm-audit-semantics` | Semantic analysis for naming, organization, and discoverability |
| [[invocations/grimoire/validators/validate|validate]] | `/grm-validate` | Full deterministic validator profile for active grimoires |
| [[invocations/grimoire/validate_structure|validate structure]] | `/grm-validate structure` | Mechanical structure compliance against Arcana formulae |
| [[invocations/grimoire/audit_boundaries|audit boundaries]] | `/grm-audit-boundaries` | Magical/practical boundary compliance |

## Typical Flow

1. Create: `/grm-create` for a new grimoire.
2. Add: `/grm-add` to add a page or chapter — fresh, or capturing a substantive chat answer.
3. Import: `/grm-import <source>` to file new sources and update the wiki.
4. Health-check: `/grm-health-check` periodically.
5. Improve: `/grm-improve` for a comprehensive normalize-and-optimize pass.
6. Update: `/grm-update` when Arcana or a grimoire may be stale.
7. Refresh skills: `/grm-sync-skills` after editing grimoire `skills/`.
8. Audit: run `/grm-validate`, then invoke `/grm-audit-*` skills as needed.

## Related

- Canonical skill catalog -> [[docs/skills|skills]]
- Meta operations -> [[invocations/meta/meta|meta]]
- Agent operations -> [[invocations/agent/agent|agent]]
- Arcana maintenance -> [[invocations/arcana/arcana|arcana]]
- Operating model -> [[docs/operating_model|operating model]]
