---
type: hub
title: "{{GRIMOIRE_NAME}}"
aliases: ["{{GRIMOIRE_DIRECTORY}}", "{{GRIMOIRE_NAME_LOWER}}"]
tags: [grimoire/{{SKILL_PREFIX}}, type/hub, hub/root]
---

# {{GRIMOIRE_NAME}}

*{{GRIMOIRE_PURPOSE}}.* Routing entry point - see [[README|README]] for the long-form description. Framework reference: `ARCANA_HOME/arcana.md`.

## Read Model

- Start here for any {{GRIMOIRE_DOMAIN}} request.
- Follow hubs depth-first to the answering leaf - explicit pointers only.
- In-grimoire pointers use full-path Obsidian wikilinks (`[[chapters/path/to/page|label]]`); cross-grimoire references use `ARCANA_HOME/...` placeholders.

## Route By Chapter

{{CHAPTER_ROUTES}}

## Fallback

If no route matches, propose one new canonical leaf plus a hub pointer rather than answering inline.
