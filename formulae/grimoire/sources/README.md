# `sources/` - Immutable Source Layer

This directory holds the **immutable source artifacts** that feed this grimoire's wiki.

## Contract

- **File, then read.** Ingest may create source artifacts and wrappers. After a source lands here, skills and invocations read it but do not edit it in place.
- **Raw artifacts and wrappers.** Articles, transcripts, screenshots, papers, datasets - whatever you ingest. Use `formulae/source.formula.md` for source wrapper Markdown. Binary assets (PDFs, audio, video) live in `sources/<slug>/` with an optional sibling wrapper at `sources/<slug>.md`.
- **Stable file paths.** Once a source is filed, do not rename it. Wiki pages cite these paths in their `sources:` frontmatter; renaming breaks provenance.
- **Provenance lives here.** Each ingested artifact is the canonical record of where the wiki's external claims came from. The `validate_provenance` rite checks that every page with `authority: external` or `hybrid` resolves to at least one source artifact that exists.
- **No derived-page backlinks.** Source wrappers do not maintain lists of derived wiki pages. The wiki pages carry the provenance pointers in their own frontmatter.

## How content lands here

- Manual: drop a file in.
- `/grm-ingest <path-or-url>` (recommended): files the source, summarizes it, updates affected wiki pages, appends to `log.md`.

## What does NOT belong here

- Original work authored inside this grimoire (those go under `chapters/` for grimoires, or `docs/` for Arcana).
- Authored synthesis, extracted analysis, corrected transcripts, and edited derivatives: those live under `chapters/` with a `sources:` pointer back to the source artifact they came from.
