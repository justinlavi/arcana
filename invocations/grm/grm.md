---
type: hub
title: "Grimoire Invocations"
aliases: ["grimoire-invocations", "grimoire-ops"]
tags: [arcana/invocations, type/hub, scope/grimoire, hub/chapter]
---

# Grimoire Invocations

Grimoire operations that create, update, validate, or audit a grimoire. Arcana maintenance routes through [[invocations/arc/arc|arc]].

## Available

| Invocation | Skill | What it does |
|---|---|---|
| [[invocations/grm/help|help]] | `/grm-help` | Show the grimoire command catalog and the active grimoire's own skills |
| [[invocations/grm/create_grimoire|create grimoire]] | `/grm-create` | Create a whole new grimoire |
| [[invocations/grm/add|add]] | `/grm-add` | Add a page or chapter to an existing grimoire, fresh or captured from the chat session |
| [[invocations/grm/update|update]] | `/grm-update` | Update Arcana and every grimoire in the library to a current, validated, synchronized state |
| [[invocations/grm/sync|sync]] | `/grm-sync` | Sync Arcana skills and the active grimoire's own skills |
| [[invocations/grm/import|import]] | `/grm-import` | File source artifacts and update affected wiki pages |
| [[invocations/grm/health_check|health check]] | `/grm-health-check` | Health-check the grimoire |
| [[invocations/grm/repair_links|repair links]] | `/grm-repair-links` | Promote filename-only wikilinks to canonical full-path form |
| [[invocations/grm/audit_semantics|audit semantics]] | `/grm-audit-semantics` | Semantic analysis for naming, organization, and discoverability |
| [[invocations/grm/validators/validate|validate]] | `/grm-validate` | Full deterministic validator profile for active grimoires |
| [[invocations/grm/validate_structure|validate structure]] | `/grm-validate structure` | Mechanical structure compliance against Arcana formulae |
| [[invocations/grm/audit_boundaries|audit boundaries]] | `/grm-audit-boundaries` | Magical/practical boundary compliance |

## Typical Flow

1. Create: `/grm-create` for a new grimoire.
2. Add: `/grm-add` to add a page or chapter — fresh, or capturing a substantive chat answer.
3. Import: `/grm-import <source>` to file new sources and update the wiki.
4. Health-check: `/grm-health-check` periodically for a normalize-and-optimize pass.
5. Update: `/grm-update` when Arcana or a grimoire may be stale.
6. Refresh skills: `/grm-sync` after editing grimoire `skills/`.
7. Audit: run `/grm-validate`, then invoke `/grm-audit-*` skills as needed.

## Related

- Canonical skill catalog -> [[docs/skills|skills]]
- Meta operations -> [[invocations/meta/meta|meta]]
- Arcana maintenance -> [[invocations/arc/arc|arc]]
- Operating model -> [[docs/operating_model|operating model]]
