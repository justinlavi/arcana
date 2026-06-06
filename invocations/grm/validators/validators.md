---
type: hub
title: "Grimoire Validators"
aliases: ["grimoire-validators"]
tags: [arcana/invocations, type/hub, scope/grimoire, hub/sub]
authority: grimoire
last_verified: 2026-05-25
---

# Grimoire Validators

Mechanical validators that operate on the resolved active grimoire. The public
entry point is `/grm-validate`; pass a selector to run one validator or omit the
selector to run the full suite. Each selector wraps a shared Arcana rite with
`--grimoire GRIMOIRE_ROOT`.

| Invocation | Skill | Checks |
|---|---|---|
| [[invocations/grm/validators/validate|validate]] | `/grm-validate` | Full deterministic grimoire validator profile, or targeted selectors |
| [[invocations/grm/validate_structure|validate structure]] | `/grm-validate structure` | Required files and directories, folder-named hubs, scaffold parity, Obsidian config |
| [[invocations/grm/validators/validate_encoding|validate encoding]] | `/grm-validate encoding` | UTF-8, LF line endings, BOMs, mojibake markers, repair artifacts |
| [[invocations/grm/validators/validate_format|validate format]] | `/grm-validate format` | Markdown tables, code fences, tree examples |
| [[invocations/grm/validators/validate_frontmatter|validate frontmatter]] | `/grm-validate frontmatter` | Page frontmatter schema |
| [[invocations/grm/validators/validate_links|validate links]] | `/grm-validate links` | Internal references resolve and hub routes use wikilinks |
| [[invocations/grm/validators/validate_orphans|validate orphans]] | `/grm-validate orphans` | Pages are reachable from other pages |
| [[invocations/grm/validators/validate_portability|validate portability]] | `/grm-validate portability` | Windows-safe paths |
| [[invocations/grm/validators/validate_provenance|validate provenance]] | `/grm-validate provenance` | External/hybrid pages cite real sources |
| [[invocations/grm/validators/validate_doc_trees|validate doc trees]] | `/grm-validate doc-trees` | ASCII directory diagrams match the filesystem |

## Related

- Boundary audit -> [[invocations/grm/audit_boundaries|audit boundaries]]
