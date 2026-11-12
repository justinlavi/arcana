---
name: {{SKILL_PREFIX}}-add
description: Put knowledge into the active grimoire - write up a topic or save a chat answer as a page or chapter, or hand it a file, a folder, or the inbox to file as cited sources and update the wiki
when_to_use: User wants to add knowledge to an existing grimoire - "add a chapter for X", "document Y", "save this answer", "promote this to the wiki", "import this PDF", "file this article", "process the inbox", "sort this folder", or drops content into the grimoire's inbox/. A topic or pasted text is authored; a path on disk is filed as a source. To create a whole new grimoire use /grm-create. Operates on the resolved active grimoire.
argument-hint: "[topic | \"this answer\" | file | folder | inbox]"
arguments: material
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Add

You are putting knowledge into the active grimoire. What the user handed over decides the mode: a topic or a chat answer is authored into a page or chapter; a file, a folder, or the inbox is filed as sources and synthesized into the wiki. Follow the invocation below exactly.

If the user provided material or a path, it is: **$material**

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Page formula**: `{{ARCANA_PATH}}/formulae/page.formula.md`
- **Source formula**: `{{ARCANA_PATH}}/formulae/source.formula.md`
- **Chapter hub formula**: `{{ARCANA_PATH}}/formulae/chapter_hub.formula.md`
- **Page stamping rite**: `{{ARCANA_PATH}}/rites/new_page.py`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/add.md`
