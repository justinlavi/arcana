---
name: {{SKILL_PREFIX}}-move
description: Rename or move a page or chapter and automatically fix every link that pointed to it - for deleting content use /grm-remove
when_to_use: User wants to rename a page or chapter, move a page into a different chapter, or reorganize where content lives - "rename this page", "move X under Y", "reorganize this chapter". Updates all wikilinks and the chapter hubs. For deleting content use /grm-remove.
argument-hint: "[from-path] [to-path]"
arguments: source, destination
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Move or Rename Grimoire Content

You are renaming or moving a page or chapter in the active grimoire and keeping every link and hub correct. Resolve the active grimoire, then follow the invocation.

If the user named a source and destination, use them: **$source -> $destination**

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Invocation**: `{{ARCANA_PATH}}/invocations/grm/move.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/move.md`
