# Grimoire Invocations

Domain operations — invocations that create or improve a domain grimoire (not Arcana itself).

## Available

| Invocation | Skill | What it does |
|---|---|---|
| [create_grimoire.md](create_grimoire.md) | `/grm-domain-create-grimoire` | Create a new domain grimoire (AI-guided, scaffolds INDEX/README/manifest/chapters) |
| [create_chapter.md](create_chapter.md) | `/grm-domain-create-chapter` | Add a knowledge chapter to the active grimoire |
| [improve_grimoire.md](improve_grimoire.md) | `/grm-domain-improve` | Comprehensive grimoire improvement (audit, normalize, optimize) |
| [analyze_semantics.md](analyze_semantics.md) | `/grm-domain-analyze-semantics` | Deep semantic analysis (naming quality, organization, discoverability) |
| [validate_structure.md](validate_structure.md) | `/grm-domain-validate-structure` | Mechanical structure compliance against Arcana formulae |

## Typical flow

1. **Create**: `/grm-domain-create-grimoire` once, then `/grm-domain-create-chapter` per topic.
2. **Improve**: `/grm-domain-improve` periodically — orchestrates `analyze-semantics` + `validate-structure` + boundary checks.
3. **Audit**: invoke individual analysis/validation skills as needed.

## Related

- Canonical skill catalog (Arcana + domain): [`../../docs/skills.md`](../../docs/skills.md)
- Meta operations: [`../meta/INDEX.md`](../meta/INDEX.md)
- Arcana maintenance (maintainer only): [`../arcana/INDEX.md`](../arcana/INDEX.md)
- Operating model: [`../../docs/operating_model.md`](../../docs/operating_model.md)
