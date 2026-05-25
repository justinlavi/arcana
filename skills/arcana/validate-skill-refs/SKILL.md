---
name: {{SKILL_PREFIX}}-validate-skill-refs
description: Mechanically validate that every Arcana-shipped slash command mentioned in Arcana docs resolves to a real skill source
when_to_use: After renaming or removing any skill; after editing docs that mention `/arc-*` or `/grm-*` commands; as a phase of `/arc-improve`; user mentions "stale skill reference", "broken slash command", or "did I rename a skill". Cheap and read-only.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Arcana Skill References

You are running the skill-reference validator against the Arcana repository. Follow the invocation guide below.

## Invocation

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_skill_refs.md`
