---
type: playbook
title: "File Answer"
aliases: ["file-answer", "domain-file-answer", "promote-answer"]
tags: [arcana/invocations, type/playbook, scope/domain]
authority: grimoire
last_verified: 2026-05-12
---

# Invocation: File Answer

## Purpose

Promote a chat answer (an analysis, a comparison, a derived insight) into a proper wiki page so it doesn't evaporate into chat history. The LLM-wiki principle: good answers compound the wiki the same way ingested sources do.

If a chat answer is just a one-line reply, skip this. Use it when the answer is something the user would want to find again, or that another query could synthesize against.

## Invocation

```
/grm-domain-file-answer
```

The agent decides what to file based on the immediate prior conversation. The user can scope it: "file the comparison", "file the analysis we just did".

## Preconditions

1. Working directory must be a registered domain grimoire. Refuse for Arcana itself.
2. There must be a recent substantive chat answer to file (the agent is responsible for identifying it; if unclear, ask).

## Workflow

### 1. Identify the answer to file

Ask the user (or infer from context) which answer to promote. Confirm the scope: a single page? Update an existing page? Both?

### 2. Choose page placement

Decide the chapter and `type:`:

- **`concept`** — a topic, technique, idea.
- **`entity`** — a specific person, project, product.
- **`playbook`** — a procedure derived from the conversation (most common for "how do I do X" answers).
- **`reference`** — a comparison table, a glossary entry, a cheatsheet.
- **`source`** — only when filing a transcript of an external thing; usually `/grm-domain-ingest` is the right skill for that.

Pick a slug (snake_case filename). Place under the most relevant chapter. If no chapter fits, this answer may be a hint to create a new chapter (`/grm-domain-create-chapter`).

### 3. Scaffold the page

Copy `GRIMOIRE_ARCANA/formulae/page.formula.md`. Fill the frontmatter:

- `type:` per Step 2.
- `title:` clear, query-shaped.
- `aliases:` alternate names a wikilink might use.
- `tags:` `chapter/<chapter>` plus `type/<type>` plus any domain tags.
- `authority: grimoire` (the wiki itself owns this analysis).
- `sources:` if the answer drew on source artifacts, list them. Otherwise empty.
- `last_verified:` today.

Write the body. The conversation is the source material — distill it into clean prose. Cite source artifacts with wikilinks (`[[<source-slug>]]`) when relevant.

### 4. Update affected hubs

Add a wikilink pointer in the relevant chapter hub's `## Routes` section. If multiple chapters relate, mention secondary hubs in `## Related Chapters`.

### 5. Append to log.md

```bash
python3 GRIMOIRE_ARCANA/rites/append_log.py \
  --grimoire . \
  --op file-answer \
  --title "<page title>" \
  --skill /grm-domain-file-answer \
  --field source=chat \
  --field pages=chapters/<chapter>/<slug>.md
```

### 6. Validate

```bash
python3 GRIMOIRE_ARCANA/rites/validate_frontmatter.py
python3 GRIMOIRE_ARCANA/rites/validate_links.py
```

## Non-negotiable rules

1. Filed answers carry `authority: grimoire` unless they directly summarize a single source (in which case use `/grm-domain-ingest`).
2. New page must be wired into a hub before considering the operation complete.
3. One log entry per file-answer.
4. Don't file trivial answers — promote what compounds.

## Report

Surface in chat:

- Page filed at `chapters/<chapter>/<slug>.md`
- Hub updated
- Log entry timestamp
- Validators pass/fail

## Related

- Page formula: `GRIMOIRE_ARCANA/formulae/page.formula.md`
- Page schema: `GRIMOIRE_ARCANA/docs/page_schema.md`
- Source ingest: `/grm-domain-ingest`
- New chapter when no chapter fits: `/grm-domain-create-chapter`
