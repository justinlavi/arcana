---
name: {{SKILL_PREFIX}}-setup
description: Get set up with Grimoire - join a grimoire your team already has (paste its repository link), start a new one, or adopt a folder of notes; works before any grimoire exists
when_to_use: User just installed Arcana or was told to use a grimoire and says "set me up", "get started", "join the X grimoire", "I have a link to a grimoire", "how do I get the team's grimoire", or asks what to do first. Also when no grimoire is registered yet. For creating from scratch use /grm-create; for turning an existing folder into a grimoire use /grm-adopt.
argument-hint: "[git url]"
arguments: url
user-invocable: true
allowed-tools: Bash Read
---

# Setup

You are walking a person through getting their first grimoire, or joining one their team already has, in plain words and one question at a time. Follow the invocation below exactly. If the user passed a repository link, it is: **$url**

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Invocation**: `{{ARCANA_PATH}}/invocations/grm/setup.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/setup.md`
