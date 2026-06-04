---
type: source
title: "[Source title - article headline, podcast episode, paper title]"
aliases: []
tags: [type/source]
sources: ["[original URL, capture origin, or sibling raw artifact path]"]
authority: external
last_verified: 1970-01-01
---

# [Source Title]

This source wrapper lives in `sources/<slug>.md`. It is a citation-stable
capture record, not an authored wiki page. Derived wiki pages live under
`chapters/` and cite this wrapper or its sibling raw artifact in `sources:`.

> Captured from: [original URL or origin]
> Captured on: YYYY-MM-DD
> Format: [article | transcript | paper | screenshot-set | dataset | other]

## Source Body

[The unmodified body of the source goes here, or a pointer to a sibling raw
artifact if the source is binary or too large for inline text.

For text sources (web articles, transcripts, paper text): paste the cleaned plain text below. The agent reads this directly during import.

For binary or large sources (PDFs, audio, video): keep the binary in
`sources/<slug>/` and reference that path here and in frontmatter `sources:`.
The agent processes the binary out-of-band.]

## Notes

[Anything important about how this source was captured. Trim notices, paywall-bypass markers, OCR confidence, transcription provenance, etc.]
