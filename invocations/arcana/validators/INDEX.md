# Core Arcana Validation Invocations

These invocations provide modular, focused validation of Arcana components.

## Purpose

Validator invocations can be run independently or orchestrated through [improve_arcana.md](../improve_arcana.md). Each invocation wraps a corresponding validation rite.

## Available Invocations

### Structure & Organization
- **[validate_structure.md](validate_structure.md)** - Directory/file integrity validation
- **[validate_naming.md](validate_naming.md)** - Snake_case naming enforcement
- **[validate_format.md](validate_format.md)** - Invocation/formula schema compliance

### Content Quality
- **[validate_semantics.md](validate_semantics.md)** - Reference-driven terminology validation
- **[validate_links.md](validate_links.md)** - Broken reference detection

### Security
- **[validate_security.md](validate_security.md)** - Credential scanning and bash safety

## Quick Start

**Run all validations**:
```bash
python3 rites/validate.py
```

**Run individual validation**:
```bash
python3 rites/validate_structure.py
```

**Invoke** (AI-guided):
```
/grm-arcana-validate
/grm-arcana-improve
/grm-arcana-improve
/grm-arcana-improve
/grm-arcana-improve
/grm-arcana-improve
```

## Architecture

Each validation invocation follows this pattern:

1. **Invocation file** (`validate_*.md`) - User-facing documentation, workflow guidance
2. **Rite script** (`rites/validate_*.py`) - Automated validation logic
3. **Reference** (`docs/reference.md`) - Canonical definitions (for semantic validation)

**Benefits**:
- Invocations provide context and guidance
- Rites provide automation and speed
- Reference provides single source of truth

## Usage Patterns

### During Development
Invoke individual validations for specific changes:
```
/grm-arcana-improve    # After renaming files
/grm-arcana-improve   # After creating new invocation
/grm-arcana-improve # Before committing
```

### Before Release
Run comprehensive validation:
```bash
python3 rites/validate.py
```

### In CI/CD
Integrate into pipeline:
```yaml
- name: Validate Arcana
  run: python3 rites/validate.py
```

## Related

- **Orchestrator**: [improve_arcana.md](../improve_arcana.md)
- **Rites**: [rites/](../../../rites/)
- **Reference**: [docs/reference.md](../../../docs/reference.md)
