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
| [[invocations/grm/adopt|adopt]] | `/grm-adopt` | Register an existing folder under ~/grimoires/ as a grimoire |
| [[invocations/grm/add|add]] | `/grm-add` | Write up new knowledge or capture a chat answer as a page or chapter (text you author) |
| [[invocations/grm/update|update]] | `/grm-update` | Update Arcana and every grimoire in the library to a current, validated, synchronized state |
| [[invocations/grm/sync|sync]] | `/grm-sync` | Reconcile your local setup: register skills, fix the library after a folder move, repair the agent routing block |
| [[invocations/grm/import|import]] | `/grm-import` | Bring an existing file or folder in as a cited source and update affected pages |
| [[invocations/grm/move|move]] | `/grm-move` | Rename or move a page or chapter; fixes every link and hub |
| [[invocations/grm/remove|remove]] | `/grm-remove` | Delete a page or chapter; flags inbound links that would break |
| [[invocations/grm/health_check|health check]] | `/grm-health-check` | Full checkup - start here (broken links, orphans, stale or contradictory pages, structure) |
| [[invocations/grm/repair_links|repair links]] | `/grm-repair-links` | Promote filename-only wikilinks to canonical full-path form |
| [[invocations/grm/audit_semantics|audit semantics]] | `/grm-audit-semantics` | Advanced, opt-in naming and discoverability review |
| [[invocations/grm/validators/validate|validate]] | `/grm-validate` | Quick mechanical pass/fail (links, headers); includes a `structure` selector |
| [[invocations/grm/audit_boundaries|audit boundaries]] | `/grm-audit-boundaries` | Advanced, opt-in magical/practical boundary check |

## Typical Flow

1. Create: `/grm-create` for a new grimoire.
2. Add: `/grm-add` to add a page or chapter — fresh, or capturing a substantive chat answer.
3. Import: `/grm-import <source>` to file new sources and update the wiki.
4. Health-check: `/grm-health-check` periodically for a normalize-and-optimize pass.
5. Update: `/grm-update` when Arcana or a grimoire may be stale.
6. Refresh setup: `/grm-sync` after editing grimoire `skills/`, moving a folder, or when routing breaks.
7. Check health: `/grm-health-check` for the full checkup; `/grm-validate` for a quick mechanical pass; `/grm-audit-*` are advanced opt-in tools.

## Related

- Canonical skill catalog -> [[docs/skills|skills]]
- Meta operations -> [[invocations/meta/meta|meta]]
- Arcana maintenance -> [[invocations/arc/arc|arc]]
- Operating model -> [[docs/operating_model|operating model]]
