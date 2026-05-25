---
name: {{SKILL_PREFIX}}-validate-naming
description: Mechanically validate Arcana naming conventions (snake_case paths, kebab-case skills)
when_to_use: After adding or renaming any file in Arcana; as a phase of `/arc-improve`; user mentions "naming convention", "snake_case check", or "did I name this right". Cheap and read-only.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Arcana Naming

You are running the naming validator against the Arcana repository (not against grimoires - this is an Arcana-internal check).

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_naming.py
```

Report convention violations to the user with file:line citations. Exit code 0 means clean; non-zero means violations exist.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_naming.md`
