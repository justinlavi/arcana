---
name: {{SKILL_PREFIX}}-grimoire-create-chapter
description: Create a new knowledge chapter in the active grimoire
when_to_use: User wants to add a chapter, document a topic in their grimoire, or has knowledge that doesn't fit any existing chapter. Phrases like "add a chapter for X", "document Y in this grimoire", "where should I put info about Z" are all good triggers. Requires being in a registered grimoire directory.
argument-hint: [chapter-topic]
arguments: [topic]
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Create Chapter

You are creating a new knowledge chapter in the active grimoire. Follow the invocation guide below exactly.

If the user provided a topic, use it: **$topic**

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Chapter formula**: `{{ARCANA_PATH}}/formulae/chapter_hub.formula.md`
- **Page formula**: `{{ARCANA_PATH}}/formulae/page.formula.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/create_chapter.md`
