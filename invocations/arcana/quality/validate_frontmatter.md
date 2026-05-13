---
type: reference
title: "Validate Frontmatter"
aliases: ["validate-frontmatter"]
tags: [arcana/invocations, type/reference, scope/quality]
authority: grimoire
last_verified: 2026-05-12
---

# Validate Frontmatter

## Purpose

Mechanically check every authored page's YAML frontmatter against the canonical [page schema](../../../docs/page_schema.md). Failures: missing frontmatter, unknown `type`, missing required fields for the type, malformed `last_verified`, broken `sources:` paths, malformed YAML lists.

`SKILL.md` files are exempt — they use a different agent-defined schema. `README.md`, `CHANGELOG.md`, `log.md`, `VERSION` are exempt by name.

## Invocation

```
/grm-arcana-validate-frontmatter
```

Or directly:

```bash
python3 GRIMOIRE_ARCANA/rites/validate_frontmatter.py
```

For a domain grimoire, `cd` into it first; the rite uses `GRIMOIRE_ARCANA` env var or its parent directory as root.

## What gets checked

See [`docs/page_schema.md`](../../../docs/page_schema.md) for the full required-fields matrix per `type`.

In short:

1. YAML frontmatter delimited by `---` exists.
2. `type:` is one of `hub | concept | entity | source | playbook | reference | log-entry`.
3. The required-fields matrix holds for the declared `type`.
4. `authority:` (when present) is one of `external | grimoire | hybrid`.
5. `sources:` paths beginning with `sources/` resolve on disk.
6. `last_verified:` parses as `YYYY-MM-DD`.

## When to run

- After creating or editing any page.
- As a phase of `/grm-arcana-improve` and `/grm-domain-improve`.
- As a phase of `/grm-domain-lint`.
- As a pre-commit / pre-release gate.

## Common failures and fixes

- **Missing frontmatter** → prepend a `---` block. See `formulae/page.formula.md` for a starting point.
- **Missing `tags:`** → every page needs at least one tag, typically `chapter/<chapter>` or `arcana/<area>`.
- **Source path doesn't resolve** → either the source was renamed (provenance broke) or never filed. Re-ingest or fix the path.
- **`last_verified` malformed** → must be ISO date `YYYY-MM-DD`.

## Related

- Schema: [`docs/page_schema.md`](../../../docs/page_schema.md)
- Validator suite: [`../validators/validators.md`](../validators/validators.md)
- Provenance: [`validate_provenance.md`](validate_provenance.md)
