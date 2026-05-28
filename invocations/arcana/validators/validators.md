---
type: hub
title: "Arcana Validators"
aliases: ["validators", "arcana-validators"]
tags: [arcana/invocations, type/hub, scope/validators, hub/sub]
---

# Arcana Validators

Mechanical, deterministic checks against the Arcana repository. Each validator has its own dedicated skill, and all of them run together via the orchestrator.

For the aggregate command, see [[invocations/arcana/validators/validate_all|validate all]].

## Available

| Validator | Skill | What it checks |
|---|---|---|
| [[invocations/arcana/validators/validate_structure|validate structure]] | `/arc-validate-structure` | Required directories and files exist; layout matches conventions |
| [[invocations/arcana/validators/validate_encoding|validate encoding]] | `/arc-validate-encoding` | UTF-8, LF line endings, BOMs, and mojibake markers |
| [[invocations/arcana/validators/validate_portability|validate portability]] | `/arc-validate-portability` | No Windows-reserved characters or basenames in any path |
| [[invocations/arcana/validators/validate_naming|validate naming]] | `/arc-validate-naming` | snake_case for paths; kebab-case for skills |
| [[invocations/arcana/validators/validate_format|validate format]] | `/arc-validate-format` | Invocation/formula schema compliance |
| [[invocations/arcana/validators/validate_frontmatter|validate frontmatter]] | `/arc-validate-frontmatter` | Every page declares its `type` and the schema's required fields |
| [[invocations/arcana/validators/validate_semantics|validate semantics]] | `/arc-validate-semantics` | Hyphenated path examples in markdown prose |
| [[invocations/arcana/validators/validate_links|validate links]] | `/arc-validate-links` | Internal references resolve and hub routes use wikilinks |
| [[invocations/arcana/validators/validate_orphans|validate orphans]] | `/arc-validate-orphans` | Every page is reachable from at least one other page |
| [[invocations/arcana/validators/validate_provenance|validate provenance]] | `/arc-validate-provenance` | Every external/hybrid page cites real sources under `sources/` |
| [[invocations/arcana/validators/validate_security|validate security]] | `/arc-validate-security` | Credential patterns and unsafe Python constructs in rites |
| [[invocations/arcana/validators/validate_skill_refs|validate skill refs]] | `/arc-validate-skill-refs` | Slash-command references and command-surface entries resolve |
| [[invocations/arcana/validators/validate_doc_trees|validate doc trees]] | `/arc-validate-doc-trees` | ASCII directory diagrams match the filesystem |

## Run them all

```bash
python3 ../../../rites/validate.py
python3 ../../../rites/validate.py --parallel
python3 ../../../rites/validate.py --smart
python3 ../../../rites/validate.py --auto
python3 ../../../rites/validate.py --format json
```

Or invoke `/arc-validate-all`, whose workflow home is [[invocations/arcana/validators/validate_all|validate all]].

## Related

- Orchestrator invocation -> [[invocations/arcana/improve_arcana|improve arcana]]
- Rite scripts: `rites/`
- Canonical terminology -> [[docs/reference|reference]]
