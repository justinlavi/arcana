# 🔮 Invocation: Validate Arcana Links

## Purpose

Detect broken internal references and links in Arcana documentation.

## Invocation

```
/grm-arcana-validate-links
```

## When to Cast

- Before Arcana releases
- After renaming or moving files
- During improve-arcana workflow (Phase 4)
- After major documentation restructuring

## Workflow

### Step 1: Run Automation

Execute the validation rite:

```bash
python3 rites/validate_links.py
```

### Step 2: Review Broken Links

The rite scans all markdown files for links and verifies targets exist.

**Link types validated**:
- Relative file references: `[text](../file.md)`
- Relative directory references: `[text](folder/)`
- Intra-document anchors: `[text](#section)` (partial validation)

**Link types skipped**:
- External URLs: `https://`, `http://`, `mailto:`
- Named keys: `GRIMOIRE_ARCANA/`, `GRIMOIRE_{DOMAIN}/`
- Anchor-only links: `#section`

### Step 3: Fix Broken Links

For each broken link:

1. **Determine cause**:
   - File was renamed? Update link to new name
   - File was moved? Update path
   - File was deleted? Remove link or restore file
   - Typo in link? Correct spelling

2. **Update link**:
   ```markdown
   <!-- Before (broken) -->
   [quickstart](old_quickstart.md)

   <!-- After (fixed) -->
   [quickstart](quickstart.md)
   ```

3. **Verify fix**:
   ```bash
   python3 rites/validate_links.py
   ```

### Step 4: Update Cross-References

When fixing links, check for related cross-references:

**Example**: If you renamed a file:
1. Update direct links to the file
2. Update references in INDEX.md
3. Update "Related" sections in other invocations
4. Check breadcrumb trails in documentation

## Outputs

**Console output**:
- Broken links with source file location
- Link text and resolved path
- Exit code: 0 (clean) or 1 (broken links found)

**On success**:
```
✅ Link validation passed (no broken links found)
```

**On broken links**:
```
❌ Broken link in invocations/grimoire/create_chapter.md:
   Link: ../quickstart.md
   Resolved to: invocations/quickstart.md
❌ Link validation failed with 1 broken links
```

## Link Best Practices

### Prefer Relative Paths

**Within same directory**:
```markdown
[other invocation](create_grimoire.md)
```

**Parent directory**:
```markdown
[docs](../../docs/quickstart.md)
```

### Use Root Placeholders for Cross-Grimoire

**Arcana → Arcana**:
```markdown
[reference](GRIMOIRE_ARCANA/docs/reference.md)
```

**Arcana → Domain**:
```markdown
[chapter](olympus-grimoire/chapters/build_system/INDEX.md)
```

### Include File Extensions

**Always use .md extension**:
```markdown
✅ [file](path/file.md)
❌ [file](path/file)
```

### Avoid Absolute Paths

**Don't hardcode deployment paths**:
```markdown
❌ [file](/home/user/arcana/file.md)
✅ [file](../file.md)
✅ [file](GRIMOIRE_ARCANA/file.md)
```

## Troubleshooting

**False positives** (valid links reported as broken):
- Placeholder paths are automatically skipped
- Code example files are excluded (IMPLEMENTATION_PLAN.md, operating_model.md)
- If needed, add exclusion to rite script

**Links work but validation fails**:
- Check for typos in path
- Verify case sensitivity (file.md vs File.md)
- Ensure no spaces in filename

**Anchor links not validated**:
- Current implementation only validates file existence
- Anchor validation would require parsing headers (future enhancement)

## Related

- **Rite**: [rites/validate_links.py](../../../rites/validate_links.py)
- **Path conventions**: [docs/reference.md](../../../docs/reference.md#path-reference-convention)
- **Orchestrator**: [improve_arcana.md](../improve_arcana.md)

## Notes

**Exclusions**: The rite automatically skips:
- `IMPLEMENTATION_PLAN.md` (contains many code examples)
- `docs/operating_model.md` (has example link patterns)
- `invocations/arcana/validate_arcana_structure.md` (shows examples)

**Performance**: Moderate speed (3-5 seconds for entire Arcana)

**Path resolution**: Uses bash realpath for accurate path normalization
