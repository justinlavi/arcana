---
name: {{SKILL_PREFIX}}-health-check
description: Health-check the active grimoire for structural and knowledge-quality issues
when_to_use: Quarterly hygiene pass; after a batch of imports; user mentions "health check the wiki", "check the grimoire", or "find orphans / stale pages / contradictions". Combines mechanical validators with judgment-based passes.
user-invocable: true
allowed-tools: Bash Read Edit
---

# Health Check Grimoire

You are health-checking the active grimoire. Combines mechanical rites (orphans, provenance, frontmatter, structure, links) with judgment passes (stale, ghost references, contradictions, missing cross-refs). Surface findings; apply only fixes the user approves.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Grimoire root**: resolved active grimoire (`GRIMOIRE_ROOT`)

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/health_check.md`
