---
name: {{NAMESPACE}}-domain-validate-structure
description: Validate grimoire structure compliance against Arcana formulae
when_to_use: User asks if their grimoire is correctly structured, after creating or restructuring chapters, before committing grimoire changes, or as a quick sanity check. Mechanical/deterministic — no judgment. For Arcana itself, use /grm-arcana-validate-structure.
user-invocable: true
allowed-tools: Bash Read
---

# Validate Structure

You are validating grimoire structure compliance. Follow the invocation guide below.

## Precondition: Grimoire Directory Guard

**Before doing anything else**, verify the current working directory is a registered domain grimoire:

1. Read `~/grimoires/library.json`
2. Resolve each grimoire's `local_path` (expand `$HOME`)
3. Check if the current working directory matches any registered grimoire path

**If the directory is NOT a registered grimoire** (including Arcana — Arcana is not a grimoire):
- Display a clear error: "This skill operates on domain grimoires. Your current directory is not a registered grimoire."
- List available grimoires from the library with their paths
- Tell the user to `cd` to a grimoire directory and re-run
- **Stop.** Do not proceed.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Chapter formula**: `{{ARCANA_PATH}}/formulae/chapter_index.formula.md`
- **Page formula**: `{{ARCANA_PATH}}/formulae/page.formula.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/validate_structure.md`
