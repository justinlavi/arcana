---
type: reference
title: "Validate Encoding"
aliases: ["validate-encoding", "validate-newlines", "validate-mojibake"]
tags: [arcana/invocations, type/reference, scope/quality]
authority: grimoire
last_verified: 2026-05-24
---

# Validate Arcana Encoding

## Purpose

Mechanically check that text files are portable across Windows, Linux, macOS, Git, and agent rewrite paths.

Arcana and grimoires may use Unicode for useful visual texture, but text files must be UTF-8 without BOM, use LF line endings, and avoid mojibake artifacts.

## Invocation

```
/arc-validate-encoding
```

Or directly:

```bash
python3 ARCANA_HOME/rites/validate_encoding.py
```

The same standard applies to Arcana and to every grimoire. For an active grimoire, use `/grm-validate-encoding`.

## What it rejects

1. Text files that are not valid UTF-8.
2. UTF-8 BOM markers.
3. CRLF or bare-CR line endings.
4. Common mojibake markers such as Latin capital A with tilde, Latin capital A with circumflex, Latin small a with circumflex, or the replacement character.
5. Known ASCII-shaped repair artifacts from broken dash/arrow repair.

## Why this matters

Without this check, a Windows-side rewrite can silently turn UTF-8 punctuation or emoji into unreadable mojibake, and Git can churn every touched file between LF and CRLF. The validator turns that class of breakage into an explicit failure while still allowing intentional Unicode.

## Related

- Validator suite hub: [[invocations/arcana/validators/validators|validators]]
- Portability validator: [[invocations/arcana/validators/validate_portability|validate_portability]]
- Page schema validator: [[invocations/arcana/validators/validate_frontmatter|validate_frontmatter]]
