---
name: {{SKILL_PREFIX}}-validate-frontmatter
description: Mechanically validate page frontmatter against the canonical schema (type, required fields, sources, last_verified)
when_to_use: Before committing Arcana changes that touched page frontmatter; after adding Arcana pages with new types; as a phase of `/arc-improve`. Cheap and read-only. For an active grimoire, use `/grm-validate-frontmatter`.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Frontmatter

You are running the frontmatter validator against the Arcana repository.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_frontmatter.py
```

For an active grimoire, use `/grm-validate-frontmatter`.

Report violations with file paths and reason. Exit code 0 means every page complies with the schema.

## Procedural detail

For the full schema and per-type required fields:

!`cat {{ARCANA_PATH}}/docs/page_schema.md`

For invocation-level guidance:

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_frontmatter.md`
