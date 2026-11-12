---
name: {{SKILL_PREFIX}}-update
description: Bring an Arcana install and every grimoire current - pull, validate, re-register every installed grimoire's skills, refresh the agent routing blocks, heal; or reconcile one surface (skills, library, agentfile) without pulling
when_to_use: An Arcana maintainer or fork owner wants the engine, library, agent skills, and agent routing blocks current across every installed grimoire, or wants one of those surfaces reconciled after editing skills, moving a grimoire folder, or changing the routing block template. Platform-scope mirror of /grm-update.
argument-hint: "[skills | library | agentfile]"
arguments: scope
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Update

You are bringing an Arcana install and every grimoire that references it current, at platform scope. With no scope, run the canonical Update procedure. With a scope, reconcile only that surface: **$scope**

## Context

- **Canonical procedure**: `{{ARCANA_PATH}}/UPDATE.md`
- **Arcana**: `{{ARCANA_PATH}}`
- **Grimoire library**: `~/grimoires/library.json`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/arc/update.md`
