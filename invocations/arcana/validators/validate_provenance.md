---
type: reference
title: "Validate Provenance"
aliases: ["validate-provenance"]
tags: [arcana/invocations, type/reference, scope/quality]
authority: grimoire
last_verified: 2026-05-12
---

# Validate Arcana Provenance

## Purpose

Confirm every page declaring `authority: external` or `authority: hybrid` lists at least one source in `sources:`, and that any source path beginning with `sources/` resolves to an existing artifact. URLs and out-of-grimoire paths are not network-checked.

## Invocation

```
/arc-validate-provenance
```

Or directly:

```bash
python3 ARCANA_HOME/rites/validate_provenance.py
```

For an active grimoire, use `/grm-validate-provenance`.

## When to run

- After adding Arcana pages with external/hybrid authority.
- After moving or renaming files in `sources/`.
- As a pre-release gate.

## Common failures

- **`sources:` empty on external page** -> either downgrade authority to `grimoire` (the page IS the source of truth), or add a real source.
- **`sources/<path>` does not resolve** -> either the artifact was renamed (provenance broke - rename it back or fix the page) or the path is a typo.
- **`sources:` not a YAML list** -> fix to `sources: ["sources/...", "..."]` or multi-line list.

## Related

- Schema: [`../../../docs/page_schema.md`](../../../docs/page_schema.md)
- Frontmatter validator: [`validate_frontmatter.md`](validate_frontmatter.md)
- Grimoire provenance validator: [`../../grimoire/validators/validate_provenance.md`](../../grimoire/validators/validate_provenance.md)
