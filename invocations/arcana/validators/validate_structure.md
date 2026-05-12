# 🔮 Invocation: Validate Arcana Structure

## ⚡ The Magical Boundary ⚡

This invocation validates Arcana itself (meta-knowledge).

## Purpose

Verify Arcana directory structure, required files, and organizational integrity.

## Invocation

```
/grm-arcana-validate
```

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
- ✅ All required directories found (docs, invocations/*, formulae, rites, resources, formulae/grimoire)
- ✅ All required files exist (INDEX.md, README.md, CHANGELOG.md, docs/*.md)
- ✅ All invocation directories have INDEX.md (invocations/grimoire/, invocations/arcana/, invocations/meta/)

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

- [ ] Each invocation category has INDEX.md with proper routing
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
❌ Missing file: INDEX.md
❌ Structure validation failed with 2 errors
```

## Related

- **Rite**: [rites/validate_structure.py](../../../rites/validate_structure.py)
- **Orchestrator**: [improve_arcana.md](../improve_arcana.md)
- **Reference**: [docs/operating_model.md](../../../docs/operating_model.md)

## Notes

This invocation runs a Python script that validates file system structure. It's fast (<1 second) and has no side effects (read-only).
