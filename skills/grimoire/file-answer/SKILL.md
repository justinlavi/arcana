---
name: {{SKILL_PREFIX}}-file-answer
description: Promote a chat answer (analysis, comparison, derived insight) into a properly-frontmattered wiki page
when_to_use: User says "file this", "save this answer", "promote this to the wiki", or after a substantive chat answer that the user wants to find again later. Use when the answer is worth compounding into the knowledge base.
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# File Answer

You are promoting a chat answer into a wiki page so it doesn't evaporate into chat history.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Grimoire root**: resolved active grimoire (`GRIMOIRE_ROOT`)
- **Page formula**: `{{ARCANA_PATH}}/formulae/page.formula.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/file_answer.md`
