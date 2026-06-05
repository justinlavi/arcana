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
| Sources | `sources/` | LLM files during import, then reads | Immutable artifacts and source wrappers: articles, transcripts, papers, screenshots, datasets. Citation-stable. |
| Inbox | `inbox/` | LLM and user both write | Transient drop zone for mixed content awaiting classification. Cleared on `/grm-import`. |
| Wiki | `chapters/`, root hub | LLM authors and maintains | Synthesized knowledge with frontmatter (`type`, `authority`, `sources`, `last_verified`) |
| Schema | `grimoire.json` + injected agent block | User co-evolves | Tells the agent how to operate this grimoire |

Plus the per-grimoire `log.md` (append-only activity record).

`sources/` and `inbox/` are distinct on purpose: `sources/` is permanent and citation-worthy (pages with `authority: external` cite it), while `inbox/` is transient (drop a zip extract, AI-generated draft, or coworker hand-off here and the next import sweep classifies each item - sources go to `sources/`, authored content goes to `chapters/`, and ambiguous items stay in `inbox/` for human review). Pages must never cite `inbox/` paths in `sources:` because inbox content disappears once processed.

### Source wrappers

`sources/` can hold raw artifacts, source wrapper Markdown, or both. A raw
artifact is copied as received and can be any format. A source wrapper is a
Markdown capture record created from `formulae/source.formula.md`; it declares
`type: source`, `authority: external`, and `sources:` pointing to the original
URL, capture origin, or a sibling raw artifact under `sources/<slug>/`.

Use a wrapper when a text source needs a cleaned body, when a binary source
needs readable capture metadata, or when an external URL needs a local,
citation-stable record. Use both when the source is bulky or binary:
`sources/<slug>.md` is the wrapper, and `sources/<slug>/<file>` is the raw
artifact.

Authored synthesis belongs in `chapters/`, not `sources/`. Chapter pages cite
source wrappers or raw artifacts in frontmatter `sources:`; the provenance
validator follows those pointers. Source wrappers do not maintain backlinks to
derived wiki pages.

The wiki layer's *routing surface* is the hub tree, defined next.

## Hub Convention (Self-Similar, Open-Ended Depth)

Every folder F that acts as a router has a hub file at `F/<basename(F)>.md`. The convention is uniform regardless of depth:

- Grimoire root hub: `<grimoire>/<grimoire>.md`
- Any chapter or sub-chapter hub: `<folder>/<folder>.md`

A hub may route to **sub-hubs**, to **leaf documents**, or to both. There is no fixed maximum depth — a chapter that needs sub-chapters gets them; a chapter that needs only direct leaves keeps them. Each hub is idempotent: the same shape and rules apply at every level.

Hub-level tags (`hub/root`, `hub/chapter`, `hub/sub`) distinguish levels for the Obsidian graph view but don't constrain the routing model. `hub/chapter` applies to a top-level chapter (immediately under `chapters/`); `hub/sub` applies to any deeper hub regardless of how many levels down.

Folder-named hubs make Obsidian's graph view legible (every node has a unique, meaningful label) and make full-path wikilinks intuitive, e.g. `[[chapters/build_system/build_system|build system]]`.

Under `chapters/`, this naming is an if-and-only-if and is mechanically enforced: a page is a hub exactly when its filename stem equals its folder name. `validate_grimoire_structure` requires every folder-named page — the root hub and each `<folder>/<folder>.md` — to declare `type: hub`, and refuses any `type: hub` page that is not folder-named. An agent can therefore tell a hub from a leaf by path alone, without reading the page. (Demonstrative asset folders such as `templates/` are exempt.)

Internal page link style is layer-aware:

- Public documentation (`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/**`, and README index files) uses standard Markdown links so repository browsing on Git hosts remains clickable.
- Vault and AI-routing surfaces (root hubs, chapter pages, invocation files, skill sources, and formula templates) use full-path wikilinks for internal Markdown-page pointers.
- External URLs, same-page anchors, and local non-Markdown artifacts use standard Markdown links in every layer.

## Naming And Depth Conventions

Two structural choices are deliberate and mechanically enforced, not incidental:

- **snake_case names.** Page and folder names are lowercase `snake_case`, enforced by `validate_naming` (with conventional uppercase exceptions such as `README.md`, `CHANGELOG.md`, and `VERSION`). snake_case is greppable as whole-word tokens, stable under full-path wikilinks, and unambiguous for lexical lookup; `kebab-case` is reserved for skill slugs. Do not rename pages to other casings.
- **Open-ended depth, no global cap.** The hub tree is as deep as the topic warrants - bounded by topic structure, never by a fixed hop limit. A flat topic stays shallow (root -> leaf); a layered one nests as far as it needs. Per the minimal-read invariant, each hop must narrow the search, so collapse a hub only when it adds a hop without narrowing it (a single-leaf pass-through) - never to hit a uniform depth target.

## What Grimoire Is

- A deterministic knowledge router for any knowledge-based work (code, documentation, policies, templates, processes, etc.).
- A persistent, compounding artifact the LLM keeps current as new sources arrive.
- **Minimal-read invariant:** every hop narrows the search; the path stops at the leaf that answers the question. Shallow when topics are flat (root hub -> leaf), deeper when topics warrant nesting (root -> chapter -> sub-chapter -> ... -> leaf). The invariant is "as few hops as the structure requires," not a fixed count.
- Hubs are maps; leaf docs store invariants, stable patterns, and source pointers.
- Keep canonical rules in one leaf and wikilink to it from related routing surfaces.
- **Primary and secondary axes:** the hub tree is the primary navigation axis; an optional owner-defined topical facet (`domain/<...>`; see [page schema](page_schema.md#tag-conventions)) is a secondary lexical axis for cross-cutting subjects.

## How To Route

1) Start at the grimoire root hub: `<grimoire>/<grimoire>.md`.
2) Classify the request: which chapter does it fall into? Is it shared or scoped to a particular project / use case?
3) Follow one explicit pointer. The target may be a leaf (you're done) or another hub (recurse).
4) Repeat step 3 at each hub. Read sub-hubs depth-first; do not branch unless the current hub explicitly directs you to a related sibling.
5) When you reach a leaf, read it. Read one related leaf only when the hub or the leaf's `Related` section calls for it.
6) For project / scope-specific overrides, the grimoire root or a chapter hub typically routes through a `projects/projects.md` (or `clients/`, `teams/`) sub-hub. Follow it and then the specific scope hub.
7) When adding knowledge, update the relevant hub with an explicit full-path wikilink pointer; no exploratory wording. If the new content needs its own grouping, add a sub-folder with its own hub - the convention recurses.

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

A grimoire supports multiple authority modes: a page can route to external
sources, be the canonical source of truth for domain-owned knowledge, or combine
both. Implementation details owned by active code or config systems stay
externally authoritative; operational procedures, policy, and normalized domain
knowledge can be grimoire-authoritative when explicitly declared.

Every page declares one authority model (`external`, `grimoire`, or `hybrid`).
The full definitions, required-fields matrix, and rules of thumb live in
[page schema](page_schema.md#authority-models) - the canonical home for the
authority model.

To keep authored knowledge from drifting out of sync with the systems it
describes:

- **External and hybrid pages are query-first.** Cite the authoritative source by
  path or URL and give a command to extract current values rather than copying
  them inline. A snapshot of a current value carries an
  "as of <date> - verify before use" label.
- **Grimoire-authoritative pages carry change control.** Add an explicit
  source-of-truth statement, in-scope vs out-of-scope boundaries, and a review
  cadence; cite external inputs as evidence, not as the primary authority.
- **Never store an implementation value with no way to re-derive it.** A stored
  value with no query or source pointer is guaranteed to drift; convert it to a
  source pointer or a labeled, query-backed snapshot.

---
