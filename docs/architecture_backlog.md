---
type: reference
title: "S-tier Architecture Backlog"
aliases: ["architecture-backlog", "s-tier-backlog", "deferred-architecture-items"]
tags: [type/reference, arcana/docs, scope/quality]
authority: grimoire
last_verified: 2026-05-25
---

# S-tier Architecture Backlog

## Purpose

Durable queue for deferred architecture opportunities found during
`/arc-improve` and `invocations/arcana/quality/review_architecture.md`.

The architecture review report should mention deferred items in chat, but
large items also belong here when they need maintainer review, sequencing, or
explicit approval before implementation. This file is not a release note and
is not a substitute for `CHANGELOG.md`; it is the working design backlog for
moving Arcana from "correct and maintainable" to "self-explaining,
contract-driven, low-drift, and deeply testable."

## How To Use This Backlog

- Add items only when the change is too broad for the current `/arc-improve`
  pass, affects public command behavior, touches release/install behavior, or
  needs a new contract before implementation.
- Keep each item stable enough that a maintainer can name its ID
  and an agent can begin with the listed owner, first slice, and validation
  profile.
- When an item is implemented, either remove it in the same change or mark it
  as resolved with the release or commit where the work landed.
- If a future architecture review discovers the same concern again, merge it
  into the existing item instead of adding a duplicate.

Priority labels:

| Priority | Meaning |
|---|---|
| P0 | Blocking correctness or data-safety issue; implement before release. |
| P1 | High-leverage S-tier work; architecture remains correct but future drift or maintenance cost is likely. |
| P2 | Important scalability or clarity improvement; can wait behind P1 items. |
| P3 | Useful polish, generated convenience, or follow-up after larger contracts exist. |

## Decision Queue

| ID | Priority | Item | Primary owner | Why deferred |
|---|---|---|---|---|
| ST-010 | P3 | Source wrapper and provenance boundary clarification | source formula, provenance docs/validators | Needs design judgment before adding mechanical checks. |

## ST-010: Source Wrapper And Provenance Boundary Clarification

Priority: P3

Status: Deferred

Primary owner: `formulae/source.formula.md`, `docs/page_schema.md`,
`docs/operating_model.md`, `rites/validate_provenance.py`

Current evidence:

- `sources/` is immutable source storage.
- Pages with `authority: external` or `hybrid` must cite stable sources.
- Arcana has a source formula, provenance validator, and source-layer docs,
  but source wrappers versus raw artifacts can still require human judgment.

Finding:

The provenance model is correct, but the line between raw source artifact,
source wrapper page, and authored chapter page could be clearer before adding
more validation.

Desired S-tier endpoint:

- Clear guidance for when `sources/` should contain raw copied artifacts,
  source wrapper markdown, external URLs, or both.
- Validation rules that stay mechanical: source path exists, inbox is not
  cited, external/hybrid pages have stable source pointers.
- AI judgment remains responsible for whether a source is substantively
  sufficient.

First implementable slice:

1. Clarify source-wrapper rules in `docs/page_schema.md` and
   `formulae/source.formula.md`.
2. Add only narrow mechanical checks if a stable rule emerges.

Blast radius:

Low-medium. Mostly docs, with possible provenance validator tweaks.

Validation profile:

- `python rites/validate_provenance.py`
- `python rites/validate.py --parallel`

Read-path delta:

Agents ingesting sources can classify artifacts without guessing whether to
create a wrapper, cite a raw file, or cite an external URL.

## Suggested Implementation Sequence

1. ST-010 after the validation and catalog contracts settle.

## Update Triggers

Update this backlog when:

- `/arc-improve` defers an item with P1 or P2 impact.
- A deferred item is implemented, rejected, or split.
- A new release changes one of the primary owner surfaces.
- A future architecture review finds the same drift risk again.

Do not update this file for small local cleanup that can be applied inside the
current pass. Those belong in the change itself and, if user-visible, in
`CHANGELOG.md`.
