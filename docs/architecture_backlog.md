---
type: reference
title: "S-tier Architecture Backlog"
aliases: ["architecture-backlog", "s-tier-backlog", "deferred-architecture-items"]
tags: [type/reference, arcana/docs, scope/quality]
authority: grimoire
last_verified: 2026-11-11
---

# S-tier Architecture Backlog

## Purpose

Durable queue for architecture work that needs maintainer review, sequencing,
or explicit approval before implementation: items found during `/arc-improve`
and `invocations/arc/quality/review_architecture.md`, and the open items of
the current release program.

This file is not a release note and is not a substitute for `CHANGELOG.md`.
It lists what is open, nothing else: an item leaves this file in the change
that implements or rejects it.

## How To Use This Backlog

- Add items only when the change is too broad for the current `/arc-improve`
  pass, affects public command behavior, touches release/install behavior, or
  needs a new contract before implementation.
- Keep each item stable enough that a maintainer can name its ID and an agent
  can begin with the listed owner, first slice, and validation profile.
- Remove an item in the same change that implements or rejects it; the
  changelog entry and the commit carry the history.
- If a future architecture review discovers the same concern again, merge it
  into the existing item instead of adding a duplicate.

Priority labels:

| Priority | Meaning |
|---|---|
| P0 | Blocking correctness or data-safety issue; implement before release. |
| P1 | High-leverage S-tier work; architecture remains correct but future drift or maintenance cost is likely. |
| P2 | Important scalability or clarity improvement; can wait behind P1 items. |
| P3 | Useful polish, generated convenience, or follow-up after larger contracts exist. |

## Release Program: Grimoire for Everyone

Target population for every item: a business-development lead, an HR
representative, a systems engineer, or an IT administrator at a company with a
self-hosted GitLab behind a VPN, using Claude Code or Codex, who will never read
`docs/`. The engineer path must keep working unchanged or get strictly simpler.

Facts the open items are designed against:

- Claude Code and Codex both have plugin systems with marketplaces. Codex reads
  a Claude Code `.claude-plugin/marketplace.json`, so one git repository can
  serve both. The Codex IDE extension does not load plugins; Codex in the IDE
  reads skills from `~/.agents/skills` and instructions from `~/.codex/AGENTS.md`.
- Claude Code copies a plugin from a directory marketplace into a versioned
  cache keyed by commit, so a grimoire cannot be a plugin without duplicating
  its whole content on every commit. Grimoire skills register as flat skill
  directories; only Arcana itself can be a plugin.
- A Claude Code `SessionStart` command hook's stdout is injected as session
  context (10,000-character cap).
- Claude Code honours a skill's `!cat` directive only for files inside the
  session's working directories, and an administrator can disable skill shell
  execution; registration therefore inlines every invocation into the generated
  skill.
- Claude Code administrators can force-install a marketplace and its plugins
  through managed settings; private git hosts work through the user's stored
  git credential.

### Decisions

| ID | Decision | Position |
|---|---|---|
| D1 | Distribution of the engine to agents | Claude Code: Arcana is a plugin (`grm` and `arc` command families), installed from a marketplace, with namespaced skill names (`/grm:add`). Codex, Cursor, Copilot: flat skill registration rendered from the same skill sources by the same rite. The engine checkout stays at `~/grimoires/arcana` for every agent; the plugin is a thin carrier. |

### Open Items

| ID | Priority | Item | Primary owner | Why queued |
|---|---|---|---|---|
| _None_ | - | No open deferred architecture items. | - | - |

## Suggested Implementation Sequence

No open implementation items.

## Update Triggers

Update this backlog when:

- `/arc-improve` defers an item with P1 or P2 impact.
- An item is implemented, rejected, or split.
- A new release changes one of the primary owner surfaces.
- A future architecture review finds the same drift risk again.

Do not update this file for small local cleanup that can be applied inside the
current pass. Those belong in the change itself and, if user-visible, in
`CHANGELOG.md`.
