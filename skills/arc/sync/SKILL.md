---
name: {{SKILL_PREFIX}}-sync
description: Sync the local environment to current Arcana by sub-target - skills (agent skill directories), library (~/grimoires/library.json), or agentfile (the Grimoire instruction block)
when_to_use: A skill isn't appearing in the slash-command picker, or skills were added, edited, or installed (skills); a grimoire was cloned, moved, or removed by hand and the library drifted from disk (library); the Grimoire instruction block in an agent file needs refreshing after Arcana changes (agentfile). Run with exactly one positional sub-target - skills, library, or agentfile. For active-grimoire-only skill sync, use /grm-sync.
argument-hint: skills|library|agentfile
arguments: target
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Sync Arcana Environment

You are syncing the local environment to current Arcana. This command is scope-respecting: it routes a single positional sub-target to the matching rite or judgment edit. Resolve `$target` and run only that sub-target.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Invocation**: `{{ARCANA_PATH}}/invocations/arc/sync.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/arc/sync.md`
