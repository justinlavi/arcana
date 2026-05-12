---
name: {{NAMESPACE}}-arcana-validate-semantics
description: Mechanically scan Arcana for deprecated terminology and hyphenated path examples
user-invocable: true
allowed-tools: Bash Read
---

# Validate Arcana Semantics

You are running the semantics validator against the Arcana repository. It scans for:

1. **Deprecated terms** listed in `{{ARCANA_PATH}}/rites/data/deprecated_terms.txt` (single source of truth — add new deprecations there).
2. **Hyphenated path examples** in body text (Arcana convention is snake_case for paths).

This is a mechanical pattern scan. For *intelligent* semantic analysis (naming quality, organizational discoverability), use `/grm-domain-analyze-semantics`.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_semantics.py
```

Report violations with file:line citations. Exit code 0 means clean; non-zero means violations exist.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_semantics.md`
