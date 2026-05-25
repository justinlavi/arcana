---
name: {{SKILL_PREFIX}}-validate-structure
description: Mechanically validate Arcana's directory structure and required hub files
when_to_use: After adding/removing top-level directories or required files in Arcana; as a phase of `/arc-improve`. Cheap and read-only. For grimoires, use `/arc-grimoire-validate-structure` instead.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Arcana Structure

You are running the structure validator against the Arcana repository. It checks that required files (root hub `arcana.md`, README.md, manifest, page_schema.md) exist and that the directory layout matches Arcana conventions. It also fails if grimoire layers (`chapters/`, `sources/`, `inbox/`, `log.md`) appear at Arcana root. Those layers are validated by `/arc-grimoire-validate-structure`, not by this Arcana validator.

This is the **Arcana** version. To validate a grimoire's structure, use `/arc-grimoire-validate-structure` instead.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_structure.py
```

Report missing/misplaced files with paths. Exit code 0 means clean; non-zero means structural issues exist.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_structure.md`
