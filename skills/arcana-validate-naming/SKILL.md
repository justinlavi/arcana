---
name: {{NAMESPACE}}-arcana-validate-naming
description: Mechanically validate Arcana naming conventions (snake_case paths, kebab-case skills)
user-invocable: true
allowed-tools: Bash Read
---

# Validate Arcana Naming

You are running the naming validator against the Arcana repository (not against domain grimoires — this is an Arcana-internal check).

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_naming.py
```

Report convention violations to the user with file:line citations. Exit code 0 means clean; non-zero means violations exist.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_naming.md`
