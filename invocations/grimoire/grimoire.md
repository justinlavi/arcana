---
type: hub
title: "Grimoire Invocations"
aliases: ["grimoire-invocations", "grimoire-ops"]
tags: [arcana/invocations, type/hub, scope/grimoire, hub/chapter]
---

# Grimoire Invocations

Grimoire operations - invocations that create or improve a grimoire (not Arcana itself).

## Available

| Invocation | Skill | What it does |
|---|---|---|
| [create_grimoire.md](create_grimoire.md) | `/grm-create` | Create a new grimoire (AI-guided; scaffolds root hub, README, manifest, sources/, log.md, chapters) |
| [create_chapter.md](create_chapter.md) | `/grm-create-chapter` | Add a knowledge chapter to the active grimoire |
| [update_arcana.md](update_arcana.md) | `/grm-update-arcana` | Pull the latest Arcana, refresh agent integration, re-register skills, and check active-grimoire compatibility |
| [register_skills.md](register_skills.md) | `/grm-register-skills` | Register Arcana skills and the active grimoire's own skills |
| [ingest.md](ingest.md) | `/grm-ingest` | File a source artifact under sources/ and update affected wiki pages |
| [file_answer.md](file_answer.md) | `/grm-file-answer` | Promote a chat answer into a properly-frontmattered wiki page |
| [lint.md](lint.md) | `/grm-lint` | Health-check the grimoire (orphans, stale, ghost references, contradictions) |
| [repair_links.md](repair_links.md) | `/grm-repair-links` | Bulk-promote filename-only wikilinks to canonical full-path form |
| [improve_grimoire.md](improve_grimoire.md) | `/grm-improve` | Comprehensive grimoire improvement (audit, normalize, optimize) |
| [analyze_semantics.md](analyze_semantics.md) | `/grm-analyze-semantics` | Deep semantic analysis (naming quality, organization, discoverability) |
| [validate_structure.md](validate_structure.md) | `/grm-validate-structure` | Mechanical structure compliance against Arcana formulae |
| [validate_boundaries.md](validate_boundaries.md) | `/grm-validate-boundaries` | Magical/practical boundary compliance |
| [validators/validators.md](validators/validators.md) | `/grm-validate-*` | Mechanical validators for active grimoires |

## Typical flow

1. **Create**: `/grm-create` once, then `/grm-create-chapter` per topic.
2. **Ingest**: `/grm-ingest <source>` to file new sources under `sources/` and update the wiki.
3. **File**: `/grm-file-answer` to promote substantive chat answers back into the wiki.
4. **Lint**: `/grm-lint` periodically - orphans, stale claims, ghost references, contradictions.
5. **Improve**: `/grm-improve` for a comprehensive normalize-and-optimize pass.
6. **Update Arcana**: `/grm-update-arcana` when the local Arcana install may be stale.
7. **Refresh skills**: `/grm-register-skills` after editing the active grimoire's `skills/`.
8. **Audit**: invoke individual analysis/validation skills as needed.

## Related

- Canonical skill catalog (Arcana + grimoire): [`../../docs/skills.md`](../../docs/skills.md)
- Meta operations: [`../meta/meta.md`](../meta/meta.md)
- Agent operations: [`../agent/agent.md`](../agent/agent.md)
- Arcana maintenance (maintainer only): [`../arcana/arcana.md`](../arcana/arcana.md)
- Operating model: [`../../docs/operating_model.md`](../../docs/operating_model.md)
