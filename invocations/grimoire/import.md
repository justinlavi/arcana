---
type: playbook
title: "Import Source"
aliases: ["import", "domain-import"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-05-13
---

# Invocation: Import

## Purpose

Bring external content into a grimoire. The skill is polymorphic - it accepts a single source artifact, a folder, or no argument (sweep `inbox/`). It classifies each item and routes it to the right destination:

- **External source artifact** -> `sources/<slug>` or `sources/<slug>.md` (immutable, citation-worthy)
- **Wiki content / draft** -> `chapters/<chapter>/<page>.md` (curated, frontmattered)
- **Junk / unclear** -> stays where it is, flagged for human review

`sources/` and `chapters/` are the destinations. `inbox/` is the (optional) staging area.

For a one-off chat answer with no source artifact, use `/grm-capture-answer` instead.

## Invocation

```
/grm-import                # no arg: sweep inbox/ if it exists
/grm-import <file>         # single source artifact
/grm-import <folder>       # walk that folder, classify each file
```

If the user provides only a description, ask for a source location (or instruct them to drop into `inbox/`) before continuing.

## Preconditions

1. Resolve `GRIMOIRE_ROOT` with the shared grimoire directory guard. Refuse for Arcana itself.
2. `sources/` and `log.md` must exist at the grimoire root. If missing, instruct the user to re-scaffold or run `/grm-validate structure`.
3. `inbox/` is optional. If the user invokes with no argument and no `inbox/` exists, ask whether to create one or to point at a specific path.

## Modes

### Mode A - single source artifact (`<file>` provided)

The classic provenance-careful flow. The argument is a single immutable artifact (article, transcript, paper, screenshot, PDF).

1. Pick a short snake_case-or-kebab-case slug and decide whether the source
   should be filed as a raw artifact, a source wrapper, or both.
2. For text sources, create `sources/<slug>.md` from
   `ARCANA_HOME/formulae/source.formula.md` and place the cleaned plain text
   body in `## Source Body`.
3. For binary or large sources, copy the raw artifact to
   `sources/<slug>/<original-file>` and create `sources/<slug>.md` as the
   wrapper pointing at that raw artifact.
4. For a raw artifact that is already citation-ready and needs no wrapper,
   copy it to `sources/<slug>.<ext>` and cite that path directly.
5. Continue with **Common workflow** below from step 2.

### Mode B - folder sweep (`<folder>` provided, OR `inbox/` swept by default)

Curatorial flow. The folder contains mixed content; classify each file before doing anything irreversible.

1. List every file (recursive) under the folder. Skip hidden files and `.gitkeep`.
2. **Classify each file** with the user. For each, propose one of three classifications and confirm in chat before acting:

   | Classification | Criteria | Action |
   |---|---|---|
   | **Source** | The file is an external artifact you want citation-stable: PDF, transcript, article, screenshot, dataset. Authored elsewhere. | Move or wrap it under `sources/` using Mode A's source wrapper rules. Then synthesize into chapters per the common workflow. |
   | **Wiki content** | Authored prose meant to be wiki-shaped (notes, drafts, half-finished chapters, AI-generated docs). Not citation-stable. | Promote to `chapters/<chapter>/<page>.md` with proper frontmatter (`authority: grimoire`, no `sources:` unless a `sources/` artifact actually grounds it). **Remove the original** - its value now lives in the wiki. |
   | **Junk / unclear** | Duplicate, superseded, ambiguous, off-topic, or you can't tell yet. | Leave in place, flag for human review in the report. **Never auto-delete.** |

3. Process classifications in order (sources first, then wiki content, junk last). For each batch, run **Common workflow** steps 3-6 below, then move to the next batch.
4. After processing, the `inbox/` (or sweep folder) should be empty except for items the user needs to judge. Junk does NOT get auto-deleted.

### Common workflow (both modes)

#### 2. Read the source(s) and discuss takeaways

Read each filed artifact end-to-end. With the user, identify:

- Existing pages that already cover this material -> those will be updated.
- Entities/concepts mentioned several times that have no page yet -> propose creating them.
- Claims that contradict existing wiki pages -> flag for the user; do not silently overwrite.
- Existing chapter affiliations the content fits.

Wait for confirmation before writing pages.

#### 3. Update affected pages

For each affected page (existing or new):

- **Existing page**: edit in place. Preserve frontmatter; bump `last_verified` to today; add the new source artifact path to `sources:` (deduplicate).
- **New page**: scaffold from `ARCANA_HOME/formulae/page.formula.md` with appropriate `type:` and `authority:`. Source-derived pages get `authority: external` and a `sources:` entry. Wiki-content promotions (Mode B) get `authority: grimoire` (unless they cite a source artifact, in which case `hybrid`).

Wikilink existing pages with full-path targets such as `[[chapters/path/to/page|label]]` so Obsidian backlinks reflect new connections.

#### 4. Update the affected hubs

Each chapter hub touched gets a wikilink pointer to any newly-created page in its `## Routes` section.

#### 5. Close provenance from the wiki side

For each source-derived page, make sure the page frontmatter cites the stable
source wrapper or raw artifact under `sources:`. Do not append backlinks or
derived-page lists to files under `sources/`; source wrappers are capture
records, and wiki pages carry the provenance pointers.

#### 6. Append a single log entry

```bash
python3 ARCANA_HOME/rites/append_log.py \
  --grimoire GRIMOIRE_ROOT \
  --op import \
  --title "<short description>" \
  --skill /grm-import \
  --field source="<inbox or path or single-file>" \
  --field pages-created=<n> \
  --field pages-updated=<n> \
  --field sources-added=<n> \
  --field inbox-remaining=<n>
```

One entry covers the whole sweep. Don't append per-file.

#### 7. Validate

```bash
python3 ARCANA_HOME/rites/validate_frontmatter.py --grimoire GRIMOIRE_ROOT
python3 ARCANA_HOME/rites/validate_provenance.py --grimoire GRIMOIRE_ROOT
python3 ARCANA_HOME/rites/validate_links.py --grimoire GRIMOIRE_ROOT
```

Fix and re-run until clean. Do not append a second log entry for the fix.

## Non-negotiable rules

1. `sources/` is immutable after a file lands there. Never edit a filed source in place.
2. `inbox/` items that get promoted to `chapters/` get **moved** (original removed). Items that become `sources/` sources get **moved**. Items the AI can't classify are **left in place** and surfaced to the user - never auto-deleted.
3. Every page derived from a source carries `authority: external` (or `hybrid`) and lists the source in `sources:`.
4. Contradictions surface to the user; the wiki never silently overrides itself.
5. Full-path wikilinks for in-grimoire pointers; relative markdown paths only for non-wiki references.
6. One log entry per import operation, regardless of how many files were processed.

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
- Page schema: `ARCANA_HOME/docs/page_schema.md`
- Source formula: `ARCANA_HOME/formulae/source.formula.md`
- Page formula: `ARCANA_HOME/formulae/page.formula.md`
- Health-check after a batch of imports: `/grm-health-check`
- Promote a chat answer (no source) into a page: `/grm-capture-answer`
