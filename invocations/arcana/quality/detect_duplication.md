# 🔮 Invocation: Detect Arcana Duplication

## Purpose

Find duplicated content across Arcana to enforce DRY (Don't Repeat Yourself) principle.

## Invocation

```
/grm-arcana-improve
```

## When to Cast

- During improve-arcana workflow (Phase 6)
- After major documentation updates
- Before Arcana releases
- When content feels repetitive
- As part of quality audits

## Workflow

### Step 1: Scan for Semantic Duplication

Look for duplicated information across Arcana files:

**Critical duplications to detect**:
- Same file tree/directory structure shown in multiple docs
- Repeated explanations of the same concept
- Redundant lists (invocation catalogs, file lists, capability lists)
- Copy-pasted code examples
- Duplicated configuration examples
- Repeated section content

**Scan strategy**:
```bash
# Find duplicate lines (5+ words) across markdown files
find . -name "*.md" -exec cat {} \; | \
  grep -v '^#' | \
  sort | uniq -cd | sort -rn | head -20

# Find files with similar content
fdupes -r . --size --sameline
```

### Step 2: Analyze Each Duplication

For each duplicate found, determine:

1. **Is this intentional?**
   - Required for context in both locations?
   - Different audiences need same information?
   - Cross-reference would be confusing?

2. **Can it be consolidated?**
   - Move to one canonical location
   - Reference from other locations
   - Generate dynamically from single source

3. **What's the authoritative source?**
   - Which file should contain the canonical version?
   - What makes it authoritative (e.g., closest to source of truth)?

### Step 3: Common Duplication Patterns

#### Pattern 1: Static File Trees

**Problem**: Directory structure hardcoded in multiple docs

**Example violation**:
```markdown
<!-- In README.md -->
arcana/
├── docs/
├── invocations/
│   ├── grimoire/
│   ├── arcana/
│   └── meta/
└── rites/

<!-- In improve_arcana.md -->
arcana/
├── docs/
├── invocations/
│   ├── grimoire/
│   ├── arcana/
│   └── meta/
└── rites/
```

**Fix**: Single reference + dynamic discovery
```markdown
<!-- README.md - high-level only -->
See INDEX.md for complete structure.

<!-- improve_arcana.md - dynamic discovery -->
**Discovery approach**: This invocation dynamically discovers Arcana content
rather than hardcoding file lists.
```

#### Pattern 2: Duplicate Concept Explanations

**Problem**: Same concept explained in multiple files

**Example violation**:
- "What is a Grimoire?" explained in README.md AND docs/quickstart.md AND INDEX.md

**Fix**: Single canonical location with references
```markdown
<!-- README.md - brief -->
A Grimoire is a deterministic knowledge router.
See [operating model](docs/operating_model.md) for details.

<!-- docs/operating_model.md - canonical -->
[Full detailed explanation here]

<!-- Other files -->
[Link to operating_model.md instead of duplicating]
```

#### Pattern 3: Duplicate Lists

**Problem**: Invocation lists, file lists, or feature lists copied across files

**Example violation**:
- Invocation catalog in INDEX.md AND help.md AND improve_arcana.md

**Fix**: Dynamic generation or single source
```markdown
<!-- help.md - dynamic generation -->
Scans invocations/ directories and extracts metadata from invocation files

<!-- INDEX.md - thin router -->
Links to invocation files, doesn't duplicate their metadata

<!-- improve_arcana.md - references -->
"For invocation catalog, use /grm-help"
```

### Step 4: Apply DRY Fixes

For each duplication, apply appropriate fix:

**Fix Type 1: Remove Static Lists**
- Replace hardcoded file trees with dynamic discovery
- Use `find`, `ls`, or invocation-based enumeration
- Document discovery approach instead of listing files

**Fix Type 2: Consolidate Explanations**
- Keep explanation in one canonical location
- Add cross-references from other locations
- Use "See X for details" pattern

**Fix Type 3: Generate Dynamically**
- Invocation catalogs generated from invocation files
- Statistics calculated on-the-fly
- Configuration examples pulled from actual templates

**Fix Type 4: Replace with References**
```markdown
<!-- Before: Duplication -->
[Full repeated content]

<!-- After: Reference -->
See [canonical location](path/to/canonical.md#section)
```

### Step 5: Validate Anti-Drift Measures

Ensure fixes prevent future drift:

**Check for**:
- [ ] No hardcoded file/directory lists that will become stale
- [ ] Documentation references dynamic discovery where possible
- [ ] Invocation catalogs generated from actual invocation files
- [ ] Examples reference actual templates/formulae (not copies)
- [ ] Single source of truth clearly identified

**Anti-drift patterns**:
```markdown
✅ GOOD: "This invocation dynamically discovers..."
❌ BAD: "Current invocations: invocation1, invocation2, invocation3..."

✅ GOOD: "See formulae/ for templates"
❌ BAD: [Copy entire template into doc]

✅ GOOD: "Run /grm-help for current invocation list"
❌ BAD: [Hardcoded invocation catalog]
```

## Outputs

**Report format**:
```
🔍 Duplication Detection Report

Found 5 duplications:

1. File tree in README.md + improve_arcana.md
   - Lines: 23 duplicated lines
   - Fix: Remove from improve_arcana, reference README
   - Impact: Prevents drift on structure changes

2. "What is Grimoire" in 3 files
   - Locations: README.md, INDEX.md, quickstart.md
   - Fix: Consolidate to operating_model.md
   - Impact: Single source for concept definition

[etc...]

DRY Fixes Applied:
- Removed 2 static file trees (67 lines eliminated)
- Consolidated 3 duplicate explanations (128 lines → 42 lines)
- Replaced 1 hardcoded list with dynamic generation

Result: 153 duplicate lines eliminated, DRY principle enforced ✅
```

## DRY Principle

**Definition**: "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."

**Benefits**:
- Easier maintenance (update in one place)
- Prevents documentation drift
- Reduces confusion (one source of truth)
- Smaller codebase
- Faster updates

**Apply to**:
- Concept explanations
- Configuration examples
- Code snippets
- File structures
- Process descriptions

**Exceptions** (when duplication is acceptable):
- Different contexts require different framing
- Cross-references would be confusing
- Audiences are completely separate
- Performance requires local copy

## Related

- **Principle**: DRY (Don't Repeat Yourself)
- **Reference**: [docs/operating_model.md](../../../docs/operating_model.md#single-source-architecture)
- **Orchestrator**: [improve_arcana.md](../improve_arcana.md)

## Notes

**Manual process**: This invocation requires human judgment to identify semantic duplication. Future enhancement could include automated text similarity analysis.

**Balance**: Some repetition aids comprehension. Apply DRY to facts/data, not to pedagogical context.
