---
type: playbook
title: "Ingest Source"
aliases: ["ingest", "domain-ingest"]
tags: [arcana/invocations, type/playbook, scope/domain]
authority: grimoire
last_verified: 2026-05-13
---

# Invocation: Ingest

## Purpose

Bring external content into a domain grimoire. The skill is polymorphic — it accepts a single source artifact, a folder, or no argument (sweep `inbox/`). It classifies each item and routes it to the right destination:

- **External source artifact** → `sources/<slug>` (immutable, citation-worthy)
- **Wiki content / draft** → `chapters/<chapter>/<page>.md` (curated, frontmattered)
- **Junk / unclear** → stays where it is, flagged for human review

`sources/` and `chapters/` are the destinations. `inbox/` is the (optional) staging area.

For a one-off chat answer with no source artifact, use `/grm-domain-file-answer` instead.

## Invocation

```
/grm-domain-ingest                # no arg: sweep inbox/ if it exists
/grm-domain-ingest <file>         # single source artifact
/grm-domain-ingest <folder>       # walk that folder, classify each file
```

If the user provides only a description, ask for a source location (or instruct them to drop into `inbox/`) before continuing.

## Preconditions

1. Working directory must be a registered domain grimoire (its key in `~/grimoires/library.json`). Refuse for Arcana itself.
2. `sources/` and `log.md` must exist at the grimoire root. If missing, instruct the user to re-scaffold or run `/grm-domain-validate-structure`.
3. `inbox/` is optional. If the user invokes with no argument and no `inbox/` exists, ask whether to create one or to point at a specific path.

## Modes

### Mode A — single source artifact (`<file>` provided)

The classic provenance-careful flow. The argument is a single immutable artifact (article, transcript, paper, screenshot, PDF).

1. Copy (don't move) it to `sources/<slug>.<ext>`. Pick a short snake_case-or-kebab-case slug.
2. For binary sources, also create a sibling `sources/<slug>.md` summary based on `GRIMOIRE_ARCANA/formulae/source.formula.md` referencing the binary.
3. For text sources, place the cleaned plain text body in the `## Source Body` section of `sources/<slug>.md`.
4. Continue with **Common workflow** below from step 2.

### Mode B — folder sweep (`<folder>` provided, OR `inbox/` swept by default)

Curatorial flow. The folder contains mixed content; classify each file before doing anything irreversible.

1. List every file (recursive) under the folder. Skip hidden files and `.gitkeep`.
2. **Classify each file** with the user. For each, propose one of three classifications and confirm in chat before acting:

   | Classification | Criteria | Action |
   |---|---|---|
   | **Source** | The file is an external artifact you want citation-stable: PDF, transcript, article, screenshot, dataset. Authored elsewhere. | Move to `sources/<slug>.<ext>`. If binary, also create `sources/<slug>.md` summary. Then synthesize into chapters per the common workflow. |
   | **Wiki content** | Authored prose meant to be wiki-shaped (notes, drafts, half-finished chapters, AI-generated docs). Not citation-stable. | Promote to `chapters/<chapter>/<page>.md` with proper frontmatter (`authority: grimoire`, no `sources:` unless a `sources/` artifact actually grounds it). **Remove the original** — its value now lives in the wiki. |
   | **Junk / unclear** | Duplicate, superseded, ambiguous, off-topic, or you can't tell yet. | Leave in place, flag for human review in the report. **Never auto-delete.** |

3. Process classifications in order (sources first, then wiki content, junk last). For each batch, run **Common workflow** steps 3–6 below, then move to the next batch.
4. After processing, the `inbox/` (or sweep folder) should be empty except for items the user needs to judge. Junk does NOT get auto-deleted.

### Common workflow (both modes)

#### 2. Read the source(s) and discuss takeaways

Read each filed artifact end-to-end. With the user, identify:

- Existing pages that already cover this material → those will be updated.
- Entities/concepts mentioned several times that have no page yet → propose creating them.
- Claims that contradict existing wiki pages → flag for the user; do not silently overwrite.
- Existing chapter affiliations the content fits.

Wait for confirmation before writing pages.

#### 3. Update affected pages

For each affected page (existing or new):

- **Existing page**: edit in place. Preserve frontmatter; bump `last_verified` to today; add the new source artifact path to `sources:` (deduplicate).
- **New page**: scaffold from `GRIMOIRE_ARCANA/formulae/page.formula.md` with appropriate `type:` and `authority:`. Source-derived pages get `authority: external` and a `sources:` entry. Wiki-content promotions (Mode B) get `authority: grimoire` (unless they cite a source artifact, in which case `hybrid`).

Wikilink existing pages with full-path targets such as `[[chapters/path/to/page|label]]` so Obsidian backlinks reflect new connections.

#### 4. Update the affected hubs

Each chapter hub touched gets a wikilink pointer to any newly-created page in its `## Routes` section.

#### 5. Close the provenance loop (sources only)

For each source-derived page, append the page path to the `## Wiki Pages Derived From This Source` section in `sources/<slug>.md`. Provenance flows both directions.

#### 6. Append a single log entry

```bash
python3 GRIMOIRE_ARCANA/rites/append_log.py \
  --grimoire . \
  --op ingest \
  --title "<short description>" \
  --skill /grm-domain-ingest \
  --field source="<inbox or path or single-file>" \
  --field pages-created=<n> \
  --field pages-updated=<n> \
  --field sources-added=<n> \
  --field inbox-remaining=<n>
```

One entry covers the whole sweep. Don't append per-file.

#### 7. Validate

```bash
python3 GRIMOIRE_ARCANA/rites/validate_frontmatter.py --grimoire .
python3 GRIMOIRE_ARCANA/rites/validate_provenance.py --grimoire .
python3 GRIMOIRE_ARCANA/rites/validate_links.py --grimoire .
```

Fix and re-run until clean. Do not append a second log entry for the fix.

## Non-negotiable rules

1. `sources/` is immutable after a file lands there. Never edit a filed source in place.
2. `inbox/` items that get promoted to `chapters/` get **moved** (original removed). Items that become `sources/` sources get **moved**. Items the AI can't classify are **left in place** and surfaced to the user — never auto-deleted.
3. Every page derived from a source carries `authority: external` (or `hybrid`) and lists the source in `sources:`.
4. Contradictions surface to the user; the wiki never silently overrides itself.
5. Full-path wikilinks for in-grimoire pointers; relative markdown paths only for non-wiki references.
6. One log entry per ingest operation, regardless of how many files were processed.

## Report

Surface in chat:

- **Mode used** (single file / folder / inbox sweep)
- **Sources filed** (count + paths under `sources/`)
- **Wiki pages created** (count + paths)
- **Wiki pages updated** (count + paths)
- **Hubs updated** (paths)
- **Items left in inbox** (paths + reason flagged)
- **Contradictions surfaced** (none / list)
- **Validators run** (pass/fail)
- **Log entry timestamp**

## Related

- Drop zone: `inbox/` (and its `inbox/README.md` contract)
- Page schema: `GRIMOIRE_ARCANA/docs/page_schema.md`
- Source formula: `GRIMOIRE_ARCANA/formulae/source.formula.md`
- Page formula: `GRIMOIRE_ARCANA/formulae/page.formula.md`
- Lint after a batch of ingests: `/grm-domain-lint`
- Promote a chat answer (no source) into a page: `/grm-domain-file-answer`
