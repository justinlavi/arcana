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

### 2. Build a source-of-truth map

List the facts Arcana repeats most often and name their canonical homes:

- Storage layers and routing: `docs/operating_model.md`
- Frontmatter schema: `docs/page_schema.md`
- Command-family naming: `docs/skill_schema.md`
- Skill catalog: generated `docs/skills.md`, sourced from `skills/*/*/SKILL.md`
- Agent instruction block: `rites/templates/grimoire_block.md`
- Grimoire scaffold contracts: `formulae/grimoire/`
- Release process: `docs/release.md` and `docs/governance.md`
- Current release architecture: `CHANGELOG.md`

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

### 3. Review naming and boundaries

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

### 4. Review AI-agent efficiency

For each common task, ask how many files an agent must read before it can act:

- Install Arcana.
- Create a grimoire.
- Add a chapter.
- Ingest a source.
- Validate Arcana.
- Improve Arcana.
- Register skills.
- Update an agent instruction block.

Prefer workflows where the agent reads one hub, one invocation, and only the
specific referenced canonical docs. Watch for:

- Hubs that summarize too much instead of routing.
- Invocations that repeat long policy sections instead of linking.
- Skills that contain logic instead of pointing to an invocation or rite.
- Docs that force agents to compare two sources to learn the current rule.
- Human-facing docs that are good marketing but poor operational entry points.

### 5. Review scalability and future-proofing

Look for places where the current design will become expensive as Arcana grows:

- Hand-maintained lists that could be generated.
- Rites that should share helper code through `_lib.py`.
- Large scripts whose UI, transport, and domain logic can be separated.
- Validator output that cannot be pasted into an editor or issue.
- Test fixtures that encode only happy paths.
- Docs whose examples narrow Arcana to one domain.
- Release instructions that assume one maintainer's local machine.

Do not add abstraction preemptively. Recommend a new abstraction only when it
removes real duplication, reduces repeated judgment work, or preserves a
single source of truth.

### 6. Apply or defer

Apply fixes directly when they are low-risk and local:

- Clarify a stale instruction.
- Replace duplicate detail with a link.
- Update a hub pointer.
- Tighten scope lists.
- Rename a confusing heading without moving files.

Defer and report when a change affects public command names, file paths,
release behavior, generated outputs, or more than ten files. For deferred
items, state the benefit, blast radius, and suggested first step.

### 7. Report

In the final `/arc-improve` report, include:

- Architecture grade before/after.
- Inventory counts by surface.
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
