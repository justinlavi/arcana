---
type: playbook
title: "Validate Grimoire"
aliases: ["grimoire-validate", "mechanical-grimoire-validation"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-06-03
---

# Invocation: Validate Grimoire

## Purpose

Run deterministic, script-backed validators against the resolved active
grimoire. This workflow is mechanical: validators return pass/fail diagnostics
and exit codes. Judgment work belongs to `/grm-audit-semantics`,
`/grm-audit-boundaries`, or `/grm-health-check`.

## Invocation

From a registered grimoire directory:

```bash
/grm-validate
/grm-validate all
/grm-validate smart
/grm-validate auto
/grm-validate summary
/grm-validate parallel
/grm-validate links frontmatter
/grm-validate links,frontmatter
```

The skill maps directly to:

```bash
python3 ARCANA_HOME/rites/validate.py --grimoire GRIMOIRE_ROOT
python3 ARCANA_HOME/rites/validate.py --grimoire GRIMOIRE_ROOT links frontmatter
python3 ARCANA_HOME/rites/validate.py --grimoire GRIMOIRE_ROOT smart
python3 ARCANA_HOME/rites/validate.py --grimoire GRIMOIRE_ROOT parallel
```

## Validator Selectors

| Selector | Rite |
|---|---|
| `structure` | `validate_grimoire_structure.py` |
| `encoding` | `validate_encoding.py` |
| `portability` | `validate_portability.py` |
| `format` | `validate_format.py` |
| `frontmatter` | `validate_frontmatter.py` |
| `links` | `validate_links.py` |
| `orphans` | `validate_orphans.py` |
| `provenance` | `validate_provenance.py` |
| `doc-trees` | `validate_doc_trees.py` |

## Report

Report any failed validators with diagnostics grouped by file and line when
available. Exit code 0 means the selected validators passed; exit code 1 means
one or more selected validators failed; exit code 2 means the selector or mode
was invalid.

## Related

- Validator hub -> [[invocations/grm/validators/validators|validators]]
- Semantic audit -> [[invocations/grm/audit_semantics|audit semantics]]
- Boundary audit -> [[invocations/grm/audit_boundaries|audit boundaries]]
