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
| ST-003 | P1 | Skill registration ownership and prefix-collision safety | `rites/register_skills.py`, agent skill dirs | Mutates user agent directories; cleanup rules need careful ownership boundaries. |
| ST-004 | P1 | Summoning Rite behavior contract and GUI/core parity | `rites/summon*`, `.github/`, install docs | Installer behavior spans shell, Python, GUI, release assets, and docs. |
| ST-005 | P2 | Mutating rite plan/apply/idempotency profile | mutating rites and invocations | Broad behavioral standard across multiple write-capable rites. |
| ST-007 | P2 | Agent target registry and instruction-block single source | agent docs, registration/update rites | Agent support is described across several surfaces and can drift. |
| ST-008 | P2 | Grimoire validation orchestrator and profiles | grimoire validators, `/grm-improve` | Would add or reshape public validation workflow. |
| ST-009 | P3 | Richer generated skill catalog | `rites/sync_docs.py`, `docs/skills.md` | Needs catalog rendering and tests against the command-surface contract. |
| ST-010 | P3 | Source wrapper and provenance boundary clarification | source formula, provenance docs/validators | Needs design judgment before adding mechanical checks. |

## ST-003: Skill Registration Ownership And Prefix-Collision Safety

Priority: P1

Status: Deferred

Primary owner: `rites/register_skills.py`,
`invocations/agent/register_skills.md`,
`invocations/grimoire/register_skills.md`,
`docs/agent_configuration.md`

Current evidence:

- Skill registration writes into agent-owned directories such as
  `~/.claude/skills/` and `~/.codex/skills/`.
- Arcana registers both platform skills and grimoire skills, while downstream
  grimoires can define their own prefixes.
- Stale generated skills and prefix collisions are user-visible, but cleanup
  must not remove user-authored skills or another tool's files.

Finding:

Registration needs a stronger ownership model before Arcana can safely get
more aggressive about stale cleanup or collision repair.

Desired S-tier endpoint:

- Generated skills carry an Arcana ownership marker that identifies source
  repo, grimoire key, command name, and generation version.
- Registration produces a plan before it writes: create, update, skip,
  collision, stale-owned cleanup.
- Prefix collisions are detected before writing and reported with the owning
  grimoire or command family.
- Cleanup only removes files Arcana can prove it generated.
- Temp-HOME tests cover clean install, update, stale removal, collision, and
  user-authored file preservation.

First implementable slice:

1. Add a dry-run/plan mode to `register_skills.py` that reports intended
   writes and collisions without changing files.
2. Add ownership metadata to newly generated skill files or adjacent manifest
   files.
3. Add temp-HOME tests for collision detection and user-authored preservation.
4. Only then add stale-owned cleanup.

Blast radius:

High because this mutates user agent directories. The work should be staged
and heavily tested before any automatic cleanup behavior changes.

Validation profile:

- New temp-HOME pytest coverage for registration.
- Manual smoke test against disposable `.codex/skills` and `.claude/skills`
  roots.
- `python rites/validate.py --parallel`

Read-path delta:

Agents and users would see exactly why a skill was written, skipped, or
blocked, instead of relying on implicit registration behavior.

## ST-004: Summoning Rite Behavior Contract And GUI/Core Parity

Priority: P1

Status: Deferred

Primary owner: `rites/summon.sh`, `rites/summon.py`,
`rites/summon_core.py`, `rites/summon_gui.py`,
`rites/build_summon_binary.py`, `.github/workflows/summon-release.yml`,
`docs/installation.md`, `docs/release.md`

Current evidence:

- The Summoning Rite has shell bootstrap behavior, Python source behavior,
  binary release behavior, GUI behavior, CLI behavior, and GitHub Actions
  release behavior.
- Docs describe release assets, binary/source fallback, Linux GUI source
  preference, Windows Git Bash support, checksums, retry controls, and agent
  setup.
- Tests cover some core helper behavior, but there is no single contract that
  defines parity between CLI, GUI, source, and release paths.

Finding:

The installer is powerful and user-facing. Its behavior is documented, but the
contract is distributed across code and docs. Future installer improvements
could drift between GUI and core behavior unless parity is named and tested.

Desired S-tier endpoint:

- A concise summoning contract that names required behaviors independent of
  transport: install Arcana, optionally discover/clone grimoires, write the
  library, inject/update agent blocks, register skills, and report failures.
- A capabilities matrix for shell bootstrap, Python CLI, Python GUI, and
  release binary modes.
- Tests that exercise core decisions without requiring network or GUI.
- Documentation generated from, or checked against, the contract where
  practical.

First implementable slice:

1. Add a contract section or small contract document for summon behavior.
2. Add tests for mode-selection and parity-critical decisions in
   `summon_core.py`.
3. Add a review checklist to `docs/release.md` for GUI/core parity before
   release.

Blast radius:

Medium-high. The first slice can be mostly documentation and tests, but later
work may affect installer UX and release automation.

Validation profile:

- `python -m pytest tests/test_summon_core.py`
- Local source-mode summon dry smoke where feasible.
- Release workflow test build before publishing assets.

Read-path delta:

A maintainer can answer "what must every summon mode do?" from one contract
instead of reconciling shell, Python, GUI, docs, and release notes.

## ST-005: Mutating Rite Plan/Apply/Idempotency Profile

Priority: P2

Status: Deferred

Primary owner: `rites/register_skills.py`, `rites/sync_library.py`,
`rites/sync_docs.py`, `rites/adopt_grimoire.py`, `rites/repair_links.py`,
`rites/clean_artifacts.py`, `invocations/arcana/quality/validate_rites.md`

Current evidence:

- Some mutating rites already distinguish dry-run from apply.
- Other rites write because writing is their primary job.
- The rite quality invocation asks whether mutating rites have a dry-run or
  apply split, but Arcana does not yet define one shared profile for plan
  output, exit codes, and idempotency tests.

Finding:

S-tier maintainability needs a consistent mental model for write-capable
rites. The current pattern is mostly good but not yet contract-shaped.

Desired S-tier endpoint:

- Every mutating rite declares one of: read-only, plan/apply, apply-only by
  nature, or append-only.
- Plan output is clear enough for agents to summarize and users to approve.
- Exit codes distinguish success, validation failure, and operational error
  where useful.
- Temp-directory or temp-HOME tests prove idempotency and scoped writes.
- Invocations state whether they are allowed to run the rite directly or need
  user confirmation first.

First implementable slice:

1. Add the profile to `docs/script_vs_ai.md` and
   `invocations/arcana/quality/validate_rites.md`.
2. Classify current rites in a table.
3. Pick one high-risk rite, likely `register_skills.py`, and bring it into
   the new profile with tests.

Blast radius:

Medium. Mostly documentation at first, then staged rite changes.

Validation profile:

- Focused tests for each updated rite.
- `python rites/validate.py --parallel`

Read-path delta:

Agents can know before running a rite whether it plans, writes, appends, or
needs human confirmation.

## ST-007: Agent Target Registry And Instruction-Block Single Source

Priority: P2

Status: Deferred

Primary owner: `rites/register_skills.py`, agent update rites,
`rites/templates/grimoire_block.md`, `docs/agent_configuration.md`,
`docs/installation.md`

Current evidence:

- Agent support appears in installation docs, agent configuration docs,
  registration rites, update invocations, and the injected Grimoire block.
- Some agents support skill registration and instruction-file updates; others
  use manual instruction blocks only.
- This distinction is important and has already required wording fixes.

Finding:

Agent support is a matrix, but Arcana does not yet have one source that both
code and docs can consult.

Desired S-tier endpoint:

- A small agent-target registry that names each supported or documented agent,
  its instruction file, skill directory behavior, auto-configuration support,
  and limitations.
- Docs and registration/update logic either read that registry or are checked
  against it.
- Adding a new agent target becomes a data change plus focused implementation,
  not a hunt through prose.

First implementable slice:

1. Inventory current agent targets in a structured file or canonical doc
   table.
2. Add tests or a validator that checks docs mention only registered targets.
3. Migrate registration/update docs to link to the registry.

Blast radius:

Medium. The first slice is mostly contract creation; later slices may change
registration and update logic.

Validation profile:

- New registry consistency test or validator.
- `python rites/validate.py --parallel`

Read-path delta:

Users and agents can learn "what does Arcana actually configure for this
agent?" from one target matrix.

## ST-008: Grimoire Validation Orchestrator And Profiles

Priority: P2

Status: Deferred

Primary owner: `rites/validate_*.py`, grimoire validator invocations,
`invocations/grimoire/improve_grimoire.md`, `skills/grimoire/validate-*`

Current evidence:

- Arcana has `/arc-validate-all` backed by `rites/validate.py`.
- Grimoire validation exists as individual `/grm-validate-*` skills and as
  phases inside `/grm-improve`.
- There is not yet a first-class grimoire equivalent that says "run the full
  deterministic grimoire validator profile" outside the broader improvement
  workflow.

Finding:

The active-grimoire validation story works, but it is less direct than the
Arcana validation story. S-tier parity would make grimoire audits easier for
humans, agents, CI, and future skill registration.

Desired S-tier endpoint:

- A grimoire validation orchestrator or profile mode that runs deterministic
  grimoire validators against an active grimoire.
- Clear distinction between mechanical validation profiles and judgment
  workflows such as `/grm-improve`, `/grm-lint`, and
  `/grm-analyze-semantics`.
- Optional public skill such as `grm-validate-all`, if the command-surface
  matrix approves adding it.
- Tests against good and bad fixture grimoires.

First implementable slice:

1. Decide whether to extend `rites/validate.py` with a grimoire profile or add
   a separate orchestrator.
2. Add tests against existing fixtures.
3. Only then add a public skill and invocation leaf.

Blast radius:

Medium-high because it may add a public command and change the recommended
grimoire maintenance path.

Validation profile:

- New orchestrator tests.
- Existing validator fixture tests.
- `python rites/validate.py --parallel`

Read-path delta:

Agents maintaining a grimoire can run one mechanical profile before deciding
whether deeper judgment work is needed.

## ST-009: Richer Generated Skill Catalog

Priority: P3

Status: Deferred

Primary owner: `rites/sync_docs.py`, `docs/skills.md`,
`rites/data/command_surface.json`

Current evidence:

- `docs/skills.md` is generated and useful.
- The catalog currently shows command and description, but not invocation
  owner, rite owner, mutation behavior, or validation profile.

Finding:

The generated catalog is good as a skill index. It can now become a stronger
operational map by rendering the command-surface metadata.

Desired S-tier endpoint:

- `docs/skills.md` remains generated, but includes enough metadata to route a
  command quickly.
- The catalog clearly distinguishes generated view from source of truth.
- Skill additions automatically update the command-surface view.

First implementable slice:

Use `rites/data/command_surface.json` to update `sync_docs.py` so the
generated catalog renders workflow owner, rite owner, guard, mutation profile,
and validation profile.

Blast radius:

Low-medium. The command-surface contract now provides the metadata source.

Validation profile:

- `python rites/sync_docs.py --apply`
- `python rites/validate.py --parallel`

Read-path delta:

Humans and agents can use the skill catalog as an operational index, not just
a list of command descriptions.

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

1. ST-005 first slice, because it defines the mutating-rite profile that
   registration should follow.
2. ST-003 after ST-005 or alongside its first slice, because registration is
   the highest-risk mutating rite.
3. ST-004 as its own focused pass before the next installer/release push.
4. ST-008 before adding `grm-validate-all`; any new command must update
   `rites/data/command_surface.json`.
5. ST-009 can now render richer metadata from the command-surface contract.

## Update Triggers

Update this backlog when:

- `/arc-improve` defers an item with P1 or P2 impact.
- A deferred item is implemented, rejected, or split.
- A new release changes one of the primary owner surfaces.
- A future architecture review finds the same drift risk again.

Do not update this file for small local cleanup that can be applied inside the
current pass. Those belong in the change itself and, if user-visible, in
`CHANGELOG.md`.
