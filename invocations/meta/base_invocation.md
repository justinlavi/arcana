---
type: reference
title: "Base Invocation"
aliases: ["base-invocation", "investigate-extract-codify-route"]
tags: [arcana/invocations, type/reference, scope/meta]
authority: grimoire
last_verified: 2026-05-13
---

# Base Invocation: Investigate → Extract → Codify → Route

A reusable, opinionated workflow for the most common Grimoire operation: "the user gave me a goal, I need to read sources, distill what's stable, write it as a wiki page, and wire it into the routing tree."

This is **not** a slash command. It's a starting template for new invocations whose work fits the four-phase pattern. If a domain operation needs different phases (e.g. ingestion is handled by `/grm-domain-ingest`, lint by `/grm-domain-lint`), use the relevant dedicated invocation instead. For the structural skeleton of a brand-new invocation file, copy `formulae/invocation.formula.md`.

The magical/practical boundary, page schema, hub convention, and storage layers are documented elsewhere; this file references them rather than restating.

## Read first

Anything you author following this template must conform to:

- **Page schema** — every authored page carries YAML frontmatter (`type`, `title`, `tags`, `authority`, `sources`, `last_verified`). Required-fields matrix in [`docs/page_schema.md`](../../docs/page_schema.md).
- **Magical boundary** — system terminology (invocation, formula, rite, hub) lives in Arcana only; chapter content uses domain-natural names (`templates/`, `scripts/`, `policies/`, `recipes/`). Full rules in [`invocations/grimoire/validate_boundaries.md`](../grimoire/validate_boundaries.md).
- **Hub convention** — every folder F has a hub at `F/<basename(F)>.md`. Depth is open-ended. See [`docs/operating_model.md`](../../docs/operating_model.md).

---

## When to follow this pattern

Use this four-phase template when:

- The user has a goal that requires reading external material and producing a single canonical wiki page.
- No more specific invocation applies (`/grm-domain-ingest` for filing a source, `/grm-domain-file-answer` for promoting a chat answer, `/grm-domain-create-chapter` for scaffolding a new chapter).

## When NOT to follow this pattern

- The user has a single source artifact to absorb — use [`ingest.md`](../grimoire/ingest.md).
- The user wants a chat answer promoted to a page — use [`file_answer.md`](../grimoire/file_answer.md).
- The user wants to scaffold a new chapter or grimoire — use the `create_*` invocations.
- The user is auditing or reorganizing — use [`improve_grimoire.md`](../grimoire/improve_grimoire.md) or [`lint.md`](../grimoire/lint.md).

---

## Defaults (when the user does not specify)

- **Scope** — Decide between *shared* (cross-scope rules: kitchen-wide techniques, company-wide policies) and *scope-specific* (single project, client, team, recipe family). Scope-specific work routes through whatever scope-folder hub the grimoire defines (commonly `chapters/projects/projects.md` in engineering grimoires, `chapters/teams/teams.md` in workplace grimoires, etc.).
- **Outputs** — Produce or update exactly one canonical leaf page. Update affected hubs with wikilinks. Add at most one supporting asset (template OR snippet) only if explicitly needed.
- **Authority** — Default to `authority: grimoire` for synthesized procedures and policies the wiki owns; use `authority: external` (with `sources:` listing artifacts under `sources/`) when distilling external material; use `hybrid` when both apply.
- **Success criteria** — Minimal-read invariant: hubs route depth-first to the answering leaf with no exploratory wording. No scope leakage. No absolute paths inside grimoire content.

---

## User Request (filled from the user message)

- **Goal**:
  <!-- 1–3 sentences: what the user wants accomplished. -->

- **Starting pointers** (files/repos/keywords):
  <!-- Use explicit pointers if provided.
       If missing: list what you will inspect first, and why those entry points are canonical. -->

- **Desired outputs**:
  - [ ] One canonical leaf page (default)
  - [ ] Hub updates (almost always required when content is created/moved)
  - [ ] One supporting asset (template OR snippet)
  - [ ] Source filed under `sources/` (only if synthesizing an external artifact)

- **Scope**:
  - [ ] Shared (cross-scope)
  - [ ] Scope-specific (route via the grimoire's scope-folder hub)

- **Authority for the new page**:
  - [ ] `external` — page summarizes external material; `sources:` required
  - [ ] `grimoire` — wiki owns the synthesis; `sources:` may be empty
  - [ ] `hybrid` — wiki owns synthesis but cites external implementation details

- **Success criteria**:
  <!-- If omitted by user, apply Defaults above. -->

---

## Non-negotiable rules

1. **Derive all claims from sources read.** No guessing.
2. **Map + invariants, not duplication.** Don't copy implementation details from external systems verbatim — link to them or provide query commands.
3. **Deterministic routing only.** Explicit hub pointers and wikilinks; no "search for X" / "look around Y" wording.
4. **Relative repo paths only.** No absolute paths inside grimoire content.
5. **Prevent scope leakage.** Shared content stays generic; scope-specific values route through their scope hub.
6. **Minimize reads.** Hubs route depth-first to the answering leaf with no detours; the structure is as deep as the topic warrants.
7. **Canonical source selection.** When multiple copies of the same authoritative material exist, prefer the system-of-record (top-level repo, original publication) over embedded or vendored copies, unless the user explicitly targets a derivative.
8. **Never store implementation values; provide query instructions instead.** Forbidden: hard-coded version numbers, configuration values, or other facts that change at the source's pace. Required: provide a `grep`/`find`/`git`-style command the reader can run to extract the current value. Templates under `chapters/<chapter>/templates/` are exempt — they are prescriptive standards, not snapshots.
9. **Magical boundary** — domain content uses practical folder names (`templates/`, `scripts/`, `snippets/`, `policies/`, `recipes/`, `playbooks/`); never `invocations/`, `formulae/`, or `rites/`. Those exist only in Arcana.
10. **Frontmatter required.** Every authored page declares its `type`, `title`, `tags`, `authority`, `sources` (when external/hybrid), and `last_verified`. See [`docs/page_schema.md`](../../docs/page_schema.md).
11. **If blocked by missing pointers**, make a best-effort guess at the canonical entry point and proceed. Ask the user one targeted question only if you cannot continue responsibly.

---

## Workflow

### Phase 1 — Investigate (classify scope and pick canonical sources)

- Classify the goal: shared or scope-specific?
- Pick the canonical source-of-truth before reading anything in depth. Top-level system-defining repos beat embedded copies; canonical published works beat secondary summaries.
- Output a concrete file/URL list before deep reading.

### Phase 2 — Extract (only what is stable and reusable)

Pull only:

- Terms / definitions
- Invariants and contracts
- Recurring patterns
- Interfaces and entry points
- Failure modes / known gotchas

Discard one-off implementation details that belong to the source, not the synthesis.

### Phase 3 — Codify (one canonical leaf page)

Scaffold from `formulae/page.formula.md`. The required structure is:

**Frontmatter** (always required):
```yaml
---
type: concept | entity | source | playbook | reference
title: "..."
aliases: [...]
tags: [chapter/<chapter>, type/<type>, ...]
sources: ["sources/<slug>.md", ...]   # required when authority is external/hybrid
authority: external | grimoire | hybrid
last_verified: YYYY-MM-DD
---
```

**Body sections** (in this order; section names taken from `formulae/page.formula.md`):

1. `# [Title]` — page heading.
2. `## Purpose` — one or two sentences: what this page covers.
3. `## When to Use` — scenarios that route here.
4. `## Primary Sources` — required when `authority` is `external` or `hybrid`. List artifacts under `sources/` and external systems the page synthesizes. Omit entirely for `authority: grimoire` pages that are themselves the source of truth.
5. **Author-named content sections** — page formula intentionally does not enforce a fixed list here. Pick what the page actually needs. Common choices by `type`:
   - `concept` / `entity`: `## Invariants`, `## Standard Patterns`, `## Architecture`, `## Comparison Table`
   - `playbook`: `## Workflow`, `## Inputs`, `## Outputs`, `## Validation`
   - `reference`: `## Vocabulary`, `## Schema`, `## Field Reference`
6. `## Gotchas` — optional. Common mistakes, edge cases.
7. `## Related` — wikilinks to sibling/parent pages.

### Phase 4 — Route (wire into the hub tree)

- Update the directly-containing chapter hub with a wikilink pointer to the new leaf.
- Update the root hub only when introducing a top-level chapter.
- Use Obsidian wikilinks (`[[page]]`) for in-grimoire pointers; the alias index resolves them. Cross-grimoire references stay as path placeholders (`GRIMOIRE_ARCANA/...`).
- If the new page introduces a new sub-chapter, scaffold its hub at `<new-folder>/<new-folder>.md` (the hub convention recurses).

### Phase 5 — Validate before finishing

Run from the grimoire root:

```bash
python3 GRIMOIRE_ARCANA/rites/validate_frontmatter.py --grimoire .
python3 GRIMOIRE_ARCANA/rites/validate_links.py --grimoire .
python3 GRIMOIRE_ARCANA/rites/validate_provenance.py --grimoire .
```

Confirm:

- Hubs route depth-first to the new leaf without backtracking.
- No project / scope-specific content was written into shared chapters.
- All added pointers and wikilinks resolve.
- No absolute paths.
- No `invocations/`, `formulae/`, or `rites/` folders created in the domain grimoire.

### Phase 6 — Append a log entry

```bash
python3 GRIMOIRE_ARCANA/rites/append_log.py \
  --grimoire . \
  --op create \
  --title "<short description of what was authored>" \
  --skill /<namespace>-<skill> \
  --field pages=<comma-separated paths>
```

---

## Output checklist

- [ ] Files created/edited (with relative paths)
- [ ] Sources read (exact file list)
- [ ] Hubs updated (paths and wikilinks added)
- [ ] Page frontmatter complete and validator-clean
- [ ] Provenance closed: external/hybrid pages cite real `sources/` artifacts
- [ ] Log entry appended
- [ ] Open TODOs (if any) with source pointers
