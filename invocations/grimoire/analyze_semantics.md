# 📊 Invocation: Analyze Semantic Clarity

## ⚡ Purpose

**AI-powered** deep semantic analysis of naming and organization to maximize discoverability, token efficiency, and human comprehension.

This invocation uses **AI intelligence** (not scripts) to:
- Understand context and meaning of terminology
- Detect subtle semantic issues scripts can't find
- Suggest improvements based on judgment, not just patterns
- Analyze against reference documentation (reference.md)
- Evolve recommendations as AI capabilities expand

**Architecture Note**: This invocation follows the **Script vs AI Intelligence** principle (see [docs/script_vs_ai.md](../../docs/script_vs_ai.md)). Rites extract data (find, count, extract), AI analyzes meaning and suggests improvements.

### What This Invocation Evaluates:
- Chapter and file name clarity **in context**
- Terminology consistency against reference docs
- Searchability and discoverability
- AI token efficiency predictions
- Human comprehension metrics
- Renaming opportunities with impact analysis

**This invocation is safe to rerun at any time.**

---

## Preconditions

Before executing, verify the current working directory is a registered domain grimoire (check `~/grimoire/catalog.json`). If it is not, list available grimoires and tell the user to `cd` to one. Arcana is not a grimoire. **Stop** if the check fails.

---

## When to Cast

- Creating new chapters (validate naming before committing)
- After major refactoring or reorganization
- When users report difficulty finding knowledge
- Quarterly as part of grimoire quality review
- When AI agents seem confused about routing

---

## Invocation

From your grimoire directory (e.g., `olympus-grimoire/`), cast:

```
/grm-domain-analyze-semantics
```

Or for Arcana:

```
/grm-domain-analyze-semantics --arcana
```

---

## What This Invocation Does

### Phase 1: Naming Clarity Analysis

**Evaluates each chapter/file name on multiple dimensions:**

1. **Specificity Score** (0-100)
   - Too vague: "misc", "other", "stuff" → Low score
   - Too specific: "cmake-3-28-5-workaround" → Medium score
   - Just right: "build_system", "cmake-overrides" → High score

2. **Searchability Score** (0-100)
   - Contains common search terms?
   - Matches domain vocabulary?
   - Findable from index?

3. **Comprehension Score** (0-100)
   - Self-explanatory without context?
   - Technical jargon level appropriate?
   - Abbreviation clarity?

4. **Token Efficiency** (tokens/knowledge ratio)
   - Name length vs knowledge contained
   - Router hop count to reach
   - Predicted AI read cost

**Scoring Rubric:**

| Range | Grade | Interpretation |
|-------|-------|----------------|
| 90-100 | A+ | Exceptional - best practice example |
| 80-89 | A | Excellent - no changes needed |
| 70-79 | B | Good - minor improvements possible |
| 60-69 | C | Acceptable - consider renaming |
| 50-59 | D | Poor - should rename |
| 0-49 | F | Critical - must rename |

---

### Phase 2: Terminology Consistency

**Detects terminology drift and inconsistencies:**

1. **Synonym Detection**
   - "config" vs "configuration" (pick one)
   - "repo" vs "repository"
   - "doc" vs "document"

2. **Abbreviation Consistency**
   - "cmake" vs "CMake" vs "CMAKE"
   - "cpp" vs "c++" vs "C++"

3. **Naming Pattern Consistency**
   - Hyphenated: "build_system", "repo_structure"
   - Underscored: "cmake_overrides", "cpp_formatting"
   - Camel case: "BuildSystem" (avoid in file names)

4. **Terminology Registry**
   - Extract canonical terms from grimoire
   - Build synonym map
   - Flag inconsistent usage

---

### Phase 3: Discoverability Analysis

**Measures how easily knowledge can be found:**

1. **Search Term Coverage**
   - Common queries: "How to build", "CMake config", "coding standards"
   - Are these terms in chapter names?
   - Are they in router routes?

2. **Entry Point Analysis**
   - How many ways to reach critical knowledge?
   - Single point of failure (only one route)?
   - Redundant cross-references?

3. **Orphan Knowledge**
   - Knowledge that exists but isn't discoverable
   - Missing from routers
   - Not cross-referenced

4. **Hot Path Identification**
   - Which chapters get accessed most?
   - Should they be promoted higher?

---

### Phase 4: Structure Assessment

**Evaluates organizational clarity:**

1. **Hierarchy Depth**
   - Optimal: 2-3 levels (root → chapter → page)
   - Deep: 4+ levels (hard to navigate)
   - Flat: Everything at root (overwhelming)

2. **Chapter Balance**
   - Size distribution across chapters
   - Detect bloated chapters (should split)
   - Detect tiny chapters (should merge)

3. **Sub-chapter Sprawl**
   - Too many sub-chapters (>8)?
   - Consider flattening or reorganizing

4. **Naming Hierarchy**
   - Are parent/child names logically related?
   - Example: `code/cpp/formatting` ✅
   - Example: `build/config/stuff` ❌

---

### Phase 5: AI Token Efficiency

**Predicts AI agent read efficiency:**

1. **Average Read Path Length**
   - Count hops from root to knowledge
   - Ideal: <2.5 hops
   - Acceptable: 2.5-3.5 hops
   - Poor: >3.5 hops

2. **Router Token Cost**
   - Tokens per router (word count × 1.3)
   - Total tokens to navigate typical request
   - Optimization opportunities

3. **Name Token Cost**
   - Long names = more tokens
   - Predict cumulative cost across grimoire

4. **Cross-Reference Load**
   - Too many "Related Chapters" links?
   - Increases cognitive load

---

### Phase 6: Recommendations

**Generates prioritized renaming and restructuring suggestions:**

1. **Critical Renames** (Score <50)
   - Must fix for clarity
   - High impact on discoverability

2. **Suggested Renames** (Score 50-69)
   - Moderate improvement opportunity
   - Lower priority

3. **Terminology Standardization**
   - Pick canonical term for synonyms
   - Apply consistently across grimoire

4. **Structure Improvements**
   - Split bloated chapters
   - Merge tiny chapters
   - Flatten over-nested hierarchies

5. **Impact Analysis**
   - Show what breaks if renamed
   - Estimate effort to apply
   - Predict quality improvement

---

## Deliverables

### 1. Semantic Analysis Report

Contains:
- **Overall Scores**: Aggregate grade (A-F) for naming clarity, terminology consistency, discoverability, structure quality, and token efficiency
- **Chapter Scores**: Top and bottom 5 chapters by semantic quality score
- **Terminology Inconsistencies**: Conflicting terms with recommended canonical form
- **Critical Renames** (Score <50): Must-fix items with current/proposed names, impact, effort, and quality gain
- **Suggested Improvements** (Score 50-69): Lower priority renames with the same detail
- **Structure Recommendations**: Chapters to split (bloated) or merge (tiny)

---

### 2. Quick Wins List

High-impact, low-effort changes that can be applied immediately. Each item includes estimated time, quality point gain, and file count.

---

### 3. Terminology Registry

Machine-readable JSON mapping canonical terms, abbreviations, and chapter name scores for automated consistency checking.

---

## Scoring Methodology

- **Specificity**: Penalizes vague names ("misc", "other", "stuff"); rewards domain-specific, self-documenting compound names
- **Searchability**: Evaluates term match with common queries, index presence, cross-reference coverage, and synonym discoverability
- **Token Efficiency**: Ratio of token cost (name length + router hops) to knowledge value (unique concepts); lower cost per concept is better

---

## Common Semantic Issues

### Issue: Vague Chapter Names

**Before**:
- `chapters/misc/`
- `chapters/other/`
- `chapters/stuff/`

**After**:
- `chapters/utilities/` (if helper tools)
- `chapters/experimental/` (if in-progress work)
- `chapters/archived/` (if legacy content)

---

### Issue: Inconsistent Terminology

**Before**:
```
chapters/config/
chapters/configuration_mgmt/
chapters/configure_tools/
```

**After**:
```
chapters/config/
chapters/config_management/
chapters/config_tools/
```

---

### Issue: Overly Deep Nesting

**Before**:
```
chapters/code/languages/cpp/patterns/modern/smart_pointers/unique_ptr.md
```
(7 levels deep)

**After**:
```
chapters/cpp_patterns/smart_pointers.md
```
(3 levels deep)

---

### Issue: Ambiguous Abbreviations

**Before**:
- `ms_sw/` - What does "ms" mean? Microsoft? Mission Support? Milliseconds?

**After**:
- `mission-support-sw/` - Clear and unambiguous
- Or add README.md explaining abbreviation

---

## Integration with Other Invocations

This invocation is automatically invoked by:

- `/grm-domain-improve` - Includes semantic analysis in Phase 2.5
- `/grm-arcana-improve` - Analyzes formula templates and invocation names

Can be run standalone for deeper analysis:

- `/grm-domain-analyze-semantics` - Full semantic audit
- `/grm-domain-analyze-semantics --quick` - Quick wins only
- `/grm-domain-analyze-semantics --chapter=build_system` - Single chapter

---

## Quality Gates

Before publishing semantic recommendations:

✅ **All scores validated** - No false negatives/positives
✅ **Rename impact analyzed** - Know what breaks
✅ **Effort estimates realistic** - Based on file counts
✅ **Alternative names suggested** - Multiple options
✅ **Terminology conflicts resolved** - Pick canonical terms

---

## Tips

### When to Apply Recommendations

**Always apply**:
- Critical renames (score <50)
- Terminology standardization
- Quick wins (<30 min effort)

**Consider carefully**:
- Structure refactoring (>2 hours effort)
- Renames affecting >10 files
- Changes to stable, well-known chapter names

**Defer or reject**:
- Cosmetic improvements (<10 quality points)
- Changes conflicting with project conventions
- Renames during active development sprints

### Semantic Best Practices

1. **Chapter names should be nouns or noun phrases**
   - ✅ "build_system", "code-standards"
   - ❌ "building", "how-to-code"

2. **Use technical domain vocabulary**
   - ✅ "cmake-overrides", "toolchain-config"
   - ❌ "build-file-tweaks", "compiler-stuff"

3. **Avoid temporal or version-specific names**
   - ❌ "new-build_system", "cmake-v3-28"
   - ✅ "build_system", "cmake-overrides"

4. **Prefer clarity over brevity**
   - ✅ "platform-operations" (clear)
   - ❌ "plat-ops" (unclear abbreviation)

---

## Related Invocations

- Validate quality gates: `/grm-arcana-validate-boundaries`
- Apply structure changes: `/grm-domain-improve`
- Optimize routing: `/grm-domain-improve`
- Full grimoire improvement: `/grm-domain-improve`

