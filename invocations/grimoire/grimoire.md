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
| [[invocations/grimoire/create_chapter|create chapter]] | `/grm-create-chapter` | Add a knowledge chapter to the active grimoire |
| [[invocations/grimoire/update|update]] | `/grm-update` | Update Arcana and every grimoire in the library to a current, validated, synchronized state |
| [[invocations/grimoire/register_skills|register skills]] | `/grm-register-skills` | Register Arcana skills and the active grimoire's own skills |
| [[invocations/grimoire/ingest|ingest]] | `/grm-ingest` | File source artifacts and update affected wiki pages |
| [[invocations/grimoire/file_answer|file answer]] | `/grm-file-answer` | Promote a chat answer into a properly-frontmattered wiki page |
| [[invocations/grimoire/lint|lint]] | `/grm-lint` | Health-check the grimoire |
| [[invocations/grimoire/repair_links|repair links]] | `/grm-repair-links` | Promote filename-only wikilinks to canonical full-path form |
| [[invocations/grimoire/improve_grimoire|improve grimoire]] | `/grm-improve` | Comprehensive grimoire improvement |
| [[invocations/grimoire/analyze_semantics|analyze semantics]] | `/grm-analyze-semantics` | Semantic analysis for naming, organization, and discoverability |
| [[invocations/grimoire/validators/validate_all|validate all]] | `/grm-validate-all` | Full deterministic validator profile for active grimoires |
| [[invocations/grimoire/validate_structure|validate structure]] | `/grm-validate-structure` | Mechanical structure compliance against Arcana formulae |
| [[invocations/grimoire/validate_boundaries|validate boundaries]] | `/grm-validate-boundaries` | Magical/practical boundary compliance |
| [[invocations/grimoire/validators/validators|validators]] | `/grm-validate-*` | Mechanical validators for active grimoires |

## Typical Flow

1. Create: `/grm-create`, then `/grm-create-chapter` per topic.
2. Ingest: `/grm-ingest <source>` to file new sources and update the wiki.
3. File: `/grm-file-answer` to promote substantive chat answers.
4. Lint: `/grm-lint` periodically.
5. Improve: `/grm-improve` for a comprehensive normalize-and-optimize pass.
6. Update: `/grm-update` when Arcana or a grimoire may be stale.
7. Refresh skills: `/grm-register-skills` after editing grimoire `skills/`.
8. Audit: run `/grm-validate-all`, then invoke analysis skills as needed.

## Related

- Canonical skill catalog -> [[docs/skills|skills]]
- Meta operations -> [[invocations/meta/meta|meta]]
- Agent operations -> [[invocations/agent/agent|agent]]
- Arcana maintenance -> [[invocations/arcana/arcana|arcana]]
- Operating model -> [[docs/operating_model|operating model]]
