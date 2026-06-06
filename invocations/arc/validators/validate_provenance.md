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

Confirm every page declaring `authority: external` or `authority: hybrid`
lists at least one source in `sources:`, and that any source path beginning
with `sources/` resolves to an existing artifact. URLs and out-of-grimoire
paths are not network-checked.

The same rite validates source wrapper Markdown under `sources/`: wrappers
must declare `type: source`, use `authority: external`, list their original
URL, capture origin, or sibling raw artifact in `sources:`, and avoid
self-citation.

## Invocation

```
/arc-validate provenance
```

Or directly:

```bash
python3 ARCANA_HOME/rites/validate_provenance.py
```

For an active grimoire, use `/grm-validate provenance`.

## When to run

- After adding Arcana pages with external/hybrid authority.
- After moving or renaming files in `sources/`.
- As a pre-release gate.

## Common failures

- **`sources:` empty on external page** -> either downgrade authority to `grimoire` (the page IS the source of truth), or add a real source.
- **`sources/<path>` does not resolve** -> either the artifact was renamed (provenance broke - rename it back or fix the page) or the path is a typo.
- **`sources:` not a YAML list** -> fix to `sources: ["sources/...", "..."]` or multi-line list.
- **Source wrapper authority is not external** -> source wrappers capture external material; authored synthesis belongs under `chapters/`.
- **Source wrapper cites itself** -> cite the original URL, capture origin, or sibling raw artifact instead.

## Related

- Schema: [[docs/page_schema|page schema]]
- Frontmatter validator: [[invocations/arc/validators/validate_frontmatter|validate frontmatter]]
- Grimoire provenance validator: [[invocations/grm/validators/validate_provenance|validate provenance]]
