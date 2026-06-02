---
type: reference
title: "Log Entry Formula"
aliases: ["log-format", "log-entry"]
tags: [type/reference, arcana/formula]
authority: grimoire
last_verified: 2026-06-02
---

# Log Entry Formula

`log.md` is append-only, parseable, and lives at the grimoire root. Every operation that mutates the wiki appends one entry. Skills and invocations call `rites/append_log.py` to write entries; do not edit `log.md` by hand outside append-only additions.

## Scope - what the log records

The log is a history of the grimoire's **content**: which pages and sources were added, removed, or changed, and why. It is **not** a journal of version-control or workflow mechanics.

Describe *what changed in the wiki*, never *how the change was delivered*. An entry must read identically no matter which branch you authored on, whether the work arrived via a merge, rebase, or cherry-pick, or what conflicts you resolved along the way - those are VCS concerns that belong in commit messages, not here.

An entry must NOT:

- Scope itself by, or name, a git branch (e.g. "catch <branch> up to main", "merge main into <branch>").
- Treat a merge, rebase, cherry-pick, push, or conflict resolution as the operation. The `<op>` tags name grimoire operations (`ingest`, `create`, `improve`, ...), not git operations - there is no `merge` op.

If a content change happens to land while you are merging or rebasing, log the content (the page added or changed), not the merge:

```markdown
# Wrong - scoped by a branch, framed as a VCS operation, uses a non-existent op
## [2026-05-20 09:00] merge | Catch lamination-notes up to main; add poolish page
- change: merged main into the branch and resolved the conflict in techniques.md

# Right - scoped by the content that changed
## [2026-05-20 09:00] create | Poolish preferment page
- skill: /grm-create-chapter
- pages: chapters/techniques/poolish.md (new), chapters/techniques/techniques.md
- note: Adds the poolish preferment method and routes it from the techniques hub.
```

## Required prefix

Every entry begins with a level-2 heading in this exact shape:

```
## [YYYY-MM-DD HH:MM] <op> | <title>
```

- `<op>` is one of: `ingest`, `query`, `lint`, `improve`, `file-answer`, `rebuild-index`, `create`, `manual`. These name grimoire-content operations, not git operations - there is no `merge`, `rebase`, or `push` op (see Scope above).
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
- skill: /grm-lint
- orphans: 0
- stale (>90d): 3
- missing-xref candidates: 2 ("autolyse", "windowpane test")

## [2026-05-13 09:14] file-answer | sourdough vs ciabatta comparison
- skill: /grm-file-answer
- source: chat
- pages: chapters/comparisons/sourdough_vs_ciabatta.md (new), chapters/comparisons/comparisons.md
```

## Rules

1. Append-only - never reorder or delete entries.
2. Local time, 24-hour clock, in `[YYYY-MM-DD HH:MM]` brackets.
3. Operation tag matches the predefined set above so log analysis tooling stays simple.
4. The first entry in any new grimoire is `create | <grimoire-name>` written by `/grm-create`.
5. The log records grimoire content, not VCS mechanics. Never scope an entry by branch or frame it as a merge / rebase / push / conflict resolution; log what changed in the wiki and let commit messages carry the git story.
