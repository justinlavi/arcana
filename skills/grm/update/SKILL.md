---
name: {{SKILL_PREFIX}}-update
description: Bring everything current - pull Arcana and every grimoire, re-register skills, refresh the agent routing block, heal grimoires; or reconcile one surface (skills, library, agentfile) without pulling
when_to_use: User wants their grimoires and Arcana up to date, wants teammates' changes, says something may be stale, a slash command is missing or old, a grimoire folder was moved or renamed and the agent cannot find it, or the agent stopped following the library because its routing block is stale or missing. "update", "update everything", "pick up the team's changes", "my command disappeared", "the agent can't find my grimoire".
argument-hint: "[skills | library | agentfile]"
arguments: scope
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Update

You are bringing the user's setup current. With no scope, run the canonical Update procedure for Arcana and every grimoire. With a scope, reconcile only that surface: **$scope**

## Context

- **Canonical procedure**: `{{ARCANA_PATH}}/UPDATE.md`, the skill-less source of truth; it works even when installed skills are stale
- **Arcana**: `{{ARCANA_PATH}}`
- **Grimoire library**: `~/grimoires/library.json`; the bare update covers every grimoire listed there, not only the one you are in

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/update.md`
