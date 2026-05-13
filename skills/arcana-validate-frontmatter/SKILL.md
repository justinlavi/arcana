---
name: {{NAMESPACE}}-arcana-validate-frontmatter
description: Mechanically validate page frontmatter against the canonical schema (type, required fields, sources, last_verified)
when_to_use: Before committing changes that touched page frontmatter; after adding pages with new types; as a phase of `/grm-arcana-improve` or `/grm-domain-lint`. Cheap and read-only.
user-invocable: true
allowed-tools: Bash Read
---

# Validate Frontmatter

You are running the frontmatter validator against the Arcana repository (or, when the working directory is a domain grimoire, against that grimoire).

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_frontmatter.py
```

Or for a specific grimoire:

```bash
GRIMOIRE_ARCANA="$(pwd)" python3 {{ARCANA_PATH}}/rites/validate_frontmatter.py
```

Report violations with file paths and reason. Exit code 0 means every page complies with the schema.

## Procedural detail

For the full schema and per-type required fields:

!`cat {{ARCANA_PATH}}/docs/page_schema.md`

For invocation-level guidance:

!`cat {{ARCANA_PATH}}/invocations/arcana/quality/validate_frontmatter.md`
