---
name: {{NAMESPACE}}-arcana-validate-security
description: Mechanically scan Arcana for credential patterns and unsafe Python constructs
user-invocable: true
allowed-tools: Bash Read
---

# Validate Arcana Security

You are running the security validator against the Arcana repository. It scans for committed credentials and unsafe Python constructs (`eval`, `exec`, etc.) in rites.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_security.py
```

Report findings with file:line citations. Exit code 0 means clean; non-zero means at least one finding.

This is a mechanical pattern scan, not a full security audit. For comprehensive review use the `security-review` skill.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_security.md`
