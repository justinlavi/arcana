# Arcana Invocations

Invocations that **modify Arcana itself**. Maintainer only.

For domain operations (creating chapters, improving grimoires) see [`../grimoire/INDEX.md`](../grimoire/INDEX.md). For meta/help, see [`../meta/INDEX.md`](../meta/INDEX.md). For the canonical skill catalog, see [`../../docs/skills.md`](../../docs/skills.md).

## Available

### Improvement & boundary

- **[improve_arcana.md](improve_arcana.md)** — Comprehensive Arcana improvement; orchestrates the validators and quality invocations. Skill: `/grm-arcana-improve`.
- **[validate_boundaries.md](validate_boundaries.md)** — Magical/practical boundary enforcement. Skill: `/grm-arcana-validate-boundaries`.

### Validators (mechanical)

Each runs independently or as part of `/grm-arcana-improve`. Each has its own dedicated skill (`/grm-arcana-validate-<name>`):

- [`validators/validate_structure.md`](validators/validate_structure.md) — directory/file integrity
- [`validators/validate_naming.md`](validators/validate_naming.md) — snake_case enforcement
- [`validators/validate_semantics.md`](validators/validate_semantics.md) — deprecated terms + hyphenated paths
- [`validators/validate_format.md`](validators/validate_format.md) — markdown formatting
- [`validators/validate_links.md`](validators/validate_links.md) — broken references
- [`validators/validate_security.md`](validators/validate_security.md) — credentials & unsafe Python

Run them all in one shot: `/grm-arcana-validate-all`. See [`validators/INDEX.md`](validators/INDEX.md) for orchestration details.

### Quality (judgment-based)

Manual passes for things validators can't measure:

- [`quality/improve_documentation.md`](quality/improve_documentation.md) — duplication and clarity audit
- [`quality/validate_rites.md`](quality/validate_rites.md) — rite-specific quality checks

See [`quality/INDEX.md`](quality/INDEX.md) for usage notes.

## When to run

- Before any Arcana release
- After bulk doc/rite changes
- Monthly drift audit (run `/grm-arcana-validate-all` and review violations)
- As phases of `/grm-arcana-improve` (the orchestrator handles ordering)
