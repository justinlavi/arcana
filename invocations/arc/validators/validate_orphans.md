---
type: reference
title: "Validate Orphans"
aliases: ["validate-orphans"]
tags: [arcana/invocations, type/reference, scope/quality]
authority: grimoire
last_verified: 2026-05-12
---

# Validate Arcana Orphans

## Purpose

Detect pages no other page reaches through valid layer-specific links. Orphans are pages the routing surface can't reach; they're either dead content or a missing hub pointer.

## Invocation

```
/arc-validate orphans
```

Or directly:

```bash
python3 ARCANA_HOME/rites/validate_orphans.py
```

For an active grimoire, use `/grm-validate orphans`.

## Exempt

- The Arcana root hub (`arcana.md`).
- `README.md`, `CHANGELOG.md`, `log.md`, `VERSION`.
- Everything under `sources/`.

Folder hubs are checked: an unreachable folder hub means the parent hub is missing a pointer.

## When to run

- As a phase of `/arc-improve`.
- After bulk renames.
- After removing an Arcana hub or page.

## Resolutions

For each orphan, three options:

1. **Wire it** - add a link using the appropriate layer style: Markdown in public docs, wikilinks in vault/AI surfaces.
2. **Promote it** - turn it into a hub itself if it represents a folder concept.
3. **Delete it** - the content is dead.

Don't auto-wire orphans during validation. Surface them for judgment.

## Related

- Schema: [[docs/page_schema|page schema]]
- Validator suite: [[invocations/arc/validators/validators|validators]]
