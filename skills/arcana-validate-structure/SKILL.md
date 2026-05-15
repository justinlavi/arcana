---
name: {{NAMESPACE}}-arcana-validate-structure
description: Mechanically validate Arcana's directory structure and required hub files
when_to_use: After adding/removing top-level directories or required files in Arcana; as a phase of `/grm-arcana-improve`. Cheap and read-only. For domain grimoires, use `/grm-domain-validate-structure` instead.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Arcana Structure

You are running the structure validator against the Arcana repository. It checks that required files (root hub `arcana.md`, README.md, manifest, log.md, sources/, page_schema.md) exist and that the directory layout matches Arcana conventions.

This is the **Arcana** version. To validate a domain grimoire's structure, use `/grm-domain-validate-structure` instead.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_structure.py
```

Report missing/misplaced files with paths. Exit code 0 means clean; non-zero means structural issues exist.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_structure.md`
