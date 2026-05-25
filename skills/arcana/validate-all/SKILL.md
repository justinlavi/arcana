---
name: {{SKILL_PREFIX}}-validate-all
description: Run the full Arcana validator suite via the orchestrator rite (every mechanical check in one shot)
when_to_use: Before committing changes to Arcana itself; after bulk edits to Arcana docs/invocations/rites/skills; as a pre-release gate; user mentions "validate Arcana" or "check before commit". Cheap and read-only - safe to run liberally.
user-invocable: true
allowed-tools: Bash Read
---

# Validate Arcana (All)

You are running the full validator suite against the Arcana repository. Follow the invocation guide below.

## Invocation

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_all.md`
