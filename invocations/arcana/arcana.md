---
type: hub
title: "Arcana Invocations"
aliases: ["arcana-invocations", "maintainer-ops"]
tags: [arcana/invocations, type/hub, scope/arcana, hub/chapter]
---

# Arcana Invocations

Invocations that modify Arcana itself. Maintainer only.

For grimoire operations, route to [[invocations/grimoire/grimoire|grimoire]]. For agent, library, help, workspace, and shared support docs, route through their invocation hubs. For the canonical skill catalog, see [[docs/skills|skills]].

## Available

### Improvement

- Arcana improvement -> [[invocations/arcana/improve_arcana|improve arcana]]

Boundary enforcement lives in the grimoire layer: [[invocations/grimoire/validate_boundaries|validate boundaries]]. It can scan Arcana itself with the `--arcana` flag.

### Validators

- Directory/file integrity -> [[invocations/arcana/validators/validate_structure|validate structure]]
- Encoding, line endings, BOMs, and mojibake -> [[invocations/arcana/validators/validate_encoding|validate encoding]]
- Filesystem portability -> [[invocations/arcana/validators/validate_portability|validate portability]]
- Snake_case path enforcement -> [[invocations/arcana/validators/validate_naming|validate naming]]
- Hyphenated path examples -> [[invocations/arcana/validators/validate_semantics|validate semantics]]
- Markdown and hub format -> [[invocations/arcana/validators/validate_format|validate format]]
- Link resolution and hub route style -> [[invocations/arcana/validators/validate_links|validate links]]
- Orphan detection -> [[invocations/arcana/validators/validate_orphans|validate orphans]]
- Source provenance -> [[invocations/arcana/validators/validate_provenance|validate provenance]]
- Credential and unsafe Python scan -> [[invocations/arcana/validators/validate_security|validate security]]
- Skill reference resolution -> [[invocations/arcana/validators/validate_skill_refs|validate skill refs]]
- Validator family hub -> [[invocations/arcana/validators/validators|validators]]

### Quality

- Architecture and source-of-truth audit -> [[invocations/arcana/quality/review_architecture|review architecture]]
- Documentation duplication and clarity audit -> [[invocations/arcana/quality/improve_documentation|improve documentation]]
- Rite-specific quality checks -> [[invocations/arcana/quality/validate_rites|validate rites]]
- Quality family hub -> [[invocations/arcana/quality/quality|quality]]

## When to run

- Before any Arcana release
- After bulk doc/rite changes
- Monthly drift audit
- As phases of `/arc-improve`
