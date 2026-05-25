---
type: hub
title: "Grimoire Invocations"
aliases: ["grimoire-invocations", "domain-ops"]
tags: [arcana/invocations, type/hub, scope/domain, hub/chapter]
---

# Grimoire Invocations

Grimoire operations - invocations that create or improve a grimoire (not Arcana itself).

## Available

| Invocation | Skill | What it does |
|---|---|---|
| [create_grimoire.md](create_grimoire.md) | `/arc-grimoire-create` | Create a new grimoire (AI-guided; scaffolds root hub, README, manifest, sources/, log.md, chapters) |
| [create_chapter.md](create_chapter.md) | `/arc-grimoire-create-chapter` | Add a knowledge chapter to the active grimoire |
| [ingest.md](ingest.md) | `/arc-grimoire-ingest` | File a source artifact under sources/ and update affected wiki pages |
| [file_answer.md](file_answer.md) | `/arc-grimoire-file-answer` | Promote a chat answer into a properly-frontmattered wiki page |
| [lint.md](lint.md) | `/arc-grimoire-lint` | Health-check the grimoire (orphans, stale, ghost references, contradictions) |
| [repair_links.md](repair_links.md) | `/arc-grimoire-repair-links` | Bulk-promote filename-only wikilinks to canonical full-path form |
| [improve_grimoire.md](improve_grimoire.md) | `/arc-grimoire-improve` | Comprehensive grimoire improvement (audit, normalize, optimize) |
| [analyze_semantics.md](analyze_semantics.md) | `/arc-grimoire-analyze-semantics` | Deep semantic analysis (naming quality, organization, discoverability) |
| [validate_structure.md](validate_structure.md) | `/arc-grimoire-validate-structure` | Mechanical structure compliance against Arcana formulae |

## Typical flow

1. **Create**: `/arc-grimoire-create` once, then `/arc-grimoire-create-chapter` per topic.
2. **Ingest**: `/arc-grimoire-ingest <source>` to file new sources under `sources/` and update the wiki.
3. **File**: `/arc-grimoire-file-answer` to promote substantive chat answers back into the wiki.
4. **Lint**: `/arc-grimoire-lint` periodically - orphans, stale claims, ghost references, contradictions.
5. **Improve**: `/arc-grimoire-improve` for a comprehensive normalize-and-optimize pass.
6. **Audit**: invoke individual analysis/validation skills as needed.

## Related

- Canonical skill catalog (Arcana + domain): [`../../docs/skills.md`](../../docs/skills.md)
- Meta operations: [`../meta/meta.md`](../meta/meta.md)
- Arcana maintenance (maintainer only): [`../arcana/arcana.md`](../arcana/arcana.md)
- Operating model: [`../../docs/operating_model.md`](../../docs/operating_model.md)
