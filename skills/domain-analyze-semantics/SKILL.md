---
name: {{NAMESPACE}}-domain-analyze-semantics
description: Deep semantic analysis of naming and organization for discoverability and token efficiency
when_to_use: User asks about naming quality, discoverability, or organization of a grimoire; user mentions chapter or page names feel awkward, redundant, or hard to find; user wants a judgment-based audit (not the mechanical /grm-arcana-validate-semantics check). Operates on the active domain grimoire.
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Analyze Semantics

You are performing a deep semantic analysis on the active domain grimoire. Follow the invocation guide below.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Reference**: `{{ARCANA_PATH}}/docs/reference.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/analyze_semantics.md`
