---
name: {{SKILL_PREFIX}}-validate-frontmatter
description: Mechanically validate page frontmatter against the canonical schema (type, required fields, sources, last_verified)
when_to_use: Before committing changes that touched page frontmatter; after adding pages with new types; as a phase of `/arc-improve` or `/arc-grimoire-lint`. Cheap and read-only.
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

Or for a specific grimoire:

```bash
python3 {{ARCANA_PATH}}/rites/validate_frontmatter.py --grimoire <path>
```

Report violations with file paths and reason. Exit code 0 means every page complies with the schema.

## Procedural detail

For the full schema and per-type required fields:

!`cat {{ARCANA_PATH}}/docs/page_schema.md`

For invocation-level guidance:

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_frontmatter.md`
