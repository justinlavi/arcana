---
name: {{SKILL_PREFIX}}-save
description: Share what you changed in the active grimoire with your team - validates, records the changes with a short description, brings in teammates' changes, and sends yours to the shared repository
when_to_use: User finished editing pages or importing sources and says "save", "share this", "publish my changes to the team", "push this", "sync my edits", or asks how teammates get their changes. Operates on the resolved active grimoire. To pick up other people's changes without sharing yours, use /grm-update.
argument-hint: "[what you changed]"
arguments: message
user-invocable: true
allowed-tools: Bash Read
---

# Save

You are sharing the user's grimoire changes with their team: validate, record with a one-line description, bring in what teammates saved meanwhile, send. Follow the invocation below exactly. If the user described the change, it is: **$message**

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Invocation**: `{{ARCANA_PATH}}/invocations/grm/save.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/save.md`
