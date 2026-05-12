# 🔮 Invocation: Improve Arcana Documentation

## Purpose

Enhance clarity, completeness, and accessibility of Arcana documentation.

## Invocation

```
/grm-arcana-improve
```

## When to Cast

- During improve-arcana workflow (Phase 4)
- After user feedback about confusion
- Before major releases
- Quarterly quality reviews
- After adding new features

## Workflow

### Step 1: Readability Analysis

Review each documentation file for clarity:

**Check for**:
- [ ] Jargon without definitions
- [ ] Unclear pronouns ("it", "this", "that" without clear referent)
- [ ] Long, complex sentences
- [ ] Passive voice overuse
- [ ] Inconsistent terminology
- [ ] Missing context for examples

**Tools**:
```bash
# Find overly long lines (readability)
find . -name "*.md" -exec grep -l '.\{120,\}' {} \;

# Find common jargon terms
grep -rh '\b[A-Z][A-Z]+\b' --include="*.md" | sort | uniq -c | sort -rn
```

**Fixes**:
- Define jargon on first use
- Break long sentences
- Add concrete examples
- Use active voice
- Link to glossary/reference

### Step 2: Completeness Check

Ensure documentation covers all necessary topics:

**For reference docs**:
- [ ] All concepts have definitions
- [ ] All processes have workflows
- [ ] All terms in reference tables are used consistently
- [ ] Cross-references are bidirectional

**For invocation files**:
- [ ] Purpose is clear and specific
- [ ] Invocation shows exact command
- [ ] Workflow has actionable steps
- [ ] Outputs describe deliverables
- [ ] Related section links to dependencies

**For formulae**:
- [ ] Placeholders are documented
- [ ] Usage instructions included
- [ ] Examples show real-world usage

### Step 3: Navigation Audit

Verify documentation is discoverable and navigable:

**Entry points**:
- [ ] README.md provides clear overview
- [ ] INDEX.md routes to all major sections
- [ ] Each section links back to INDEX.md

**Cross-references**:
- [ ] Related documentation linked in each file
- [ ] Breadcrumb navigation present
- [ ] Deep links to specific sections

**Search-friendliness**:
- [ ] Headings use clear, searchable terms
- [ ] Synonyms included for discoverability
- [ ] Anchor links have descriptive names

**Audit commands**:
```bash
# Find files not linked from INDEX.md
comm -23 \
  <(find . -name "*.md" -not -name "INDEX.md" | sort) \
  <(grep -oP '(?<=\().*?\.md(?=\))' INDEX.md | sort)

# Find broken "Related" sections
grep -A 5 "## Related" **/*.md | grep "FIXME\|TODO\|TBD"
```

### Step 4: Beginner Experience Test

Test documentation from new user perspective:

**Quickstart validation**:
1. Can new user set up in stated time (10 minutes)?
2. Are prerequisites clearly listed?
3. Do all commands work as written?
4. Are error messages helpful?
5. Is first successful outcome clear?

**Progressive disclosure**:
- [ ] Simple path for beginners
- [ ] Deep dives available for advanced users
- [ ] Clear indicators of difficulty level
- [ ] Examples progress from simple → complex

**Common stumbling blocks**:
```bash
# Find steps without expected output
grep -A 2 "Step [0-9]:" **/*.md | grep -v "Expected:\|Output:\|Result:"

# Find commands without context
grep '```bash' -A 1 **/*.md | grep -v '^#'
```

### Step 5: Consistency Review

Ensure consistent voice, style, and structure:

**Voice**:
- [ ] Arcana docs use consistent tone (authoritative but friendly)
- [ ] Invocation docs use magical language appropriately
- [ ] Technical precision without unnecessary complexity

**Structure**:
- [ ] All invocations follow same section order
- [ ] All docs files use same heading levels
- [ ] All formulae have consistent format

**Terminology**:
- [ ] Use canonical terms from docs/reference.md
- [ ] Consistent capitalization (e.g., "Arcana" vs "arcana")
- [ ] Pronouns clearly refer to specific entities

**Automated checks**:
```bash
# Run semantic validation
python3 rites/validate_semantics.py

# Check consistent capitalization
grep -rn "arcana" --include="*.md" | \
  grep -v "Arcana"
```

### Step 6: Apply Improvements

For each documentation issue:

**Clarity issues**:
1. Rewrite unclear sentences
2. Add examples where abstract
3. Define jargon inline or link to reference

**Completeness gaps**:
1. Add missing sections
2. Expand terse explanations
3. Include edge cases and gotchas

**Navigation problems**:
1. Add cross-references
2. Create breadcrumb links
3. Improve INDEX.md routing

**Inconsistencies**:
1. Standardize terminology
2. Unify section structure
3. Align voice and tone

## Documentation Quality Scorecard

Grade documentation on these dimensions:

**Clarity** (A-F):
- Clear language, well-defined terms, concrete examples
- Grade: A = crystal clear, F = confusing

**Completeness** (A-F):
- All necessary information present, no gaps
- Grade: A = comprehensive, F = missing critical info

**Accessibility** (A-F):
- Easy to find, good navigation, clear entry points
- Grade: A = highly discoverable, F = hidden/hard to navigate

**Consistency** (A-F):
- Uniform style, tone, structure, terminology
- Grade: A = perfectly consistent, F = contradictory

**Maintainability** (A-F):
- DRY principle, single source of truth, anti-drift
- Grade: A = self-maintaining, F = requires constant updates

**Example scorecard**:
```
📊 Documentation Quality Report

docs/quickstart.md:
  Clarity: A (95/100) - Clear, actionable steps
  Completeness: B (82/100) - Missing troubleshooting for macOS
  Accessibility: A (90/100) - Excellent navigation
  Consistency: A (95/100) - Matches style guide
  Maintainability: B (85/100) - Some hardcoded paths
  Overall: A- (89/100)

[Scores for all files...]

Arcana Average: A- (88/100)
```

## Outputs

**Improvements report**:
```
📝 Documentation Improvement Summary

Files Updated: 8

Clarity Enhancements:
- Rewrote 12 unclear sentences
- Added 7 concrete examples
- Defined 5 jargon terms inline

Completeness Additions:
- Added troubleshooting to 3 files
- Expanded 4 terse sections
- Documented 6 edge cases

Navigation Improvements:
- Added 15 cross-references
- Created breadcrumb links in 6 files
- Updated INDEX.md routing

Consistency Fixes:
- Standardized 23 terminology uses
- Unified section structure in 5 files
- Aligned voice in reference docs

Quality Score: B+ (87/100) → A- (91/100) [+4 points]
```

## Related

- **Validation**: [validate_semantics.md](../validators/validate_semantics.md)
- **Reference**: [docs/reference.md](../../../docs/reference.md)
- **DRY**: [detect_duplication.md](detect_duplication.md)
- **Orchestrator**: [improve_arcana.md](../improve_arcana.md)

## Notes

**Subjective judgment**: Documentation quality requires human assessment. Automated checks complement but don't replace editorial review.

**Iterative improvement**: Documentation is never "done". Continuous refinement based on user feedback.
