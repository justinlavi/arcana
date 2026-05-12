# 🔮 Invocation: Validate Arcana Naming

## Purpose

Enforce snake_case naming convention for Arcana files and directories.

## Invocation

```
/grm-arcana-improve
```

## When to Cast

- Before Arcana releases
- After creating new files
- During improve-arcana workflow (Phase 1)
- As part of pre-commit validation

## Workflow

### Step 1: Run Automation

Execute the validation rite:

```bash
python3 rites/validate_naming.py
```

### Step 2: Review Violations

The rite checks:

**Markdown files** (should be snake_case.md):
- ✅ Valid: `quick_start.md`, `operating_model.md`
- ❌ Invalid: `quick-start.md`, `quickStart.md`, `QuickStart.md`

**Python scripts** (should be snake_case.py):
- ✅ Valid: `validate_structure.py`, `validate.py`
- ❌ Invalid: `validate-structure.py`, `validateStructure.py`

**Allowed exceptions**:
- `README.md`, `CHANGELOG.md`, `INDEX.md`, `CLAUDE.md`, `LICENSE.md` (all caps)
- `IMPLEMENTATION_PLAN.md` (special planning documents)

### Step 3: Fix Violations

For each violation found:

1. **Rename file** to use snake_case:
   ```bash
   git mv file-name.md file_name.md
   ```

2. **Update all references** to the renamed file:
   - Search for old filename in markdown links
   - Update import/include statements
   - Fix cross-references in other docs

3. **Test links**:
   ```bash
   python3 rites/validate_links.py
   ```

### Step 4: Verify Consistency

Check that examples in documentation also use snake_case:
- Chapter names in examples: `chapters/example_chapter/`
- File references: `templates/example_template.md`
- Directory paths: `scripts/helper_scripts/`

## Outputs

**Console output**:
- Hyphenated filenames with paths
- CamelCase filenames with paths
- Exit code: 0 (compliant) or 1 (violations found)

**On success**:
```
✅ All markdown files use proper naming
✅ All shell scripts use proper naming
✅ Naming validation passed
```

**On violations**:
```
⚠️  Hyphenated filename (should use snake_case): invocations/grimoire/create-chapter.md
⚠️  CamelCase filename (should use snake_case): docs/quickStart.md
⚠️  Naming validation found 2 issues
```

## Naming Convention Rationale

**Why snake_case?**
1. **Consistency**: One standard across all Arcana files
2. **Readability**: Better for multi-word names (`operating_model.md` vs `operating-model.md`)
3. **URL-safe**: Works in web contexts without escaping
4. **Shell-friendly**: No escaping needed in bash scripts
5. **Python-aligned**: Matches Python module naming convention

**Why not kebab-case (hyphens)?**
- Inconsistent with Python imports
- Harder to double-click select in editors
- Can be confused with minus operator in some contexts

**Why not camelCase or PascalCase?**
- Case-sensitive filesystems create portability issues
- Harder to type (requires shift key)
- Less readable in CLI contexts

## Related

- **Rite**: [rites/validate_naming.py](../../../rites/validate_naming.py)
- **Reference**: [docs/reference.md](../../../docs/reference.md#naming-conventions)
- **Orchestrator**: [improve_arcana.md](../improve_arcana.md)

## Notes

**Git rename best practice**:
```bash
# Rename with git to preserve history
git mv old-name.md new_name.md

# Update references
grep -r "old-name.md" . --include="*.md"

# Commit rename separately from content changes
git commit -m "Rename: old-name.md → new_name.md (snake_case)"
```
