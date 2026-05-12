---
name: {{NAMESPACE}}-domain-improve
description: Comprehensive grimoire improvement — audit, normalize, and optimize the active domain grimoire
when_to_use: User asks to audit, polish, improve, or review a domain grimoire; user is preparing for a release; user mentions tech debt, drift, or stale content in their grimoire. Operates on the *active* grimoire (must be cd'd into a registered grimoire). For Arcana itself, use /grm-arcana-improve instead.
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Improve Grimoire

You are performing a comprehensive improvement on the active domain grimoire. Follow the invocation guide below exactly.

## Precondition: Grimoire Directory Guard

**Before doing anything else**, verify the current working directory is a registered domain grimoire:

1. Read `~/grimoires/library.json`
2. Resolve each grimoire's `local_path` (expand `$HOME`)
3. Check if the current working directory matches any registered grimoire path

**If the directory is NOT a registered grimoire** (including Arcana — Arcana is not a grimoire):
- Display a clear error: "This skill operates on domain grimoires. Your current directory is not a registered grimoire."
- List available grimoires from the library with their paths
- Tell the user to `cd` to a grimoire directory and re-run
- **Stop.** Do not proceed with any phases.

## Context

- **Arcana**: `{{ARCANA_PATH}}`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/improve_grimoire.md`
