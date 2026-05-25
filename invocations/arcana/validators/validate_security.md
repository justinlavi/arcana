---
type: reference
title: "Validate Security"
aliases: ["validate-security"]
tags: [arcana/invocations, type/reference, scope/validators]
authority: grimoire
last_verified: 2026-05-12
---

# 🔮 Invocation: Validate Arcana Security

## Purpose

Security scanning for credentials, unsafe patterns, and shell script quality.

## Invocation

```
/arc-validate-security
```

## When to Cast

- Before Arcana releases
- After adding or modifying rite scripts
- During improve-arcana workflow
- Before committing sensitive changes
- As part of CI/CD pipeline

## Workflow

### Step 1: Run Automation

Execute the validation rite:

```bash
python3 rites/validate_security.py
```

### Step 2: Review Security Scans

The rite performs three types of security checks:

#### Credential Scanning

Scans for potential hardcoded credentials:
- Password patterns: `password = "value"`
- API key patterns: `api_key = "value"`
- Secret patterns: `secret = "value"`
- Token patterns: `token = "value"`
- Private keys: `BEGIN PRIVATE KEY`

#### Shell Script Safety (shellcheck)

If shellcheck is installed, validates:
- Syntax errors
- Common pitfalls
- Portability issues
- Quote handling
- Variable expansion

#### Bash Pattern Safety

Validates rite scripts use safe patterns:
- All scripts have `set -euo pipefail`
- No `eval` usage (command injection risk)
- Proper error handling

### Step 3: Handle Findings

For each security issue:

**Potential credential found**:
1. Verify if actual credential or false positive
2. If credential: Remove immediately, rotate credential
3. If false positive: Add to exclusion list if appropriate

**ShellCheck warning**:
1. Review warning context
2. Apply recommended fix
3. Re-run validation

**Unsafe bash pattern**:
1. Add `set -euo pipefail` to script header
2. Replace `eval` with safer alternative
3. Add proper error handling

## Outputs

**Console output**:
- Credential patterns found with locations
- ShellCheck results (if installed)
- Unsafe bash patterns
- Exit code: 0 (secure) or 1 (issues found)

**On success**:
```
✅ No potential credentials found
✅ All shell scripts passed shellcheck
✅ No unsafe bash patterns found
✅ Security validation passed
```

**On issues**:
```
❌ Found potential credential (pattern: api_key)
⚠️  Script missing 'set -euo pipefail': rites/new_script.sh
❌ Security validation failed with 2 issues
```

**Without shellcheck**:
```
⚠️  shellcheck not installed, skipping shell script validation
   Install with: sudo apt install shellcheck (Debian/Ubuntu)
              or: brew install shellcheck (macOS)
```

## Security Best Practices

### Never Commit Credentials

**Don't**:
```bash
API_KEY="sk-1234567890abcdef"  # ❌ Hardcoded credential
password="mypassword123"        # ❌ Hardcoded password
```

**Do**:
```bash
API_KEY="${API_KEY:-}"          # ✅ Read from environment
password="$(cat ~/.password)"   # ✅ Read from secure file
```

### Use Safe Bash Patterns

**Always start scripts with**:
```bash
#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures
```

**Avoid eval**:
```bash
# Don't
eval "$user_input"  # ❌ Command injection risk

# Do
case "$user_input" in
    allowed) do_something ;;
    *)       echo "Invalid" ;;
esac
```

### Quote Variables

```bash
# Unsafe
file=$1
cat $file  # ❌ Word splitting, glob expansion

# Safe
file="$1"
cat "$file"  # ✅ Properly quoted
```

## Installing ShellCheck

ShellCheck provides deep static analysis for shell scripts.

**Ubuntu/Debian**:
```bash
sudo apt install shellcheck
```

**macOS**:
```bash
brew install shellcheck
```

**Verify installation**:
```bash
shellcheck --version
```

## Troubleshooting

**False positive credential matches**:
- Rite scripts contain patterns to search for (intentional)
- These are automatically excluded from scanning
- IMPLEMENTATION_PLAN.md contains example patterns (excluded)

**ShellCheck false positives**:
- Review warning context
- Add `# shellcheck disable=SC####` comment if justified
- Document why the warning is suppressed

**Validation script itself flagged**:
- validate_security.py is automatically excluded from pattern matching
- Prevents self-referential false positives

## Related

- **Rite**: [rites/validate_security.py](../../../rites/validate_security.py)
- **Best practices**: [[docs/governance#security|governance]]
- **Orchestrator**: [[invocations/arcana/improve_arcana|improve arcana]]

## Notes

**Exclusions**: The rite automatically skips:
- `rites/` directory when scanning for credential patterns (contains search patterns)
- `validate_security.py` itself when checking unsafe bash patterns

**Limitations**:
- Pattern matching can have false positives
- Cannot detect all security issues (e.g., logic flaws)
- Complements, does not replace, code review

**Performance**: Fast scan (<2 seconds) plus shellcheck time if installed
