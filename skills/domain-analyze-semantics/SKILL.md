---
name: {{NAMESPACE}}-domain-analyze-semantics
description: Deep semantic analysis of naming and organization for discoverability and token efficiency
when_to_use: User asks about naming quality, discoverability, or organization of a grimoire; user mentions chapter or page names feel awkward, redundant, or hard to find; user wants a judgment-based audit (not the mechanical /grm-arcana-validate-semantics check). Operates on the active domain grimoire.
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Analyze Semantics

You are performing a deep semantic analysis on the active domain grimoire. Follow the invocation guide below.

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
- **Reference**: `{{ARCANA_PATH}}/docs/reference.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/analyze_semantics.md`
