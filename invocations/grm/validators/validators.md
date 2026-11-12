---
type: hub
title: "Grimoire Validators"
aliases: ["grimoire-validators"]
tags: [arcana/invocations, type/hub, scope/grimoire, hub/sub]
authority: grimoire
last_verified: 2026-11-12
---

# Grimoire Validators

Mechanical validators that operate on the resolved active grimoire. The public
entry point is `/grm-check`: `check quick` runs the full suite, `check
<selector>` runs one or more validators. Each selector wraps a shared Arcana
rite with `--grimoire GRIMOIRE_ROOT`.

| Invocation | Skill | Checks |
|---|---|---|
| [[invocations/grm/check|check]] | `/grm-check quick` | Full deterministic grimoire validator profile, or targeted selectors |
| [[invocations/grm/validate_structure|validate structure]] | `/grm-check structure` | Required files and directories, folder-named hubs, scaffold parity, Obsidian config |
| [[invocations/grm/validators/validate_encoding|validate encoding]] | `/grm-check encoding` | UTF-8, LF line endings, BOMs, mojibake markers, repair artifacts |
| [[invocations/grm/validators/validate_format|validate format]] | `/grm-check format` | Markdown tables, code fences, tree examples |
| [[invocations/grm/validators/validate_frontmatter|validate frontmatter]] | `/grm-check frontmatter` | Page frontmatter schema |
| [[invocations/grm/validators/validate_links|validate links]] | `/grm-check links` | Internal references resolve, match on-disk casing, and hub routes use wikilinks |
| [[invocations/grm/validators/validate_orphans|validate orphans]] | `/grm-check orphans` | Pages are reachable from other pages |
| [[invocations/grm/validators/validate_portability|validate portability]] | `/grm-check portability` | Windows-safe paths, no case collisions |
| [[invocations/grm/validators/validate_provenance|validate provenance]] | `/grm-check provenance` | External/hybrid pages cite real sources |
| [[invocations/grm/validators/validate_doc_trees|validate doc trees]] | `/grm-check doc-trees` | ASCII directory diagrams match the filesystem |

## Related

- Judgment reviews (`naming`, `boundaries`) and mechanical repairs (`fix`) -> [[invocations/grm/check|check]]
