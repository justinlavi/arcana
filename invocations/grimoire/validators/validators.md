---
type: hub
title: "Grimoire Validators"
aliases: ["grimoire-validators"]
tags: [arcana/invocations, type/hub, scope/grimoire, hub/sub]
authority: grimoire
last_verified: 2026-05-25
---

# Grimoire Validators

Mechanical validators that operate on the resolved active grimoire. Each wraps a shared Arcana rite with `--grimoire GRIMOIRE_ROOT`.

| Invocation | Skill | Checks |
|---|---|---|
| [[invocations/grimoire/validators/validate_all|validate all]] | `/grm-validate-all` | Full deterministic grimoire validator profile |
| [[invocations/grimoire/validators/validate_encoding|validate encoding]] | `/grm-validate-encoding` | UTF-8, LF line endings, BOMs, mojibake markers, repair artifacts |
| [[invocations/grimoire/validators/validate_format|validate format]] | `/grm-validate-format` | Markdown tables, code fences, tree examples |
| [[invocations/grimoire/validators/validate_frontmatter|validate frontmatter]] | `/grm-validate-frontmatter` | Page frontmatter schema |
| [[invocations/grimoire/validators/validate_links|validate links]] | `/grm-validate-links` | Internal references resolve and hub routes use wikilinks |
| [[invocations/grimoire/validators/validate_orphans|validate orphans]] | `/grm-validate-orphans` | Pages are reachable from other pages |
| [[invocations/grimoire/validators/validate_portability|validate portability]] | `/grm-validate-portability` | Windows-safe paths |
| [[invocations/grimoire/validators/validate_provenance|validate provenance]] | `/grm-validate-provenance` | External/hybrid pages cite real sources |
| [[invocations/grimoire/validators/validate_doc_trees|validate doc trees]] | `/grm-validate-doc-trees` | ASCII directory diagrams match the filesystem |

## Related

- Structure validator -> [[invocations/grimoire/validate_structure|validate structure]]
- Boundary validator -> [[invocations/grimoire/validate_boundaries|validate boundaries]]
