---
name: {{NAMESPACE}}-arcana-validate-structure
description: Mechanically validate Arcana's directory structure and required hub files
user-invocable: true
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
