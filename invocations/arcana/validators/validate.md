---
type: playbook
title: "Validate Arcana"
aliases: ["arcana-validate", "mechanical-validation"]
tags: [arcana/invocations, type/playbook, scope/validators]
authority: grimoire
last_verified: 2026-06-03
---

# Invocation: Validate Arcana

## Purpose

Run deterministic, script-backed validators against Arcana. This workflow is
mechanical: validators return pass/fail diagnostics and exit codes. Judgment
work belongs to audit or improve workflows.

## Invocation

```bash
/arc-validate
/arc-validate all
/arc-validate smart
/arc-validate auto
/arc-validate summary
/arc-validate parallel
/arc-validate links frontmatter
/arc-validate links,frontmatter
```

The skill maps directly to:

```bash
python3 rites/validate.py
python3 rites/validate.py links frontmatter
python3 rites/validate.py smart
python3 rites/validate.py parallel
```

## Validator Selectors

| Selector | Rite |
|---|---|
| `structure` | `validate_structure.py` |
| `encoding` | `validate_encoding.py` |
| `portability` | `validate_portability.py` |
| `naming` | `validate_naming.py` |
| `semantics` | `validate_semantics.py` |
| `format` | `validate_format.py` |
| `frontmatter` | `validate_frontmatter.py` |
| `links` | `validate_links.py` |
| `orphans` | `validate_orphans.py` |
| `provenance` | `validate_provenance.py` |
| `skill-refs` | `validate_skill_refs.py` |
| `security` | `validate_security.py` |
| `doc-trees` | `validate_doc_trees.py` |

## Report

Report any failed validators with diagnostics grouped by file and line when
available. Exit code 0 means the selected validators passed; exit code 1 means
one or more selected validators failed; exit code 2 means the selector or mode
was invalid.

## Related

- Validator hub -> [[invocations/arcana/validators/validators|validators]]
- Arcana improvement -> [[invocations/arcana/improve_arcana|improve arcana]]
- Grimoire mechanical validation -> [[invocations/grimoire/validators/validate|validate]]
