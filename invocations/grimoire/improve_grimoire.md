---
type: playbook
title: "Improve Grimoire"
aliases: ["improve-grimoire", "upgrade-grimoire", "domain-improve"]
tags: [arcana/invocations, type/playbook, scope/domain]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Improve Grimoire

## Purpose

Upgrade, audit, and improve the *active* grimoire against the current Arcana version. This includes managed scaffold drift, schema/structure drift, and token-efficient deterministic routing through the hub tree (root hub -> chapter hub -> optional sub-chapter hubs -> 1-2 canonical leaf docs; depth is open-ended). Combines mechanical validators with judgment-based passes. Safe to rerun.

This is the domain-grimoire counterpart to `/arc-improve` (which targets Arcana itself). The two are unrelated - never fall back from one to the other.

## Invocation

From a registered grimoire's root:

```
/arc-grimoire-improve
```

## Preconditions

1. The current working directory must match a `local_path` in `~/grimoires/library.json`.
2. If it does not match, list available grimoires from the library, instruct the user to `cd` into one, and **stop**.
3. Arcana is not a grimoire - refuse if `cwd` is the Arcana root.

## When to cast

- Routing takes more hops than the topic warrants (deeply-nested chains for genuinely simple knowledge)
- Arcana was updated and this grimoire may be behind the current scaffold/schema
- A grimoire was created from an older Arcana version
- Hub trees are unbalanced - a few hubs hold most of the leaves while others are nearly empty
- Orphan docs or broken links have accumulated
- Routers feel bloated or duplicated
- Quarterly hygiene pass, or after adding 5+ new docs

## Workflow

### Phase 0: Arcana and active-grimoire alignment

Before editing the grimoire:

- Confirm the user has pulled the latest Arcana they intend to use. Do not run network commands unless the user asks.
- Confirm Arcana skills have been registered after the update (`/arc-skills-register`) or tell the user to run it before relying on newly added skills.
- If the user asks to upgrade all grimoires, list registered grimoires from `~/grimoires/library.json`, recommend doing one grimoire at a time, and start with the active grimoire unless the user chooses another.
- Confirm the active grimoire root is not Arcana.

### Phase 1: Mechanical validation and scaffold drift

Invoke and collect output from:

- `/arc-grimoire-validate-structure` - directory layout, required hub files, managed scaffold drift
- `/arc-validate-format` (`python3 ARCANA_HOME/rites/validate_format.py --grimoire .`) - Markdown tables, fences, and tree examples
- `/arc-validate-links` - internal markdown links resolve
- `/arc-grimoire-validate-boundaries` - magical/practical boundary compliance

Stop and report if any validator returns hard errors that would invalidate later phases (e.g. missing root hub).

If `/arc-grimoire-validate-structure` reports missing or stale managed scaffold files, copy the current files from `ARCANA_HOME/formulae/grimoire/` before continuing:

| Grimoire file | Source of truth |
|---|---|
| `.editorconfig` | `ARCANA_HOME/formulae/grimoire/.editorconfig` |
| `.gitattributes` | `ARCANA_HOME/formulae/grimoire/.gitattributes` |
| `.obsidian/app.json` | `ARCANA_HOME/formulae/grimoire/.obsidian/app.json` |
| `inbox/README.md` | `ARCANA_HOME/formulae/grimoire/inbox/README.md` |
| `sources/README.md` | `ARCANA_HOME/formulae/grimoire/sources/README.md` |

Do not mechanically replace grimoire-authored files such as the root README, root hub, `grimoire.json`, `log.md`, chapter hubs, or content pages. Those require contextual review.

### Phase 2: Inventory

- Enumerate routers (every hub) and leaf docs.
- Classify leaves as wired (reachable from a router) or orphaned.
- Flag absolute paths, `search`/`look around` instructions, and prose >150 words inside routers.
- Identify duplicate or near-duplicate leaf content.

### Phase 3: Semantic analysis

Run `/arc-grimoire-analyze-semantics` and incorporate its output:

- Naming clarity scores per chapter
- Terminology drift (`config` vs `configuration`, etc.)
- Discoverability gaps (queries whose hop count is disproportionate to the topic's depth)
- Quick wins (high impact, <30 min effort)

### Phase 4: Judgment passes

Apply the following heuristics to the inventory and semantic output. Each is human-judgment work - explain the reason for every change in the final report.

**Router normalization**
- Routers are pointer lists. Move prose into leaf docs.
- Each router entry: one line, one destination, query-shaped phrasing (`CMake config -> cmake_overrides.md`).
- Root hub points only to chapter hub files; chapter hub points to 1-2 leaves per topic.

**Canonicalization**
- For duplicate topics, pick one canonical leaf and replace the others with redirects or links.
- Split a leaf only when splitting reduces total reads for a typical query.
- Wire orphans into the nearest sensible router or delete them.

**Boundary hygiene**
- No magical folder names (`invocations/`, `formulae/`, `rites/`) inside the grimoire.
- No platform/team buzzwords leaking into generic content; no proprietary names in examples.
- Chapter content uses practical domain terminology, not Grimoire system jargon.

**Freshness**
- Flag leaves not touched in >90 days for revalidation.
- Flag references to files or SHAs that no longer exist.
- Do not auto-rewrite stale technical content - surface it as a TODO.

**Arcana upgrade review**
- Compare current grimoire practices against `ARCANA_HOME/docs/operating_model.md`, `ARCANA_HOME/docs/page_schema.md`, and `ARCANA_HOME/rites/templates/grimoire_block.md`.
- Update stale command names, manifest field names, and operational vocabulary to current Arcana.
- Preserve historical log entries unless the entry is actively misleading for current operations; add a new log entry for the migration instead of rewriting history.

### Phase 5: Apply fixes

Edit files directly:

- Rewrite bloated routers
- Fix broken links
- Merge duplicates into the canonical leaf
- Delete or wire orphans
- Apply terminology standardizations from Phase 3
- Apply rename quick wins (update incoming links in the same pass)

Defer anything that touches >10 files or rewrites stable chapter names - surface as TODOs instead.

### Phase 6: Re-validate

Re-run the Phase 1 validators. All must pass. Re-run `/arc-grimoire-analyze-semantics` if Phase 5 made significant renames; confirm scores improved.

## Non-negotiable rules

1. Do not invent new conventions - restructure within what exists.
2. Deterministic routing only - explicit pointers, no `search`/`look around`.
3. Grimoires are maps - do not duplicate implementation detail from source.
4. Relative repo paths only.
5. Refactors preserve technical meaning.
6. Stay in the active grimoire's directory tree.

## Scope

Operates on the active grimoire only:

```
{grimoire-name}/
├── {grimoire-name}.md       # Root hub (folder-name convention)
├── README.md
├── grimoire.json
├── log.md
├── sources/                 # Immutable sources
└── chapters/
    ├── <chapter>/<chapter>.md   # Chapter hub (folder-name convention)
    ├── <chapter>/*.md           # Leaf pages
    ├── **/templates/
    ├── **/scripts/
    └── **/snippets/
```

Out of scope: Arcana, other registered grimoires, source repos referenced by the grimoire.

## Report

Surface in chat (do not write report files):

- Quality grade before/after (A-F)
- Validator pass/fail summary (Phase 1, Phase 6)
- Inventory counts (routers, leaves, orphans, duplicates)
- Fixes applied, grouped by phase
- Semantic improvements (renames, terminology standardizations)
- Boundary violations fixed
- Arcana upgrade fixes (managed scaffold files copied, schema fields updated, command names updated)
- Freshness TODOs requiring human judgment
- Remaining manual work, prioritized

## Related

- Mechanical: `/arc-grimoire-validate-structure`, `/arc-validate-links`, `/arc-grimoire-validate-boundaries`
- Semantic: `/arc-grimoire-analyze-semantics`
- Authoring: `/arc-grimoire-create-chapter`
- Arcana counterpart (maintainer only): `/arc-improve`
