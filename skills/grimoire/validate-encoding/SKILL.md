---
name: {{SKILL_PREFIX}}-validate-encoding
description: Validate UTF-8, LF line endings, BOMs, mojibake markers, and repair artifacts in the active grimoire
when_to_use: User asks to check a grimoire for encoding, newline, mojibake, or cross-platform text issues; after broad edits on Windows, Linux, or macOS; before committing grimoire changes.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Grimoire Encoding

You are validating encoding and newline safety in the active grimoire.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grimoire/validators/validate_encoding.md`
