---
type: hub
title: "Grimoire Invocations"
aliases: ["grimoire-invocations", "domain-ops"]
tags: [arcana/invocations, type/hub, scope/domain, hub/chapter]
---

# Grimoire Invocations

Domain operations — invocations that create or improve a domain grimoire (not Arcana itself).

## Available

| Invocation | Skill | What it does |
|---|---|---|
| [create_grimoire.md](create_grimoire.md) | `/grm-domain-create-grimoire` | Create a new domain grimoire (AI-guided; scaffolds root hub, README, manifest, sources/, log.md, chapters) |
| [create_chapter.md](create_chapter.md) | `/grm-domain-create-chapter` | Add a knowledge chapter to the active grimoire |
| [ingest.md](ingest.md) | `/grm-domain-ingest` | File a source artifact under sources/ and update affected wiki pages |
| [file_answer.md](file_answer.md) | `/grm-domain-file-answer` | Promote a chat answer into a properly-frontmattered wiki page |
| [lint.md](lint.md) | `/grm-domain-lint` | Health-check the grimoire (orphans, stale, ghost references, contradictions) |
| [improve_grimoire.md](improve_grimoire.md) | `/grm-domain-improve` | Comprehensive grimoire improvement (audit, normalize, optimize) |
| [analyze_semantics.md](analyze_semantics.md) | `/grm-domain-analyze-semantics` | Deep semantic analysis (naming quality, organization, discoverability) |
| [validate_structure.md](validate_structure.md) | `/grm-domain-validate-structure` | Mechanical structure compliance against Arcana formulae |

## Typical flow

1. **Create**: `/grm-domain-create-grimoire` once, then `/grm-domain-create-chapter` per topic.
2. **Ingest**: `/grm-domain-ingest <source>` to file new sources under `sources/` and update the wiki.
3. **File**: `/grm-domain-file-answer` to promote substantive chat answers back into the wiki.
4. **Lint**: `/grm-domain-lint` periodically — orphans, stale claims, ghost references, contradictions.
5. **Improve**: `/grm-domain-improve` for a comprehensive normalize-and-optimize pass.
6. **Audit**: invoke individual analysis/validation skills as needed.

## Related

- Canonical skill catalog (Arcana + domain): [`../../docs/skills.md`](../../docs/skills.md)
- Meta operations: [`../meta/meta.md`](../meta/meta.md)
- Arcana maintenance (maintainer only): [`../arcana/arcana.md`](../arcana/arcana.md)
- Operating model: [`../../docs/operating_model.md`](../../docs/operating_model.md)
