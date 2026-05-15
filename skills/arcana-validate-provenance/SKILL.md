---
name: {{NAMESPACE}}-arcana-validate-provenance
description: Mechanically validate that pages with authority external/hybrid cite real sources under sources/
when_to_use: After `/grm-domain-ingest`, as a phase of `/grm-domain-lint`, after moving files in sources/. Cheap and read-only.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Provenance

You are running the provenance validator against the Arcana repository (or, when the working directory is a domain grimoire, against that grimoire).

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_provenance.py --grimoire .
```

Report each provenance failure with file path and reason. Exit code 0 means every external/hybrid page resolves to existing sources.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_provenance.md`
