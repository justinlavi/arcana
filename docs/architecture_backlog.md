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
| AB-11 | P1 | Generic publishing: stage and audit as rites, generator templates, CI templates for GitLab Pages, GitHub Pages, Cloudflare | new `rites/stage_publish.py`, `rites/audit_publish.py`, new `formulae/publish/`, new `invocations/grm/publish.md` | New contract; japan-grimoire migration proves it. |
| AB-15 | P2 | Layperson documentation and product naming | `README.md`, `docs/installation.md`, new `docs/getting_started.md`, `formulae/grimoire/README.md` | The command surface and install path are settled. |
| AB-16 | P3 | Grimoire skills auto-load by path | grimoire `skills/**/SKILL.md` via `paths:` frontmatter | Claude-only convenience. |

### Item Details

#### AB-11 Generic publishing (P1)

A company with a self-hosted GitLab publishes a grimoire to GitLab Pages behind
project membership, built by CI on every push, with no vendored generator.

First slice:

- `rites/stage_publish.py` (flatten `chapters/`, rewrite full-path wikilinks
  and `sources:` paths, carry chapter-local sources, preserve casing) and
  `rites/audit_publish.py` (secret audit with BLOCKER/WARNING and an allowlist
  file): deterministic, cross-platform, JSON envelopes.
- `formulae/publish/quartz/` with `quartz.config.ts` and layout templates that
  read the staged content directory, and `formulae/publish/ci/` with
  `gitlab-pages.yml`, `github-pages.yml`, and `cloudflare-pages.md` that run
  stage, audit, `npx quartz build` at a pinned version, and publish `public/`.
  The generator is installed in CI or in a gitignored `publish/quartz/`.
- `invocations/grm/publish.md`: `grm-publish init <target>` scaffolds
  `publish/` from the formulae; `grm-publish build` runs stage, audit, build
  locally; `grm-publish check` audits only, as the tenth grimoire verb.
- Migrate `japan-grimoire/publish/` to the generic shape as the proof, keeping
  its Cloudflare deployment working.

Validation profile: rite tests on the fixture grimoire, a CI job that stages
and audits the fixture. Compatibility: MINOR; `publish/` stays excluded from
validation.

#### AB-15 Layperson documentation and product naming (P2)

A reader who is not an engineer meets "Grimoire" as the product, sees one
install sentence per agent, and learns the day-to-day verbs. Arcana is
mentioned once as the engine they never touch.

First slice: `docs/getting_started.md` for the non-engineer personas;
`README.md` restructured with that page first and the engineering material
after; `formulae/grimoire/README.md` installation section reduced to the
install line and `/grm-setup`.

#### AB-16 Grimoire skills auto-load by path (P3)

Grimoire skills can declare `paths:` so Claude loads them when the user works
under the grimoire directory. Convenience only; Claude-specific.

## Suggested Implementation Sequence

1. AB-11, including the japan-grimoire migration.
2. AB-15, AB-16.

## Update Triggers

Update this backlog when:

- `/arc-improve` defers an item with P1 or P2 impact.
- An item is implemented, rejected, or split.
- A new release changes one of the primary owner surfaces.
- A future architecture review finds the same drift risk again.

Do not update this file for small local cleanup that can be applied inside the
current pass. Those belong in the change itself and, if user-visible, in
`CHANGELOG.md`.
