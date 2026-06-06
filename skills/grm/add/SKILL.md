---
name: {{SKILL_PREFIX}}-add
description: Write up new knowledge or save a chat answer as a page or chapter (text you author, not a file on disk) - for a file on disk use /grm-import
when_to_use: User wants to add knowledge to an existing grimoire - "add a chapter for X", "document Y", "where should I put info about Z", "file this", "save this answer", "promote this to the wiki". The command sizes the material into a page or a chapter. To create a whole new grimoire use /grm-create; for external files or source artifacts use /grm-import. Operates on the resolved active grimoire.
argument-hint: [topic or material]
arguments: topic
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Add Content

You are adding knowledge content to the active grimoire - a single page or a new chapter, sized to the material. Follow the invocation guide below exactly.

If the user provided a topic or material, use it: **$topic**

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Chapter formula**: `{{ARCANA_PATH}}/formulae/chapter_hub.formula.md`
- **Page formula**: `{{ARCANA_PATH}}/formulae/page.formula.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/add.md`
