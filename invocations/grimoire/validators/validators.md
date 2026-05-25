---
type: hub
title: "Grimoire Validators"
aliases: ["grimoire-validators"]
tags: [arcana/invocations, type/hub, scope/grimoire, hub/sub]
authority: grimoire
last_verified: 2026-05-25
---

# Grimoire Validators

Mechanical validators that operate on the active grimoire. Each wraps a shared Arcana rite with `--grimoire .` so the user-facing command target is explicit.

| Invocation | Skill | Checks |
|---|---|---|
| [validate_encoding.md](validate_encoding.md) | `/grm-validate-encoding` | UTF-8, LF line endings, BOMs, mojibake markers, repair artifacts |
| [validate_format.md](validate_format.md) | `/grm-validate-format` | Markdown tables, code fences, tree examples |
| [validate_frontmatter.md](validate_frontmatter.md) | `/grm-validate-frontmatter` | Page frontmatter schema |
| [validate_links.md](validate_links.md) | `/grm-validate-links` | Markdown links and wikilinks resolve |
| [validate_orphans.md](validate_orphans.md) | `/grm-validate-orphans` | Pages are reachable from other pages |
| [validate_portability.md](validate_portability.md) | `/grm-validate-portability` | Windows-safe paths |
| [validate_provenance.md](validate_provenance.md) | `/grm-validate-provenance` | External/hybrid pages cite real sources |

Related root-level grimoire validators:

- [../validate_structure.md](../validate_structure.md) - `/grm-validate-structure`
- [../validate_boundaries.md](../validate_boundaries.md) - `/grm-validate-boundaries`
