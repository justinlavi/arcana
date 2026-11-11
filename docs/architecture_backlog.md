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
| D6 | Consolidate the command surface | Proposed, awaiting maintainer sign-off; see [Command consolidation](#command-consolidation-d6). |

### Open Items

| ID | Priority | Item | Primary owner | Why queued |
|---|---|---|---|---|
| AB-07 | P1 | Arcana as a Claude Code plugin | new `.claude-plugin/`, `rites/sync_skills.py`, `rites/data/agent_targets.json` | New contract; public command namespace (D1). |
| AB-08 | P1 | Session-start context hook: routing block, installed grimoires, drift nudge | new `hooks/hooks.json`, new `rites/session_context.py`, `rites/summon_state.py` | Depends on AB-07 for Claude; Codex keeps file injection. |
| AB-11 | P1 | Generic publishing: stage and audit as rites, generator templates, CI templates for GitLab Pages, GitHub Pages, Cloudflare | new `rites/stage_publish.py`, `rites/audit_publish.py`, new `formulae/publish/`, new `invocations/grm/publish.md` | New contract; japan-grimoire migration proves it. |
| AB-12 | P2 | One Python launcher for every platform | new `bin/arcana` (sh) and `bin/arcana.cmd`, every `SKILL.md` and invocation that says `python3` | Sequence after AB-07 so the plugin `bin/` carries it. |
| AB-15 | P2 | Layperson documentation and product naming | `README.md`, `docs/installation.md`, new `docs/getting_started.md`, `formulae/grimoire/README.md` | Write after AB-07 and D6 settle the real command surface. |
| AB-16 | P3 | Grimoire skills auto-load by path | grimoire `skills/**/SKILL.md` via `paths:` frontmatter | Claude-only convenience; after AB-07. |

### Command consolidation (D6)

Goal: fewer verbs, each one a plain-language intent, no two commands whose
names a newcomer has to tell apart ("update" versus "sync", "validate" versus
"health-check", "add" versus "import").

Proposed `/grm-*` surface, nine verbs:

| Verb | Absorbs | What it does |
|---|---|---|
| `setup` | `adopt` | Join a grimoire by link, turn a folder into a grimoire, or route to `create`. `setup <url>` joins; `setup <folder>` adopts. |
| `create` | - | Start a grimoire from scratch (conversational scaffold). |
| `add` | `import` | Put knowledge in. A topic or pasted text is authored; a path to a file, a folder, or `inbox/` is filed as a source. One verb, polymorphic on its argument. |
| `save` | - | Share what you changed: validate, commit, pull, push. |
| `update` | `sync` | Bring everything current: pull Arcana and every grimoire, reconcile library, skills, and routing blocks, heal. `update skills`, `update library`, `update agentfile` reconcile one surface without pulling. |
| `check` | `validate`, `health-check`, `audit-semantics`, `audit-boundaries`, `repair-links` | Evaluate the grimoire. `check` is the full health pass; `check quick` and `check <validator>` are the mechanical subset; `check naming` and `check boundaries` are the judgment audits; `check fix` applies the mechanical repairs (links). |
| `move` | - | Rename or move a page or chapter and fix every link. |
| `remove` | - | Delete a page or chapter and fix every link. |
| `help` | - | The catalog. |

Proposed `/arc-*` surface, five verbs: `update` (absorbs `sync`, with the same
scoped forms), `validate`, `improve`, `clean`, `help`. `arc-adopt` goes;
`/grm-setup <folder>` covers a maintainer adopting a directory.

Consequences to confirm before implementation:

- Public command removals: `grm-adopt`, `grm-import`, `grm-sync`,
  `grm-validate`, `grm-health-check`, `grm-audit-semantics`,
  `grm-audit-boundaries`, `grm-repair-links`, `arc-adopt`, `arc-sync`. The
  registration rite removes stale managed skills on the next sync, so no user
  keeps a dead command.
- Invocations merge accordingly: `add` carries the authoring and filing
  modes; `check` carries the health, audit, and repair phases; `update`
  carries the sync sub-targets. Generated skills stay under 500 lines by
  keeping phase detail in `references/` files beside each `SKILL.md`.
- Command-surface, rite-profile, and routing-block contracts are updated in
  the same change; `docs/skills.md` is regenerated.
- japan-grimoire's own skills keep their names (`jpn-travel-*`); grimoire
  skill naming is not part of this decision.

### Item Details

#### AB-07 Arcana as a Claude Code plugin (P1)

Arcana's repository gains `.claude-plugin/marketplace.json` listing the `grm`
and `arc` plugins from inside the same repository, each with a `plugin.json`
whose `version` is `VERSION`. Skill sources keep `{{SKILL_PREFIX}}` and
`{{ARCANA_PATH}}` as the rendering seam; one rite renders both the plugin
layout (paths through `${CLAUDE_PLUGIN_ROOT}`) and the flat registration
(absolute paths), so the two cannot drift. The plugin is a thin carrier
(skills, hook, launcher); its session-start hook clones the engine into
`~/grimoires/arcana` if absent and fast-forwards it when clean, pinned to the
plugin's version tag, so every agent runs the same rites from the same
checkout. `ARCANA_HOME` resolves in this order: the `grm` plugin root's
engine path, the library, `~/grimoires/arcana`.

Rollout at a company: an administrator sets `extraKnownMarketplaces` and
`enabledPlugins` in managed settings once; every Claude Code user then has
Grimoire with auto-update and no manual steps. Access to a private host uses
the credential git already stores.

Open questions for the first slice: whether `!cat` expands inside the Claude
Code VS Code extension (plugins, hooks, and settings are shared with the CLI),
and which built-in commands the extension hides.

Validation profile: `claude plugin validate .` in CI, `summon.py --check`
recognising plugin-mode installs, full suite. Compatibility: MINOR for
grimoires; the public command namespace is the D1 position.

#### AB-08 Session-start context hook (P1)

A `SessionStart` command hook in the `grm` plugin prints the canonical routing
block, so the text is always the installed version's, plus what a static block
cannot carry: the installed grimoires with one-line descriptions, and a
one-line drift or behind-upstream nudge from `summon.py --check` so the agent
offers `/grm-update` at the right moment.

First slice: `hooks/hooks.json` with one `SessionStart` command that runs
`python rites/session_context.py` (read-only, fast; the git fetch for the
behind-upstream check is time-boxed and skipped offline). Claude Code then
needs no `inject_agent_file.py`; Codex keeps file injection. The block shrinks
to routing essentials; schema detail moves to a skill the agent loads on
demand.

Validation profile: hook output under the 10,000-character cap, `summon.py
--check` parity. Compatibility: MINOR.

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
  locally; `grm-publish check` audits only. (Under D6 this becomes either
  a tenth verb, `grm-publish`, or a scope of `save`.)
- Migrate `japan-grimoire/publish/` to the generic shape as the proof, keeping
  its Cloudflare deployment working.

Validation profile: rite tests on the fixture grimoire, a CI job that stages
and audits the fixture. Compatibility: MINOR; `publish/` stays excluded from
validation.

#### AB-12 One Python launcher (P2)

`bin/arcana` (POSIX sh) and `bin/arcana.cmd` locate a Python 3.10+
interpreter (`python3`, `python`, `py -3`) and run `rites/<name>.py` with the
remaining arguments; skills and invocations say `arcana validate --summary`
instead of naming an interpreter. With AB-07 the plugin's `bin/` is on the
agent's PATH automatically.

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

1. D6 sign-off, then the consolidation (it reshapes the skill tree that AB-07
   packages).
2. AB-07, AB-08, AB-12.
3. AB-11, including the japan-grimoire migration.
4. AB-15, AB-16.

## Update Triggers

Update this backlog when:

- `/arc-improve` defers an item with P1 or P2 impact.
- An item is implemented, rejected, or split.
- A new release changes one of the primary owner surfaces.
- A future architecture review finds the same drift risk again.

Do not update this file for small local cleanup that can be applied inside the
current pass. Those belong in the change itself and, if user-visible, in
`CHANGELOG.md`.
