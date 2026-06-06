---
name: {{SKILL_PREFIX}}-add
description: Add knowledge content to the active grimoire - a page or a chapter, written fresh or distilled from the current chat session
when_to_use: User wants to add knowledge to their grimoire - "add a chapter for X", "document Y", "where should I put info about Z", "file this", "save this answer", "promote this to the wiki". The command sizes the material into a page or a chapter. For external files or source artifacts, use /grm-import instead. Operates on the resolved active grimoire.
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

!`cat {{ARCANA_PATH}}/invocations/grimoire/add.md`
