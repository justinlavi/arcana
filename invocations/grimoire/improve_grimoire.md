# Invocation: Improve Domain Grimoire

## Purpose

Audit and improve the *active* domain grimoire for token-efficient, deterministic routing: `INDEX.md` → chapter `INDEX.md` → 1–2 canonical leaf docs. Combines mechanical validators with judgment-based passes. Safe to rerun.

This is the domain-grimoire counterpart to `/grm-arcana-improve` (which targets Arcana itself). The two are unrelated — never fall back from one to the other.

## Invocation

From a registered domain grimoire's root:

```
/grm-domain-improve
```

## Preconditions

1. The current working directory must match a `local_path` in `~/grimoire/catalog.json`.
2. If it does not match, list available grimoires from the catalog, instruct the user to `cd` into one, and **stop**.
3. Arcana is not a domain grimoire — refuse if `cwd` is the Arcana root.

## When to cast

- Routing takes >3 hops to reach common knowledge
- Orphan docs or broken links have accumulated
- Routers feel bloated or duplicated
- Quarterly hygiene pass, or after adding 5+ new docs

## Workflow

### Phase 1: Mechanical validation

Invoke and collect output from:

- `/grm-domain-validate-structure` — directory layout, required `INDEX.md` files, naming
- `/grm-arcana-validate-links` — internal markdown links resolve
- `/grm-arcana-validate-boundaries` — magical/practical boundary compliance

Stop and report if any validator returns hard errors that would invalidate later phases (e.g. missing root `INDEX.md`).

### Phase 2: Inventory

- Enumerate routers (every `INDEX.md`) and leaf docs.
- Classify leaves as wired (reachable from a router) or orphaned.
- Flag absolute paths, `search`/`look around` instructions, and prose >150 words inside routers.
- Identify duplicate or near-duplicate leaf content.

### Phase 3: Semantic analysis

Run `/grm-domain-analyze-semantics` and incorporate its output:

- Naming clarity scores per chapter
- Terminology drift (`config` vs `configuration`, etc.)
- Discoverability gaps (queries that take >3 hops)
- Quick wins (high impact, <30 min effort)

### Phase 4: Judgment passes

Apply the following heuristics to the inventory and semantic output. Each is human-judgment work — explain the reason for every change in the final report.

**Router normalization**
- Routers are pointer lists. Move prose into leaf docs.
- Each router entry: one line, one destination, query-shaped phrasing (`CMake config → cmake_overrides.md`).
- Root `INDEX.md` points only to chapter `INDEX.md` files; chapter `INDEX.md` points to 1–2 leaves per topic.

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
- Do not auto-rewrite stale technical content — surface it as a TODO.

### Phase 5: Apply fixes

Edit files directly:

- Rewrite bloated routers
- Fix broken links
- Merge duplicates into the canonical leaf
- Delete or wire orphans
- Apply terminology standardizations from Phase 3
- Apply rename quick wins (update incoming links in the same pass)

Defer anything that touches >10 files or rewrites stable chapter names — surface as TODOs instead.

### Phase 6: Re-validate

Re-run the Phase 1 validators. All must pass. Re-run `/grm-domain-analyze-semantics` if Phase 5 made significant renames; confirm scores improved.

## Non-negotiable rules

1. Do not invent new conventions — restructure within what exists.
2. Deterministic routing only — explicit pointers, no `search`/`look around`.
3. Grimoires are maps — do not duplicate implementation detail from source.
4. Relative repo paths only.
5. Refactors preserve technical meaning.
6. Stay in the active grimoire's directory tree.

## Scope

Operates on the active grimoire only:

```
grimoire-{domain}/
├── INDEX.md
├── README.md
└── chapters/
    ├── **/INDEX.md
    ├── **/*.md
    ├── **/templates/
    ├── **/scripts/
    └── **/snippets/
```

Out of scope: Arcana, other registered grimoires, source repos referenced by the grimoire.

## Report

Surface in chat (do not write report files):

- Quality grade before/after (A–F)
- Validator pass/fail summary (Phase 1, Phase 6)
- Inventory counts (routers, leaves, orphans, duplicates)
- Fixes applied, grouped by phase
- Semantic improvements (renames, terminology standardizations)
- Boundary violations fixed
- Freshness TODOs requiring human judgment
- Remaining manual work, prioritized

## Related

- Mechanical: `/grm-domain-validate-structure`, `/grm-arcana-validate-links`, `/grm-arcana-validate-boundaries`
- Semantic: `/grm-domain-analyze-semantics`
- Authoring: `/grm-domain-create-chapter`
- Arcana counterpart (maintainer only): `/grm-arcana-improve`
