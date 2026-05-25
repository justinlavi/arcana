---
type: reference
title: "Log Entry Formula"
aliases: ["log-format", "log-entry"]
tags: [type/reference, arcana/formula]
authority: grimoire
last_verified: 2026-05-12
---

# Log Entry Formula

`log.md` is append-only, parseable, and lives at the grimoire root. Every operation that mutates the wiki appends one entry. Skills and invocations call `rites/append_log.py` to write entries; do not edit `log.md` by hand outside append-only additions.

## Required prefix

Every entry begins with a level-2 heading in this exact shape:

```
## [YYYY-MM-DD HH:MM] <op> | <title>
```

- `<op>` is one of: `ingest`, `query`, `lint`, `improve`, `file-answer`, `rebuild-index`, `create`, `manual`.
- `<title>` is a short human-readable label (source name, query summary, etc.).

This shape lets you scan recent activity with `grep '^## \[' log.md | tail -20`.

## Entry body

Free-form bullet list, but include at minimum:

- `- skill: /<skill prefix>-<verb>` (or `manual` if hand-edited)
- `- pages: ` comma-separated relative paths touched
- For `ingest` / `file-answer`: `- source: sources/<filename>` or `- source: chat`

## Example entries

```markdown
## [2026-05-12 14:32] ingest | Tartine bread method article
- skill: /cook-domain-ingest
- source: sources/article-tartine-method.md
- pages: chapters/techniques/lamination.md, chapters/recipes/sourdough.md, chapters/techniques/techniques.md

## [2026-05-12 15:01] lint | quarterly health check
- skill: /arc-grimoire-lint
- orphans: 0
- stale (>90d): 3
- missing-xref candidates: 2 ("autolyse", "windowpane test")

## [2026-05-13 09:14] file-answer | sourdough vs ciabatta comparison
- skill: /arc-grimoire-file-answer
- source: chat
- pages: chapters/comparisons/sourdough_vs_ciabatta.md (new), chapters/comparisons/comparisons.md
```

## Rules

1. Append-only - never reorder or delete entries.
2. Local time, 24-hour clock, in `[YYYY-MM-DD HH:MM]` brackets.
3. Operation tag matches the predefined set above so log analysis tooling stays simple.
4. The first entry in any new grimoire is `create | <grimoire-name>` written by `/arc-grimoire-create`.
