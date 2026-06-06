---
type: reference
title: "Validate Frontmatter"
aliases: ["validate-frontmatter"]
tags: [arcana/invocations, type/reference, scope/quality]
authority: grimoire
last_verified: 2026-05-12
---

# Validate Arcana Frontmatter

## Purpose

Mechanically check every authored page's YAML frontmatter against the canonical [[docs/page_schema|page schema]]. Failures: missing frontmatter, unknown `type`, source wrappers outside `sources/`, missing required fields for the type, malformed `last_verified`, broken `sources:` paths, malformed YAML lists.

`SKILL.md` files are exempt - they use a different agent-defined schema. `README.md`, `CHANGELOG.md`, `log.md`, `VERSION` are exempt by name.

## Invocation

```
/arc-validate frontmatter
```

Or directly:

```bash
python3 ARCANA_HOME/rites/validate_frontmatter.py
```

For an active grimoire, use `/grm-validate frontmatter`.

## What gets checked

See [[docs/page_schema|page schema]] for the full required-fields matrix per `type`.

In short:

1. YAML frontmatter delimited by `---` exists.
2. `type:` is one of `hub | concept | entity | source | playbook | reference | log-entry`.
3. The required-fields matrix holds for the declared `type`.
4. `authority:` (when present) is one of `external | grimoire | hybrid`.
5. `type: source` is reserved for source wrappers under `sources/`.
6. `sources:` paths beginning with `sources/` resolve on disk.
7. `last_verified:` parses as `YYYY-MM-DD`.

## When to run

- After creating or editing any page.
- As a phase of `/arc-improve`.
- As a pre-commit / pre-release gate.

## Common failures and fixes

- **Missing frontmatter** -> prepend a `---` block. See `formulae/page.formula.md` for a starting point.
- **Missing `tags:`** -> every page needs at least one tag, typically `chapter/<chapter>` or `arcana/<area>`.
- **`type: source` outside `sources/`** -> use a wiki page type such as `concept`, `entity`, `playbook`, or `reference`, then cite the source in `sources:`.
- **Source path doesn't resolve** -> either the source was renamed (provenance broke) or never filed. Re-ingest or fix the path.
- **`last_verified` malformed** -> must be ISO date `YYYY-MM-DD`.

## Related

- Schema: [[docs/page_schema|page schema]]
- Validator suite: [[invocations/arc/validators/validators|validators]]
- Provenance: [[invocations/arc/validators/validate_provenance|validate provenance]]
