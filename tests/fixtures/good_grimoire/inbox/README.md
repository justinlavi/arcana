# `inbox/` - Transient Drop Zone

This directory is the place to drop **mixed content that needs to be sorted**: zip extracts, AI-generated drafts, copy-pasted notes, half-finished documentation a coworker handed you, screenshots that may or may not be source-worthy. Anything that's "stuff I want to absorb into this grimoire but I haven't classified yet."

## Contract

- **Transient.** `inbox/` is meant to be emptied. After absorption, only items that need human judgment remain.
- **Mixed content allowed.** Drop binaries, markdown, partial files, whole folders.
- **Not citation-stable.** Wiki pages should never set a `sources:` entry pointing at `inbox/`. Items with citation value get moved to `sources/` first; items without get promoted to `chapters/` and the original is removed.
- **No structure required.** No frontmatter, no naming convention, no folder discipline. The AI will sort it.

## How content lands here

- Manual: drop, drag, extract, save-as into `inbox/` directly.
- Tooling: any external pipeline (web clipper, downloader, screenshot tool) that targets `inbox/` is fine - items will be classified and relocated on next absorption pass.

## How content leaves here

Run `/grm-import` (no argument sweeps `inbox/`). The skill walks the folder and, for each file, proposes a classification - confirmed in chat - then moves the file:

| Classification | Destination | Notes |
|---|---|---|
| **External source artifact** | `sources/<slug>` (+ sibling `sources/<slug>.md` wrapper when useful) | Becomes immutable, citation-worthy. Pages with `authority: external` cite this. |
| **Wiki content / draft** | `chapters/<chapter>/<page>.md` with proper frontmatter | Promoted; original removed (its value is now in the wiki). Authority defaults to `grimoire` unless the draft synthesized a `sources/` source. |
| **Junk / superseded / unclear** | Stays in `inbox/`, flagged in chat | User decides whether to delete or revisit. |

After absorption the `import` skill appends a single log entry to `log.md` summarizing what was filed where.

## What does NOT belong here

- Files you want to keep around as immutable references -> `sources/` directly.
- Authored wiki content you've already written -> `chapters/` directly (use `/grm-create-chapter` if you want scaffolding).
- Operating state from another tool (caches, indexes, build artifacts).
