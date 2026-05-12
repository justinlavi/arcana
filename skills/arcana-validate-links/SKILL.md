---
name: {{NAMESPACE}}-arcana-validate-links
description: Mechanically validate that internal markdown links in Arcana resolve to real files
user-invocable: true
allowed-tools: Bash Read
---

# Validate Arcana Links

You are running the link validator against the Arcana repository (not against domain grimoires — this is an Arcana-internal check).

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_links.py
```

Report broken links to the user with file:line citations. Exit code 0 means clean; non-zero means broken links exist.

Be aware: template formula files (under `formulae/`) intentionally contain placeholder paths like `GRIMOIRE_ARCANA/...` that don't resolve — these are not failures. The rite knows how to skip them; if it doesn't, treat as a rite bug, not a content bug.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_links.md`
