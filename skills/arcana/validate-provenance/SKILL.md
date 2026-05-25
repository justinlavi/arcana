---
name: {{SKILL_PREFIX}}-validate-provenance
description: Mechanically validate that pages with authority external/hybrid cite real sources under sources/
when_to_use: After adding or moving Arcana pages with external/hybrid authority; as a phase of `/arc-improve`. Cheap and read-only. For an active grimoire, use `/grm-validate-provenance`.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Provenance

You are running the provenance validator against the Arcana repository.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_provenance.py
```

Report each provenance failure with file path and reason. Exit code 0 means every external/hybrid page resolves to existing sources.

For an active grimoire, use `/grm-validate-provenance`.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_provenance.md`
