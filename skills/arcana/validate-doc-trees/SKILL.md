---
name: {{SKILL_PREFIX}}-validate-doc-trees
description: Detect drift between ASCII directory-tree diagrams in markdown docs and the actual filesystem of the Arcana repo
when_to_use: After renaming, adding, or removing Arcana folders / rites / invocations; as a phase of `/arc-improve`. Cheap and read-only. For an active grimoire, use `/grm-validate-doc-trees`.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Doc Trees

You are running the documented-tree drift detector against the Arcana
repository.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_doc_trees.py
```

Report each drifted entry with its file:line. Exit code 0 means every tree
diagram with a resolvable filesystem anchor matches reality; non-zero means
at least one diagram drifted from the actual layout.

For an active grimoire, use `/grm-validate-doc-trees`.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_doc_trees.md`
