---
name: {{NAMESPACE}}-arcana-validate-orphans
description: Detect pages no other page links to (orphans) — neither via markdown links nor wikilinks
when_to_use: After bulk renames, after removing a hub or chapter, as a phase of `/grm-domain-lint`. Cheap and read-only.
user-invocable: true
allowed-tools: Bash Read
---

# Validate Orphans

You are running the orphan detector against the Arcana repository (or, when the working directory is a domain grimoire, against that grimoire).

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_orphans.py --grimoire .
```

Report each orphan with its relative path. Exit code 0 means no orphans; non-zero means at least one page is unreachable.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/quality/validate_orphans.md`
