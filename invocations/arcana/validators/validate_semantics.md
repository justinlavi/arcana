# 🔮 Invocation: Validate Arcana Semantics

## ⚡ The Magical Boundary ⚡

This invocation validates Arcana's terminology against the canonical reference.

## Purpose

Reference-driven terminology validation against [docs/reference.md](../../../docs/reference.md) as single source of truth.

## Invocation

```
/grm-arcana-improve
```

## When to Cast

- Before Arcana releases
- After terminology updates
- During improve-arcana workflow (Phase 5)
- After updating docs/reference.md
- When adding or modifying documentation

## Workflow

### Step 1: Extract Canonical Terms

The rite automatically reads `docs/reference.md` and extracts canonical terms from:
- **Core Concepts table** → valid magical terms (Grimoire, Chapter, Invocation, Formula, Rite)
- **Commands & Triggers table** → valid command patterns

### Step 2: Run Automation

Execute the validation rite:

```bash
python3 rites/validate_semantics.py
```

### Step 3: Review Violations

The rite scans all Arcana markdown files for:

**Deprecated terms** (should no longer appear):
- "The Keepers" (replaced by "Arcana maintainer")
- "Archmage" (replaced by "Arcana maintainer")
- "Domain Master" / "Elder Mage" (replaced by "domain lead")
- "Apprentice" / "Scribe" / "Mage" (replaced by "user" or "contributor")
- "tome" (replaced by "grimoire")

**Hyphenated examples** (should use snake_case):
- `chapters/example-name/` → `chapters/example_name/`
- `file-name.md` → `file_name.md`

### Step 4: Apply Fixes

For each violation found:

1. **Determine context**:
   - Is this a code example? Update to snake_case
   - Is this deprecated terminology? Replace with canonical term from reference
   - Is this in CHANGELOG.md documenting history? May be acceptable

2. **Replace with canonical term**:
   - Use exact term from docs/reference.md
   - Maintain grammatical context (capitalization, plurality)

3. **Verify consistency**:
   - Check surrounding text for similar issues
   - Update related documentation if needed

### Step 5: Update Reference (if needed)

If you discover a new term that should be canonical:

1. Add to appropriate table in `docs/reference.md`
2. Document why this term is canonical
3. Re-run validation to ensure consistency

## Outputs

**Console output**:
- Deprecated terms found with file locations
- Hyphenated examples with line numbers
- Exit code: 0 (clean) or 1 (issues found)

**On success**:
```
✅ No deprecated terms found
✅ No hyphenated examples found
✅ Semantic validation passed
```

**On issues found**:
```
⚠️  Found deprecated term 'The Keepers' in: invocations/arcana/improve_arcana.md
⚠️  Found hyphenated example in: invocations/grimoire/create_chapter.md
⚠️  Semantic validation found 2 issues
```

## Reference-Driven Architecture

This invocation implements single-source-of-truth pattern:

**Canonical source**: `docs/reference.md`
- All valid terms defined in tables
- No hardcoded patterns in validation rite
- Easy to extend (just update reference tables)

**Validation process**:
1. Read reference tables
2. Extract canonical terms
3. Compare all Arcana content against canonical list
4. Report deviations

**Benefits**:
- ✅ Zero duplication (terms defined once)
- ✅ Self-maintaining (new terms auto-validated)
- ✅ Drift-proof (impossible to have outdated patterns)

## Related

- **Rite**: [rites/validate_semantics.py](../../../rites/validate_semantics.py)
- **Reference**: [docs/reference.md](../../../docs/reference.md) (single source of truth)
- **Orchestrator**: [improve_arcana.md](../improve_arcana.md)

## Notes

**Exclusions**: The rite automatically skips:
- `CHANGELOG.md` (may document historical terms)
- `IMPLEMENTATION_PLAN.md` (contains example patterns)
- Files documenting deprecated patterns for validation purposes

**Performance**: Fast scan (<2 seconds for entire Arcana)
