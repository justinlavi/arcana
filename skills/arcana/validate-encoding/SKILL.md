---
name: {{SKILL_PREFIX}}-validate-encoding
description: Mechanically validate UTF-8, LF line endings, BOMs, mojibake markers, and repair artifacts
user-invocable: true
allowed-tools: Bash
---

# Validate Arcana Encoding

Run the encoding validator from the Arcana directory:

```bash
python3 rites/validate_encoding.py
```

For an active grimoire, use `/grm-validate-encoding`.
