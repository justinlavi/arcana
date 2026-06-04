---
type: reference
title: "Validate Structure"
aliases: ["validate-structure-arcana"]
tags: [arcana/invocations, type/reference, scope/validators]
authority: grimoire
last_verified: 2026-05-12
---

# Invocation: Validate Arcana Structure

## Purpose

Verify Arcana directory structure, required files, and organizational integrity.

## Invocation

```
/arc-validate structure
```

To validate a **grimoire's** structure instead, use `/grm-validate structure` - that one operates on the active grimoire directory rather than on Arcana.

## When to Cast

- Before Arcana releases
- After adding new invocations/formulae/docs files
- During improve-arcana workflow (Phase 1)
- As part of pre-commit validation

## Workflow

### Step 1: Run Automation

Execute the validation rite:

```bash
python3 rites/validate_structure.py
```

### Step 2: Verify Output

**Expected**: All required directories and files present.

**Success indicators**:
- ✅ All required directories found (docs, invocations/*, formulae, rites, resources, skills, formulae/grimoire)
- ✅ All required files exist (the root hub, README.md, CHANGELOG.md, docs/*.md)
- ✅ All invocation family directories have a hub file (arcana, grimoire, agent, library, workspace, help, meta)
- ✅ Grimoire layers (`chapters/`, `sources/`, `inbox/`, `log.md`) exist in `formulae/grimoire/`, not at Arcana root

### Step 3: Handle Errors

If errors are found:

**Missing directories**:
1. Identify if intentionally removed or accidental deletion
2. Create with appropriate README if needed
3. Update documentation if structure changed

**Missing files**:
1. Check if file was renamed (e.g., old docs naming)
2. Verify file wasn't moved to different location
3. Recreate from template or git history if needed

### Step 4: Manual Checks

Additional verification not covered by automation:

- [ ] Each invocation category has a hub with proper routing
- [ ] formulae/grimoire/ contains complete starter grimoire
- [ ] resources/ contains icon assets and branding materials
- [ ] No unexpected directories or files (check for cruft)

## Outputs

**Console output**:
- List of required directories and their status
- List of required files and their status
- Exit code: 0 (success) or 1 (failures found)

**On success**:
```
✅ Structure validation passed
```

**On failure**:
```
❌ Missing directory: docs
❌ Missing file: <hub>.md
❌ Structure validation failed with 2 errors
```

## Related

- **Rite**: [rites/validate_structure.py](../../../rites/validate_structure.py)
- **Orchestrator**: [[invocations/arcana/improve_arcana|improve arcana]]
- **Reference**: [[docs/operating_model|operating model]]

## Notes

This invocation runs a Python script that validates file system structure. It's fast (<1 second) and has no side effects (read-only).
