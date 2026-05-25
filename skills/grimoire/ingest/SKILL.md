---
name: {{SKILL_PREFIX}}-ingest
description: Bring content into the active grimoire - single source, folder, or inbox/ sweep - classifying each item into sources/ (citations), chapters/ (wiki content), or leaving it for review
when_to_use: User wants to absorb material into a grimoire. Triggers include "ingest this", "process the inbox", "sort the dump", "absorb this folder", "add this article", or dropping content into the grimoire's `inbox/` folder for processing. Polymorphic - works on a single file, a folder of mixed content, or (no argument) the grimoire's inbox/.
argument-hint: [path-or-folder-or-empty]
arguments: [source]
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Ingest

You are bringing content into the active grimoire. The skill is polymorphic and routes content to the right destination based on what it is. Follow the invocation guide below.

If the user provided a source location, use it: **$source**
If no argument was provided, default to sweeping `inbox/`.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Grimoire root**: cwd (must be a registered grimoire)
- **Sources layer**: `sources/` (immutable; LLM never edits filed artifacts)
- **Inbox layer**: `inbox/` (transient drop zone; gets emptied on ingest)
- **Wiki layer**: `chapters/` (curated, frontmattered)
- **Source formula**: `{{ARCANA_PATH}}/formulae/source.formula.md`
- **Page formula**: `{{ARCANA_PATH}}/formulae/page.formula.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/ingest.md`
