# Invocation: Validate Arcana Semantics

## Purpose

Mechanical scan of Arcana for **deprecated terminology** and **hyphenated path examples**. Fast, deterministic, no judgment required.

For *intelligent* semantic analysis (naming quality, organizational discoverability, terminology design), use `/grm-domain-analyze-semantics` — this rite is intentionally not that.

## Invocation

```
/grm-arcana-validate-semantics
```

Also runs as part of `/grm-arcana-improve` (alongside the other validators).

## What the Rite Checks

The rite is `rites/validate_semantics.py`. Two checks, both data-driven:

1. **Deprecated terms** — any markdown file containing a term from
   [`rites/data/deprecated_terms.txt`](../../../rites/data/deprecated_terms.txt) is flagged with file:line. To deprecate a new term, add it to that file (one term per line). The data file is the single source of truth — do not list deprecated terms here.

2. **Hyphenated path examples** — paths like `chapters/example-name/` or `file-name.md` in body text are flagged. Arcana convention is `snake_case` for filesystem paths.

## Workflow

```bash
python3 rites/validate_semantics.py
```

Exit code: 0 if no violations, 1 if any violation is found.

## Exclusions

- `validate_semantics.md` (this file)
- `deprecated_terms.txt` (the data file — necessarily mentions all the terms)
- `invocations/arcana/quality/` (quality docs may discuss historical terms)

## Fixing Violations

1. **Deprecated term hits**: replace with the canonical equivalent. For roles previously called "The Keepers" / "Archmage" / "Domain Master" use "Arcana maintainer" or "domain lead". For "tome" use "grimoire". The `deprecated_terms.txt` file is the authoritative list of what to avoid; the canonical replacements live in [`docs/reference.md`](../../../docs/reference.md).
2. **Hyphenated example hits**: convert to snake_case (`chapters/example_name/`).

## Related

- **Rite**: [`rites/validate_semantics.py`](../../../rites/validate_semantics.py)
- **Data**: [`rites/data/deprecated_terms.txt`](../../../rites/data/deprecated_terms.txt) (single source of truth for the deprecated-term list)
- **Reference**: [`docs/reference.md`](../../../docs/reference.md) (canonical terminology)
- **Smart analysis**: `/grm-domain-analyze-semantics` (judgment-based, not mechanical)
- **Orchestrator**: [`improve_arcana.md`](../improve_arcana.md)
