---
type: hub
title: "{{GRIMOIRE_NAME}}"
aliases: ["{{GRIMOIRE_DIRECTORY}}", "{{GRIMOIRE_NAME_LOWER}}"]
tags: [grimoire/{{SKILL_NAMESPACE}}, type/hub, hub/root]
---

# {{GRIMOIRE_NAME}}

*{{GRIMOIRE_PURPOSE}}.* Routing entry point — see [README.md](README.md) for the long-form description. Framework reference: `GRIMOIRE_ARCANA/arcana.md`.

## Read Model

- Start here for any {{GRIMOIRE_DOMAIN}} request.
- Follow hubs depth-first to the answering leaf — explicit pointers only, no exploratory wording.
- In-grimoire pointers use Obsidian wikilinks (`[[page]]`); cross-grimoire references use `GRIMOIRE_ARCANA/...` placeholders.

## Route By Chapter

{{CHAPTER_ROUTES}}

## Fallback

If no route matches, propose one new canonical leaf plus a hub pointer rather than answering inline.
