---
name: {{SKILL_PREFIX}}-import
description: Import files, folders, or inbox content into the active grimoire
when_to_use: User wants to bring material into a grimoire. Triggers include "import this", "process the inbox", "sort the dump", "absorb this folder", "add this article", or dropping content into the grimoire's `inbox/` folder for processing. Polymorphic - works on a single file, a folder of mixed content, or (no argument) the grimoire's inbox/.
argument-hint: [path-or-folder-or-empty]
arguments: source
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Import

You are bringing content into the active grimoire. The skill is polymorphic and routes content to the right destination based on what it is. Follow the invocation guide below.

If the user provided a source location, use it: **$source**
If no argument was provided, default to sweeping `inbox/`.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Grimoire root**: resolved active grimoire (`GRIMOIRE_ROOT`)
- **Sources layer**: `sources/` (immutable; LLM never edits filed artifacts)
- **Inbox layer**: `inbox/` (transient drop zone; gets emptied on import)
- **Wiki layer**: `chapters/` (curated, frontmattered)
- **Source formula**: `{{ARCANA_PATH}}/formulae/source.formula.md`
- **Page formula**: `{{ARCANA_PATH}}/formulae/page.formula.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/import.md`
