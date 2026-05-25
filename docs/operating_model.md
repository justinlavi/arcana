---
type: reference
title: "Grimoire Operating Model"
aliases: ["operating-model", "routing-model"]
tags: [type/reference, arcana/docs]
authority: grimoire
last_verified: 2026-05-12
---

# Grimoire Operating Model

## Universal Principles

The following principles apply across every domain a grimoire might cover.

## Storage Layers

A grimoire's content is organized into layers that work together:

| Layer | Directory | Owner | Purpose |
|---|---|---|---|
| Sources | `sources/` | LLM reads, never modifies | Immutable artifacts: articles, transcripts, papers, screenshots. Citation-stable. |
| Inbox | `inbox/` | LLM and user both write | Transient drop zone for mixed content awaiting classification. Cleared on `/grm-ingest`. |
| Wiki | `chapters/`, root hub | LLM authors and maintains | Synthesized knowledge with frontmatter (`type`, `authority`, `sources`, `last_verified`) |
| Schema | `grimoire.json` + injected agent block | User co-evolves | Tells the agent how to operate this grimoire |

Plus the per-grimoire `log.md` (append-only activity record).

`sources/` and `inbox/` are distinct on purpose: `sources/` is permanent and citation-worthy (pages with `authority: external` cite it), while `inbox/` is transient (drop a zip extract, AI-generated draft, or coworker hand-off here and the next ingest sweep classifies each item — sources go to `sources/`, authored content goes to `chapters/`, and ambiguous items stay in `inbox/` for human review). Pages must never cite `inbox/` paths in `sources:` because inbox content disappears once processed.

The wiki layer's *routing surface* is the hub tree, defined next.

## Hub Convention (Self-Similar, Open-Ended Depth)

Every folder F that acts as a router has a hub file at `F/<basename(F)>.md`. The convention is uniform regardless of depth:

- Grimoire root hub: `<grimoire>/<grimoire>.md`
- Any chapter or sub-chapter hub: `<folder>/<folder>.md`

A hub may route to **sub-hubs**, to **leaf documents**, or to both. There is no fixed maximum depth — a chapter that needs sub-chapters gets them; a chapter that needs only direct leaves keeps them. Each hub is idempotent: the same shape and rules apply at every level.

Hub-level tags (`hub/root`, `hub/chapter`, `hub/sub`) distinguish levels for the Obsidian graph view but don't constrain the routing model. `hub/chapter` applies to a top-level chapter (immediately under `chapters/`); `hub/sub` applies to any deeper hub regardless of how many levels down.

Folder-named hubs make Obsidian's graph view legible (every node has a unique, meaningful label) and make full-path wikilinks intuitive, e.g. `[[chapters/build_system/build_system|build system]]`.

## What Grimoire Is

- A deterministic knowledge router for any knowledge-based work (code, documentation, policies, templates, processes, etc.).
- A persistent, compounding artifact the LLM keeps current as new sources arrive.
- **Minimal-read invariant:** every hop narrows the search; the path stops at the leaf that answers the question. Shallow when topics are flat (root hub -> leaf), deeper when topics warrant nesting (root -> chapter -> sub-chapter -> ... -> leaf). The invariant is "as few hops as the structure requires," not a fixed count.
- Hubs are maps; leaf docs store invariants, stable patterns, and source pointers.
- Keep canonical rules in one leaf and link/wikilink to it from related docs.

## How To Route

1) Start at the grimoire root hub: `<grimoire>/<grimoire>.md`.
2) Classify the request: which chapter does it fall into? Is it shared or scoped to a particular project / use case?
3) Follow one explicit pointer. The target may be a leaf (you're done) or another hub (recurse).
4) Repeat step 3 at each hub. Read sub-hubs depth-first; do not branch unless the current hub explicitly directs you to a related sibling.
5) When you reach a leaf, read it. Read one related leaf only when the hub or the leaf's `Related` section calls for it.
6) For project / scope-specific overrides, the grimoire root or a chapter hub typically routes through a `projects/projects.md` (or `clients/`, `teams/`) sub-hub. Follow it and then the specific scope hub.
7) When adding knowledge, update the relevant hub with an explicit pointer (full-path wikilinks preferred); no exploratory wording. If the new content needs its own grouping, add a sub-folder with its own hub — the convention recurses.

## Scope Rules
- **Shared chapters** store rules that apply across all scopes the grimoire covers (e.g. company-wide policies in an HR grimoire, kitchen-wide techniques in a cooking grimoire).
- **Scope-specific chapters** (often under a `projects/`, `clients/`, `teams/`, or similar folder) store overrides and values that only apply to one scope.
- Never place scope-specific values in shared chapters.
- Never duplicate shared invariants in scope-specific docs — link to the shared canonical page instead.

## Templates And Snippets
- Chapter-local assets live with their chapter:
 - `chapters/<chapter>/templates/`
 - `chapters/<chapter>/snippets/`
- Use `chapters/shared/templates/` only for cross-chapter reusable assets.
- Routers should point to concrete files (not "search" instructions).
- **Templates are prescriptive standards**: they define how content should be structured across the grimoire (not drift sources).

## Content Types And Drift Management

### Core Principle
**Grimoire supports multiple authority modes.** It can route to external sources, act as canonical source of truth for domain-owned knowledge, or combine both in hybrid pages.

Implementation details owned by active code/config systems should remain externally authoritative.
Operational procedures, policy, tribal knowledge normalization, and domain standards can be authoritative in Grimoire when explicitly declared.

### Knowledge Authority Model

Every knowledge page must declare one authority model:

**External**
- Use when truth is owned outside Grimoire (repos, services, platforms).
- Page role: deterministic router + contextual guidance.
- Requires external source pointers and query-first extraction patterns.

**Grimoire**
- Use when the page itself is intended to be canonical truth for the domain.
- Page role: authoritative record in Grimoire.
- Requires explicit scope and change control.

**Hybrid**
- Use when Grimoire owns canonical synthesis while external systems still own implementation details.
- Page role: policy/process authority + external source map.
- Requires both change control and external pointers.

**How to choose**: If changing source code/config in another repo changes truth -> External. If editing this page is how truth changes -> Grimoire. If both -> Hybrid.

### Content Type Taxonomy

**Type 1: Source Pointers (Zero Drift Risk)**
- Pure file/line references to authoritative sources
- Example: "CMake options live in `CP_Framework/CMakeLists.txt` lines 10-25"
- Validation: File exists, lines exist
- No duplication of implementation details

**Type 2: High-Level Invariants (Low Drift Risk)**
- Behavioral contracts and architectural patterns
- Example: "`configure_package()` only includes if `CMakeLists.txt` exists"
- Validation: Behavioral test (does it still work this way?)
- Rarely changes; represents stable architecture

**Type 3: Policy Documents (Low Drift Risk)**
- Domain standards and conventions
- Example: "Platform-specific code must live behind `ops` abstractions"
- Validation: Domain agreement and code review enforcement
- Changes require deliberate policy decisions

**Type 4: Observed Patterns (Medium Drift Risk)**
- Snapshots of current state with source references
- Example: "Observed brace style: Allman (as of SHA xyz)"
- Validation: SHA-stamped, must be revalidated periodically
- Must be labeled "as of [date] - VERIFY BEFORE USE"
- Include query commands to extract current values

**Type 5: Prescriptive Templates (Controlled Drift)**
- Code/CMake templates in `chapters/*/formulae/`
- These ARE the standard (not a snapshot of it)
- Purpose: Ensure consistency across projects
- Updates to templates propagate standard changes across projects
- Exception to "no source of truth" rule by design

**Type 6: Canonical Operational Knowledge (Grimoire Authority, Controlled Drift)**
- Domain-owned procedures, handover playbooks, and policy-like guidance whose source of truth is the Grimoire page
- Example: VM handover runbook that exists only in Grimoire
- Validation: Review cadence + change authority + explicit scope boundaries
- Must include change control and provenance metadata

**Type 7: FORBIDDEN (High Drift Risk)**
- Stored implementation values without query instructions
- Example: Storing `SYS_LOG_FORMAT = INLINE` without extraction command
- This type should never exist in Grimoire
- Always convert to Type 4 (Observed Patterns with queries)

### Query-First Pattern
When documenting project-specific values or configuration in **External** or **Hybrid** pages:
1. Provide bash/grep commands to extract current values from source
2. Include "Primary Sources" with exact file paths
3. Show example values labeled "as of [date] - VERIFY BEFORE USE"
4. Use query instructions that can be run to get current values

### Canonical-in-Grimoire Pattern
When documenting **Grimoire** authority pages:
1. Add explicit source-of-truth statement ("this page is canonical for X")
2. Define in-scope vs out-of-scope boundaries
3. Define change control (triggers, cadence, approval path)
4. Link external inputs as evidence only (not required as primary authority)


---
