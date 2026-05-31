---
name: {{SKILL_PREFIX}}-validate-doc-trees
description: Detect drift between ASCII directory-tree diagrams in markdown docs and the actual filesystem of the active grimoire
when_to_use: User asks whether tree diagrams in READMEs / hubs / how-tos match the real folder layout; after renaming, adding, or removing chapters / skills / folders; before committing grimoire changes; user mentions stale file trees, drifted READMEs, or out-of-date directory diagrams.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Grimoire Doc Trees

You are detecting drift between ASCII directory-tree diagrams (in fenced code
blocks) and the actual filesystem of the active grimoire.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/validators/validate_doc_trees.md`
