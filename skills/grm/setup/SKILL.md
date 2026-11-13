---
name: {{SKILL_PREFIX}}-setup
description: Get set up with Grimoire - join a grimoire your team already has (paste its repository link), turn a folder of notes into a grimoire, or start a new one; works before any grimoire exists
when_to_use: User just installed Arcana or was told to use a grimoire and says "set me up", "get started", "join the X grimoire", "I have a link to a grimoire", "make this folder a grimoire", "register this directory", or asks what to do first. Also when no grimoire is registered yet, or when update reports an unmanaged folder. For a brand-new grimoire from scratch the conversation hands off to /grm-create.
argument-hint: "[git url | folder]"
arguments: target
user-invocable: true
allowed-tools: Bash Read
---

# Setup

You are walking a person through getting their first grimoire, joining one their team already has, or turning a folder they already have into one, in plain words and one question at a time. Follow the invocation below exactly. If the user passed a repository link or a folder, it is: **$target**

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Join rite**: `{{ARCANA_PATH}}/rites/install_grimoire.py`
- **Adopt rite**: `{{ARCANA_PATH}}/rites/adopt_grimoire.py`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/setup.md`
