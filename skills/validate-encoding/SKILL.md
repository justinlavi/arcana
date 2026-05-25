---
name: arc-validate-encoding
description: Mechanically validate UTF-8, LF line endings, BOMs, and mojibake markers
user-invocable: true
allowed-tools: Bash
---

# Validate Encoding

Run the encoding validator from the Arcana directory:

```bash
python3 rites/validate_encoding.py
```

For a grimoire:

```bash
python3 ARCANA_HOME/rites/validate_encoding.py --grimoire <path>
```
