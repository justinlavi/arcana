---
type: reference
title: "Validate Orphans"
aliases: ["validate-orphans"]
tags: [arcana/invocations, type/reference, scope/quality]
authority: grimoire
last_verified: 2026-05-12
---

# Validate Orphans

## Purpose

Detect pages no other page links to — neither via standard markdown links nor via wikilinks (resolved by stem or `aliases:` frontmatter). Orphans are pages the routing surface can't reach; they're either dead content or a missing hub pointer.

## Invocation

```
/grm-arcana-validate-orphans
```

Or directly:

```bash
python3 GRIMOIRE_ARCANA/rites/validate_orphans.py [--grimoire <path>]
```

## Exempt

- The grimoire root hub (`<grimoire>/<grimoire>.md`).
- `README.md`, `CHANGELOG.md`, `log.md`, `VERSION`.
- Everything under `sources/`.

Folder hubs are checked: an unreachable folder hub means the parent hub is missing a pointer.

## When to run

- As a phase of `/grm-domain-lint`.
- After bulk renames.
- After removing a hub or a chapter.

## Resolutions

For each orphan, three options:

1. **Wire it** — add a wikilink or markdown link from the appropriate hub.
2. **Promote it** — turn it into a hub itself if it represents a folder concept.
3. **Delete it** — the content is dead.

Don't auto-wire orphans during validation. Surface them for judgment.

## Related

- Schema: [`../../../docs/page_schema.md`](../../../docs/page_schema.md)
- Lint workflow: [`../../grimoire/lint.md`](../../grimoire/lint.md)
- Validator suite: [`../validators/validators.md`](../validators/validators.md)
