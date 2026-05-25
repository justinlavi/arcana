---
type: playbook
title: "Review Arcana Architecture"
aliases: ["architecture-review", "arcana-architecture-review"]
tags: [arcana/invocations, type/playbook, scope/quality]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Review Arcana Architecture

## Purpose

Judgment-based review of Arcana's whole architecture: repository layout,
directory names, file names, source-of-truth boundaries, user-facing command
surfaces, AI-agent efficiency, and long-term maintainability.

Mechanical validators answer whether the current tree obeys known rules. This
invocation asks whether the rules, layout, and information flow still feel like
the right design.

## Invocation

Runs as a phase of `/arc-improve`. There is no standalone slash command.

## When to cast

- Before an Arcana release.
- After command-family, manifest, scaffold, installer, or validator changes.
- When docs feel correct but the system feels harder to explain than it should.
- When repeated maintenance work suggests a missing single source of truth.

## Workflow

### 1. Inventory every surface

Start with a complete file map, then classify each path by responsibility:

```bash
rg --files
rg --files docs invocations formulae rites skills tests
```

Review the whole repository, not only authored markdown:

| Surface | Review question |
|---|---|
| Root files | Do `arcana.md`, `README.md`, `CHANGELOG.md`, `VERSION`, `arcana.json`, `pyproject.toml`, `CONTRIBUTING.md`, and `LICENSE` each have one clear job? |
| `docs/` | Is each canonical concept documented in exactly one place, with other docs linking to it? |
| `invocations/` | Do family folders match `arcana.json`, and do hubs route without duplicating leaf content? |
| `formulae/` | Are templates treated as contracts, with placeholders documented in one canonical location? |
| `rites/` | Are scripts deterministic, shared through `_lib.py`, and small enough to audit? |
| `skills/` | Are skills thin pointers, grouped by command family, with no logic duplicated from invocations or rites? |
| `tests/` | Do fixtures cover the invariants Arcana claims to enforce? |
| `.github/` | Does automation match the release and build docs? |
| `.obsidian/` and `resources/` | Are tracked assets intentional, reusable, and documented only where users need them? |

Do not require router hubs for code, config, skill, fixture, asset, or hidden
tool directories. Hub conventions apply to knowledge-routing folders.

### 2. Dispatch parallel review lanes

For an S-tier pass, do not keep the entire review in one linear context when
subagents or parallel AI reviewers are available. Split the repo into isolated
lanes so each reviewer can go deep without competing for attention. If
subagents are unavailable, run the same lanes serially and keep their notes
separate until synthesis.

Keep the maintainer on the critical path: the maintainer owns validation,
final judgment, edits, and synthesis. Delegate sidecar analysis that can run
independently.

| Lane | Scope | Primary question |
|---|---|---|
| Root and docs | `README.md`, `arcana.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/*.md` | Are audience boundaries, canonical homes, and human/AI read paths obvious? |
| Invocations | `invocations/**/*.md` | Are workflows thin, routable, non-duplicative, and clear about when to use rites vs judgment? |
| Rites | `rites/*.py`, `rites/templates/`, `rites/data/` | Are scripts small enough to audit, deterministic, portable, and sharing helpers well? |
| Formulae and tests | `formulae/**/*`, `tests/**/*` | Do templates, managed scaffold files, fixtures, and tests encode the contracts Arcana claims? |
| Skills and agents | `skills/**/*/SKILL.md`, agent docs, registration/update flows | Are skills thin, discoverable, portable across agents, and generated views current? |
| Release and install | `.github/`, `docs/release.md`, `docs/installation.md`, summoning rites | Is install/update/release behavior documented once and resilient across platforms? |
| Cross-cutting AI efficiency | All surfaces | For common workflows, what is the shortest useful read path and where does it force inference? |

Give each lane the same output contract:

- `lane`: one of the lane names above.
- `scope_reviewed`: concrete files or globs inspected.
- `commands_run`: read-only checks run, or `none`.
- `findings`: top 5 findings, ordered by user impact and maintenance risk.
- Each finding includes `id`, `priority` (`P0`-`P3`), `evidence`
  (`file:line` references), `invariant`, `recommendation`, `action`
  (`apply_now`, `defer`, `codify`, `retain`), `blast_radius`, and
  `read_path_delta`.
- `deferred_opportunities`: changes too broad for the current pass.
- `workflow_updates`: instructions that should be added to future
  `/arc-improve` or architecture reviews.

Use this template for each delegated lane:

```text
Audit Arcana for S-tier architecture in this lane only.
Repo root: ARCANA_HOME.
Lane:
Scope:
Do not edit files unless explicitly assigned this lane's write scope.
Find source-of-truth drift, duplicated contracts, AI/human read-path friction,
missing tests, unsafe mutation behavior, and unclear ownership.
Return the lane output schema from review_architecture.md.
```

When worker agents are allowed to edit, assign disjoint write scopes. Otherwise
use read-only explorers and let the maintainer apply the integrated patch.

### 3. Synthesize lane reports

Merge the lane reports before editing. Look for:

- The same issue reported from two surfaces, which usually indicates a missing
  source of truth.
- Conflicting recommendations, which usually indicate unclear ownership or
  audience boundaries.
- Repeated "defer" items that deserve a roadmap section or future validator.
- Local edits that unlock multiple lanes without changing public behavior.

Build a synthesis matrix so findings are mergeable instead of prose-only:

| Finding ID | Lanes | Canonical owner | Apply/defer/codify | First step |
|---|---|---|---|---|
| `<stable-id>` | `<lanes>` | `<file or subsystem>` | `<decision>` | `<next action>` |

Grade the architecture with an explicit rubric:

| Grade | Meaning |
|---|---|
| A | Correct, coherent, validator-clean, and maintainable by the current maintainer. |
| S | Self-explaining to new maintainers and agents, contract-driven, low-drift, deeply testable, and scalable without relying on one person's memory. |

An S-tier recommendation should improve at least one of: deterministic read
paths, source-of-truth ownership, testable contracts, cross-agent portability,
or release/update resilience. Avoid novelty refactors that do not improve one
of those properties.

### 4. Build a source-of-truth map

List the facts Arcana repeats most often and name their canonical homes:

- Storage layers and routing: `docs/operating_model.md`
- Frontmatter schema: `docs/page_schema.md`
- Command-family naming: `docs/skill_schema.md`
- Skill catalog: generated `docs/skills.md`, sourced from `skills/*/*/SKILL.md`
- Agent instruction block: `rites/templates/grimoire_block.md`
- Grimoire scaffold contracts: `formulae/grimoire/`
- Release process: `docs/release.md` and `docs/governance.md`
- Release history and snapshots: `CHANGELOG.md` (not the live canonical
  architecture; link to canonical docs for current rules)

Then search for drift-prone repetitions:

```bash
rg -n "single source|canonical|source of truth|duplicate|drift|generated|do not edit" .
rg -n "Unreleased|legacy|deprecated|migration|old|stale|TODO|FIXME" docs invocations formulae skills rites README.md arcana.md CHANGELOG.md CONTRIBUTING.md
```

For each repetition, decide:

- **Navigation duplicate**: short summary plus link; keep it.
- **Drift risk**: replace detail with a link to the canonical home.
- **Generated view**: prefer a sync rite when the information is structured.
- **Intentional snapshot**: keep it only when the document explicitly acts as a
  release snapshot or audit record.

### 5. Review naming and boundaries

Judge whether names help users and agents predict where things live:

- Folder names match operational families: `arcana`, `grimoire`, `agent`,
  `library`, `workspace`, `help`, `meta`.
- File names use snake_case for authored documents and Python; skill folders
  use kebab-case.
- Hubs are named after their folders and stay router-shaped.
- `meta/` contains only shared fragments and templates, not user-facing
  operations.
- Arcana-only vocabulary (`invocations`, `formulae`, `rites`) does not leak
  into grimoire content examples except when explaining the boundary.
- Examples stay generic and reusable (`cooking-grimoire`, `hr-grimoire`,
  `Alice/Bob`, `Project Alpha`, `{your-grimoire}`).

Flag names that are mechanically valid but semantically awkward. Mechanical
validators cannot tell whether a name is intuitive.

### 6. Review AI-agent efficiency

For each common task, ask how many files an agent must read before it can act:

- Install Arcana.
- Create a grimoire.
- Add a chapter.
- Ingest a source.
- Validate Arcana.
- Improve Arcana.
- Improve a grimoire.
- Update Arcana from a grimoire.
- Register skills.
- Update an agent instruction block.
- Diagnose a validator failure.

Prefer workflows where the agent reads one hub, one invocation, and only the
specific referenced canonical docs. Watch for:

- Hubs that summarize too much instead of routing.
- Invocations that repeat long policy sections instead of linking.
- Skills that contain logic instead of pointing to an invocation or rite.
- Docs that force agents to compare two sources to learn the current rule.
- Human-facing docs that are good marketing but poor operational entry points.

Record the shortest useful read path for each workflow as:

```text
workflow -> entry file -> invocation/rite -> canonical docs/templates -> validation
```

Flag any path that requires comparing two docs to learn the current rule, or
any path where a generated view is treated as editable truth.

For public command surfaces, the skills/agents and invocations lanes must
produce this matrix:

```text
command -> skill source -> invocation leaf -> rite/judgment owner ->
guard/preconditions -> mutation/log behavior -> validation profile ->
generated docs impact
```

Every public command should have exactly one workflow home. Skills stay thin,
hubs route, rites own deterministic mechanics, and judgment passes are named
as judgment.

### 7. Review scalability and future-proofing

Look for places where the current design will become expensive as Arcana grows:

- Hand-maintained lists that could be generated.
- Rites that should share helper code through `_lib.py`.
- Large scripts whose UI, transport, and domain logic can be separated.
- Validator output that cannot be pasted into an editor or issue.
- Test fixtures that encode only happy paths.
- Docs whose examples narrow Arcana to one domain.
- Release instructions that assume one maintainer's local machine.
- Review processes that depend on a single AI context instead of isolated
  reviewer lanes plus synthesis.
- Managed scaffold contracts repeated across docs, formulas, validators, and
  tests instead of living in one machine-checkable place.
- Skill registration cleanup paths that can delete user-authored or
  prefix-colliding skills.
- Mutating rites without dry-run/plan output, explicit exit codes, or temp-HOME
  tests.
- Installer behavior split between shell, CLI, GUI, docs, and release notes
  without a contract that names the canonical behavior.
- Validator diagnostics that are not structured enough for editors, issue
  reports, or AI repair loops.

Do not add abstraction preemptively. Recommend a new abstraction only when it
removes real duplication, reduces repeated judgment work, or preserves a
single source of truth.

### 8. Apply or defer

Apply fixes directly when they are low-risk and local:

- Clarify a stale instruction.
- Replace duplicate detail with a link.
- Update a hub pointer.
- Tighten scope lists.
- Rename a confusing heading without moving files.

Defer and report when a change affects public command names, file paths,
release behavior, generated outputs, or more than ten files. For deferred
items, state the benefit, blast radius, and suggested first step.

### 9. Report

In the final `/arc-improve` report, include:

- Architecture grade before/after.
- Inventory counts by surface.
- Review lanes run, skipped, or serialized, with reason.
- Source-of-truth issues fixed.
- Redundancy removed or intentionally retained.
- Naming and boundary findings.
- AI-efficiency findings: shortest useful read path for key workflows.
- Changes applied.
- Deferred architecture opportunities, prioritized.

## Non-goals

- Do not turn subjective quality checks into brittle validators after one
  observation. Codify only repeated, stable rules.
- Do not optimize for fewer files if it makes routing less explicit.
- Do not collapse user-facing docs into maintainer docs; audiences matter.
- Do not rewrite working architecture for novelty.

## Related

- Orchestrator: [`../improve_arcana.md`](../improve_arcana.md)
- Documentation quality: [`improve_documentation.md`](improve_documentation.md)
- Rite quality: [`validate_rites.md`](validate_rites.md)
- Script vs AI split: [`../../../docs/script_vs_ai.md`](../../../docs/script_vs_ai.md)
- Skill schema: [`../../../docs/skill_schema.md`](../../../docs/skill_schema.md)
