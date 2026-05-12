---
name: {{NAMESPACE}}-arcana-validate-format
description: Mechanically validate Arcana markdown formatting (headings, code fences, frontmatter)
user-invocable: true
allowed-tools: Bash Read
---

# Validate Arcana Format

You are running the format validator against the Arcana repository (not against domain grimoires — this is an Arcana-internal check).

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_format.py
```

Report violations to the user with file:line citations from the rite output. Exit code 0 means clean; non-zero means violations were found.

## Procedural detail

For full workflow guidance (when to run, how to interpret violations, fix patterns):

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_format.md`
