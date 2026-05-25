---
name: {{SKILL_PREFIX}}-validate-orphans
description: Detect pages no other page links to (orphans) - neither via markdown links nor wikilinks
when_to_use: After bulk renames or after removing an Arcana hub/page; as a phase of `/arc-improve`. Cheap and read-only. For an active grimoire, use `/grm-validate-orphans`.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Orphans

You are running the orphan detector against the Arcana repository.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_orphans.py
```

Report each orphan with its relative path. Exit code 0 means no orphans; non-zero means at least one page is unreachable.

For an active grimoire, use `/grm-validate-orphans`.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_orphans.md`
