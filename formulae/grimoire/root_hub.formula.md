---
type: hub
title: "{{GRIMOIRE_NAME}}"
aliases: ["{{GRIMOIRE_DIRECTORY}}", "{{GRIMOIRE_NAME_LOWER}}"]
tags: [grimoire/{{SKILL_NAMESPACE}}, type/hub, hub/root]
---

# {{GRIMOIRE_NAME}}

{{GRIMOIRE_PURPOSE}}

- **Domain**: {{GRIMOIRE_DOMAIN}}
- **Skill namespace**: `{{SKILL_NAMESPACE}}-*`
- **Arcana**: `GRIMOIRE_ARCANA/arcana.md`

## Read Model

- Start here for any {{GRIMOIRE_DOMAIN}} request.
- Hub convention: every folder F has a hub at `F/<basename(F)>.md`. A hub routes to sub-hubs, to leaf pages, or both — depth is open-ended. Each hop narrows the search until the answering leaf is reached.
- Use wikilinks (`[[page]]`) inside this grimoire so Obsidian backlinks and graph view work; cross-grimoire references use path placeholders (`GRIMOIRE_ARCANA/...`).
- Follow explicit pointers only — no exploratory wording.

## Layers

- **`sources/`** — immutable source artifacts (articles, transcripts, papers). LLM reads, never edits.
- **`inbox/`** — transient drop zone for mixed content awaiting classification. Cleared by `/grm-domain-ingest`.
- **`chapters/`** — LLM-authored knowledge pages with required frontmatter. See `GRIMOIRE_ARCANA/docs/page_schema.md`.
- **`log.md`** — append-only activity log; entries prefixed `## [YYYY-MM-DD HH:MM] <op> | <title>`.

## Route By Chapter

{{CHAPTER_ROUTES}}

## Operations

- Add a new source → `/{{SKILL_NAMESPACE}}-domain-ingest` (or `/grm-domain-ingest` if not yet renamed)
- File a chat answer back into the wiki → `/grm-domain-file-answer`
- Health check (orphans, stale pages, missing cross-refs) → `/grm-domain-lint`
- Add a new chapter → `/grm-domain-create-chapter`

## Fallback

If no route matches, propose one new canonical leaf plus a hub pointer rather than answering inline.
