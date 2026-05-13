# `sources/` — Immutable Source Layer

This directory holds the **immutable source artifacts** that feed this grimoire's wiki.

## Contract

- **Read, never write.** Skills and invocations must not modify files in `sources/`. Source artifacts are the ground truth that the wiki summarizes.
- **Anything goes.** Articles, transcripts, screenshots, papers, datasets — whatever you ingest. Use `formulae/source.formula.md` as a starting point for text sources. Binary assets (PDFs, audio, video) live in `sources/<slug>/`.
- **Stable file paths.** Once a source is filed, do not rename it. Wiki pages cite these paths in their `sources:` frontmatter; renaming breaks provenance.
- **Provenance lives here.** Each ingested artifact is the canonical record of where the wiki's external claims came from. The `validate_provenance` rite checks that every page with `authority: external` or `hybrid` resolves to at least one source artifact that exists.

## How content lands here

- Manual: drop a file in.
- `/grm-domain-ingest <path-or-url>` (recommended): files the source, summarizes it, updates affected wiki pages, appends to `log.md`.

## What does NOT belong here

- Original work authored inside this grimoire (those go under `chapters/` for domain grimoires, or `docs/` for Arcana).
- Generated derivatives (summaries, extracted figures with edits, transcripts you've corrected): those live under `chapters/` with a `sources:` pointer back to the source artifact they came from.
