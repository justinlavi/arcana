---
type: hub
title: "Arcana Invocations"
aliases: ["arcana-invocations", "maintainer-ops"]
tags: [arcana/invocations, type/hub, scope/arcana, hub/chapter]
---

# Arcana Invocations

Invocations that **modify Arcana itself**. Maintainer only.

For domain operations (creating chapters, improving grimoires) see [`../grimoire/grimoire.md`](../grimoire/grimoire.md). For meta/help, see [`../meta/meta.md`](../meta/meta.md). For the canonical skill catalog, see [`../../docs/skills.md`](../../docs/skills.md).

## Available

### Improvement

- **[improve_arcana.md](improve_arcana.md)** — Comprehensive Arcana improvement; orchestrates the validators and quality invocations. Skill: `/grm-arcana-improve`.

Boundary enforcement lives in the domain layer: see [`../grimoire/validate_boundaries.md`](../grimoire/validate_boundaries.md) (skill: `/grm-domain-validate-boundaries`). It can scan Arcana itself with the `--arcana` flag.

### Validators (mechanical)

Each runs independently or as part of `/grm-arcana-improve`. Each has its own dedicated skill (`/grm-arcana-validate-<name>`):

- [`validators/validate_structure.md`](validators/validate_structure.md) — directory/file integrity
- [`validators/validate_naming.md`](validators/validate_naming.md) — snake_case enforcement
- [`validators/validate_semantics.md`](validators/validate_semantics.md) — hyphenated path examples in prose
- [`validators/validate_format.md`](validators/validate_format.md) — markdown formatting
- [`validators/validate_links.md`](validators/validate_links.md) — broken references
- [`validators/validate_security.md`](validators/validate_security.md) — credentials & unsafe Python

Run them all in one shot: `/grm-arcana-validate-all`. See [`validators/validators.md`](validators/validators.md) for orchestration details.

### Quality (judgment-based)

Manual passes for things validators can't measure:

- [`quality/improve_documentation.md`](quality/improve_documentation.md) — duplication and clarity audit
- [`quality/validate_rites.md`](quality/validate_rites.md) — rite-specific quality checks

See [`quality/quality.md`](quality/quality.md) for usage notes.

## When to run

- Before any Arcana release
- After bulk doc/rite changes
- Monthly drift audit (run `/grm-arcana-validate-all` and review violations)
- As phases of `/grm-arcana-improve` (the orchestrator handles ordering)
