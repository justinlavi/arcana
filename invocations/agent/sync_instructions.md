---
type: playbook
title: "Sync Agent Grimoire Instructions"
aliases: ["sync-agent-instructions", "refresh-agent-block"]
tags: [arcana/invocations, type/playbook, scope/agent]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Sync Agent Grimoire Instructions

## Purpose

Refresh the Grimoire instruction block inside user agent instruction files, preserving all non-Grimoire content. This is AI-guided judgment work, not a pure mechanical rewrite: users often keep unrelated project, style, safety, or personal instructions in the same files.

Canonical block: `ARCANA_HOME/rites/templates/grimoire_block.md`.

## Invocation

```
/arc-agent-sync-instructions
```

Optional user text may name explicit files to update.

## Default Targets

Inspect existing files only unless the user explicitly asks to create missing
ones. Default automatic targets come from
`ARCANA_HOME/rites/data/agent_targets.json` entries with `instruction_mode:
auto`; see `ARCANA_HOME/docs/agent_targets.md` for the current matrix.

If the user provides paths, inspect those too. If the current repository contains `AGENTS.md`, `CLAUDE.md`, `.github/copilot_instructions.md`, or similarly named agent instruction files, mention them as candidates but ask before modifying project-level files unless the user explicitly included them.

Do not scan all of `$HOME` by default. If the user asks for "everything on this machine", ask before running a bounded search and explain the scope.

## Workflow

### 1. Load the canonical block

Read `ARCANA_HOME/rites/templates/grimoire_block.md`. This is the source of truth. Preserve it exactly when inserting or replacing, aside from surrounding blank lines needed to fit the target document.

### 2. Inspect each target

For each candidate file:

1. If the file does not exist, skip it by default and report that it was absent.
2. Read the full file before editing.
3. Determine whether it contains a Grimoire block:
  - Preferred: text between `<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->` and `<!-- END GRIMOIRE KNOWLEDGE BASE -->`.
  - Ambiguous: multiple Grimoire sections, malformed markers, or surrounding text that looks user-authored. Stop and ask before editing that file.

### 3. Patch conservatively

Apply the smallest safe edit:

- Existing marked block: replace only the marked region with the canonical block.
- No existing block in an existing default target: insert the canonical block after the first top-level heading if there is one, otherwise append it to the end. If the file is project-level or user-specified but not a default target, ask before inserting.

Never rewrite, sort, reflow, or deduplicate non-Grimoire content. Preserve frontmatter, comments, headings, personal instructions, project rules, and unrelated agent configuration exactly.

### 4. Review after editing

After editing each file:

- Re-read the file.
- Confirm exactly one Grimoire block is present.
- Confirm the canonical block text appears exactly once.
- Summarize whether the operation was `updated`, `inserted`, `skipped`, or `needs user decision`.

### 5. Sync skills if needed

This skill updates instruction files only. If the user also needs newly added skills to appear in slash-command pickers, run or recommend `/arc-agent-sync-skills` separately.

## Safety Rules

1. Preserve all non-Grimoire content.
2. Do not create missing instruction files unless the user explicitly asks.
3. Do not edit project-level instruction files without explicit user confirmation.
4. Do not replace a whole file when a block-level edit is possible.
5. Ask before editing when the Grimoire block boundaries are ambiguous.
6. Report every file touched.

## Related

- Canonical block: `ARCANA_HOME/rites/templates/grimoire_block.md`
- Agent targets: `ARCANA_HOME/docs/agent_targets.md`
- Agent configuration: `ARCANA_HOME/docs/agent_configuration.md`
- Skill registration: `/arc-agent-sync-skills`
