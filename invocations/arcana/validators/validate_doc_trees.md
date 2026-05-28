---
type: reference
title: "Validate Arcana Doc Trees"
aliases: ["validate-arcana-doc-trees", "arcana-validate-doc-trees", "validate-tree-diagrams-arcana"]
tags: [arcana/invocations, type/reference, scope/validators]
authority: grimoire
last_verified: 2026-05-28
---

# Invocation: Validate Arcana Doc Trees

## Purpose

Detect drift between ASCII directory-tree diagrams (in fenced code blocks)
and the actual filesystem of the Arcana repository.

## Invocation

```
/arc-validate-doc-trees
```

## Workflow

Run against the Arcana repository root:

```bash
python3 ARCANA_HOME/rites/validate_doc_trees.py
```

Exit code 0 means every diagram with a resolvable filesystem anchor matches
reality. Most Arcana diagrams use placeholder roots like `{grimoire-name}/`
or `~/grimoires/` and are treated as illustrative.

## What it checks

See [[invocations/grimoire/validators/validate_doc_trees|grimoire-side
validate_doc_trees]] for the full algorithm. The Arcana-side invocation runs
the same script with no `--grimoire` flag (defaults to the Arcana root).

## Related

- Validators hub: [[invocations/arcana/validators/validators|validators]]
- Improvement playbook: [[invocations/arcana/improve_arcana|improve arcana]]
- Grimoire counterpart: [[invocations/grimoire/validators/validate_doc_trees|grm-validate-doc-trees]]
