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
| _None_ | - | No open deferred architecture items. | - | - |

## Suggested Implementation Sequence

No open implementation items.

## Update Triggers

Update this backlog when:

- `/arc-improve` defers an item with P1 or P2 impact.
- A deferred item is implemented, rejected, or split.
- A new release changes one of the primary owner surfaces.
- A future architecture review finds the same drift risk again.

Do not update this file for small local cleanup that can be applied inside the
current pass. Those belong in the change itself and, if user-visible, in
`CHANGELOG.md`.
