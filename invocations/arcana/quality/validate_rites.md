# 🔮 Invocation: Validate Arcana Rites

## Purpose

Ensure rite scripts are functional, portable, maintainable, and follow best practices.

## Invocation

```
/grm-arcana-improve
```

## When to Cast

- After creating or modifying rite scripts
- During improve-arcana workflow (Phase 7.5)
- Before Arcana releases
- As part of quality audits
- When adding new automation

## Workflow

### Step 1: ShellCheck Validation

Run static analysis on all rite scripts:

```bash
# Install shellcheck if needed
# Ubuntu/Debian: sudo apt install shellcheck
# macOS: brew install shellcheck

# Run shellcheck on all rites
find rites/ -name "*.py" -exec shellcheck {} \;
```

**Common issues detected**:
- Unquoted variables
- Unused variables
- Incorrect array usage
- Missing error handling
- Portability problems
- Deprecated syntax

**Fix shellcheck warnings**:
```bash
# Before (unsafe)
file=$1
cat $file  # SC2086: Quote to prevent word splitting

# After (safe)
file="$1"
cat "$file"
```

### Step 2: Portability Check

Test scripts on multiple shells and platforms:

**Shells to test**:
- bash 4.x (older systems)
- bash 5.x (modern systems)
- zsh (macOS default, with bash compatibility)

**Test approach**:
```bash
# Test with different bash versions
bash --version
python3 rites/validate.py

# Test on different platforms
# - Linux (Ubuntu/Debian)
# - macOS
# - WSL (Windows Subsystem for Linux)
```

**Portability checklist**:
- [ ] Uses `#!/bin/bash` shebang (not `#!/bin/sh`)
- [ ] No bash 5.x-only features (unless documented)
- [ ] No GNU-specific flags (e.g., `grep -P` on macOS)
- [ ] Handles path differences (e.g., `/usr/bin` vs `/usr/local/bin`)
- [ ] Works with spaces in filenames

### Step 3: Error Handling Validation

Verify each rite has robust error handling:

**Required patterns**:
```bash
#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Error tracking
ERRORS=0

# Increment on error
if ! some_command; then
    echo "❌ Error message"
    ((ERRORS++))
fi

# Exit with appropriate code
if [[ $ERRORS -eq 0 ]]; then
    exit 0
else
    exit 1
fi
```

**Validation checks**:
- [ ] All rites use `set -euo pipefail`
- [ ] Error counter tracks issues
- [ ] Exit codes meaningful (0 = success, 1 = failure)
- [ ] Error messages descriptive
- [ ] No silent failures

**Audit command**:
```bash
# Find rites missing set -euo pipefail
find rites/ -name "*.py" -type f | while read -r script; do
    if ! grep -q "set -euo pipefail" "$script"; then
        echo "Missing: $script"
    fi
done
```

### Step 4: Documentation Check

Ensure each rite is self-documenting:

**Required documentation**:
```bash
#!/bin/bash
# rites/validate_example.sh
# [One-line description of purpose]
#
# Usage: bash rites/validate_example.sh [--flag]
# Exit codes: 0 = success, 1 = validation errors found
```

**Validation checks**:
- [ ] Header comment with purpose
- [ ] Usage example
- [ ] Exit code documentation
- [ ] Parameter descriptions (if any)
- [ ] Example output (in comments or related invocation)

**Documentation audit**:
```bash
# Find rites without proper headers
find rites/ -name "*.py" | while read -r script; do
    if ! head -5 "$script" | grep -q "^# Usage:"; then
        echo "Missing usage: $script"
    fi
done
```

### Step 5: Output Quality Review

Validate rite output is helpful and consistent:

**Output standards**:
- [ ] Clear success indicators (✅)
- [ ] Clear failure indicators (❌)
- [ ] Warnings distinguishable (⚠️)
- [ ] File paths relative to Arcana root
- [ ] Line numbers included for file issues
- [ ] Summary at end

**Example good output**:
```bash
🔮 Validating Arcana Structure
==================================

Checking required directories...
✅ Found: docs
❌ Missing: old_directory

==================================
❌ Validation failed with 1 errors
```

**Output anti-patterns**:
- Absolute paths (not portable)
- Cryptic error codes
- No summary
- Mixed success/failure indicators

### Step 6: Performance Check

Ensure rites run efficiently:

**Performance targets**:
- Individual rite: < 5 seconds
- validate.py: < 30 seconds
- No unnecessary file scans

**Measure performance**:
```bash
# Time individual rites
time python3 rites/validate_structure.py
time python3 rites/validate_semantics.py

# Profile to find bottlenecks
python3 rites/validate.py 2>&1 | grep -E '^\+'
```

**Optimization tips**:
- Minimize `find` commands (cache results)
- Use efficient grep patterns
- Avoid redundant file reads
- Parallelize independent checks

### Step 7: Integration Testing

Test rites work together:

**Test scenarios**:

1. **Clean Arcana** (should pass all):
   ```bash
   python3 rites/validate.py
   # Expected: All validations pass
   ```

2. **Intentional violations** (should detect):
   ```bash
   # Create test violations
   touch test-hyphen.md  # Naming violation

   python3 rites/validate_naming.py
   # Expected: Detects hyphenated filename

   # Cleanup
   rm test-hyphen.md
   ```

3. **Exclusion patterns** (should skip):
   ```bash
   # Verify exclusions work correctly
   python3 rites/validate_semantics.py
   # Should not flag deprecated terms in CHANGELOG.md
   ```

## Outputs

**Validation report**:
```
🔧 Rite Quality Report

ShellCheck:
✅ All rites passed shellcheck (0 warnings)

Portability:
✅ Tested on bash 4.4, 5.2, zsh 5.9
✅ No platform-specific commands

Error Handling:
✅ All rites use set -euo pipefail
✅ Consistent error counting
✅ Meaningful exit codes

Documentation:
✅ All rites have usage headers
✅ Exit codes documented
⚠️  1 rite missing example output

Output Quality:
✅ Consistent emoji indicators
✅ Relative file paths
✅ Clear summaries

Performance:
✅ Individual rites: 0.5-2.3 seconds
✅ validate.py: 12 seconds
✅ All under target thresholds

Integration:
✅ Clean Arcana passes all tests
✅ Intentional violations detected
✅ Exclusion patterns work correctly

Overall: A (95/100) - Production ready
```

## Rite Best Practices

### Structure Template

```bash
#!/bin/bash
# rites/validate_example.sh
# [One-line description]
#
# Usage: bash rites/validate_example.sh
# Exit codes: 0 = success, 1 = failures found

set -euo pipefail

ARCANA_ROOT="${GRIMOIRE_ARCANA:-$(cd "$(dirname "$0")/.." && pwd)}"
ERRORS=0

echo "🔮 Validating [Aspect]"
echo "=================================="
echo "Arcana root: $ARCANA_ROOT"
echo ""

# Validation logic
if ! validation_check; then
    echo "❌ Error description"
    ((ERRORS++))
fi

# Summary
echo ""
echo "=================================="
if [[ $ERRORS -eq 0 ]]; then
    echo "✅ Validation passed"
    exit 0
else
    echo "❌ Validation failed with $ERRORS errors"
    exit 1
fi
```

### Common Pitfalls

**Don't**:
- Use `eval` (command injection risk)
- Ignore shellcheck warnings
- Use platform-specific commands without fallback
- Print absolute paths
- Fail silently

**Do**:
- Quote all variables
- Use `set -euo pipefail`
- Test on multiple platforms
- Provide helpful error messages
- Document exit codes

## Related

- **Security**: [validate_security.md](../validators/validate_security.md)
- **All rites**: [rites/](../../../rites/)
- **Orchestrator**: [improve_arcana.md](../improve_arcana.md)

## Notes

**ShellCheck installation**: Not required for basic validation, but highly recommended for quality.

**Continuous improvement**: As new patterns emerge, update this invocation with best practices.
