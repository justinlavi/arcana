---
name: {{NAMESPACE}}-domain-lint
description: Health-check the active grimoire — orphans, stale claims, ghost references, contradictions, missing cross-refs
when_to_use: Quarterly hygiene pass; after a batch of ingests; user mentions "lint the wiki", "check the grimoire", or "find orphans / stale pages / contradictions". Combines mechanical validators with judgment-based passes.
user-invocable: true
allowed-tools: Bash Read Edit
---

# Lint Grimoire

You are health-checking the active domain grimoire. Combines mechanical rites (orphans, provenance, frontmatter, structure, links) with judgment passes (stale, ghost references, contradictions, missing cross-refs). Surface findings; apply only fixes the user approves.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Grimoire root**: cwd (must be a registered domain grimoire)

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/lint.md`
