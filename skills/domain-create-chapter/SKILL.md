---
name: grm-domain-create-chapter
description: Create a new knowledge chapter in the active domain grimoire
argument-hint: [chapter-topic]
arguments: [topic]
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Create Chapter

You are creating a new knowledge chapter in the active domain grimoire. Follow the invocation guide below exactly.

If the user provided a topic, use it: **$topic**

## Precondition: Grimoire Directory Guard

**Before doing anything else**, verify the current working directory is a registered domain grimoire:

1. Read `~/grimoire/catalog.json`
2. Resolve each grimoire's `local_path` (expand `$HOME`)
3. Check if the current working directory matches any registered grimoire path

**If the directory is NOT a registered grimoire** (including Arcana — Arcana is not a grimoire):
- Display a clear error: "This skill operates on domain grimoires. Your current directory is not a registered grimoire."
- List available grimoires from the catalog with their paths
- Tell the user to `cd` to a grimoire directory and re-run
- **Stop.** Do not proceed.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Chapter formula**: `{{ARCANA_PATH}}/formulae/chapter_index.formula.md`
- **Page formula**: `{{ARCANA_PATH}}/formulae/page.formula.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/create_chapter.md`
