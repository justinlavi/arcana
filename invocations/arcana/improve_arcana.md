# 🪄 Invocation: Improve Arcana

## ⚡ Purpose

**For the Arcana maintainer only** - Continuously improve Arcana to ensure it remains the universal foundation for all grimoires.

This invocation maintains the quality of:
- Universal invocations
- Universal formulae
- Universal rites
- Reference documentation
- The grimoire template

**This invocation is safe to rerun at any time.**

---

## ⚡ The Magical Boundary ⚡

**This invocation maintains Arcana's magical integrity:**

### Magical Language Throughout
- This invocation operates entirely within the magical realm of Arcana
- All improvements maintain wizardly language and thematic consistency
- Invocations, formulae, and rites are ONLY in Arcana (never in domain grimoires)

### Quality Standards for Universal Magic
- Ensures all invocations have proper magical boundary sections
- Validates that examples use generic names (Domain A, Knowledge Domain)
- Confirms no platform assumptions (Slack → domain communication)
- Maintains the magical/practical boundary in all documentation

---

## When to Cast

- Arcana documentation feels cluttered
- Invocations have accumulated technical debt
- Formulae need updating for new patterns
- Reference docs are out of sync
- Major version update is being prepared

---

## Invocation

From the Arcana directory, cast:

```
/grm-arcana-improve
```

Only the Arcana maintainer should run this invocation.

---

## What This Invocation Does

**Quick Start - Run All Validations**:
```bash
python3 rites/validate.py              # sequential (default)
python3 rites/validate.py --parallel   # parallel execution
python3 rites/validate.py --summary    # summary-only output
```

For detailed phase-by-phase workflow, continue below:

---

### Phase 1: Inventory & Health Check
1. Enumerate all Arcana components:
   - INDEX.md, README.md (entry points)
   - invocations/grimoire/*.md, invocations/arcana/*.md (universal workflows)
   - formulae/*.md (universal templates)
   - rites/*.py (universal automation)
   - docs/*.md (reference docs)
   - formulae/grimoire/ (the master template)
   - resources/ (branding assets)

2. Validate internal consistency:
   - All invocations reference correct paths (invocations/grimoire/, invocations/arcana/)
   - All formulae use current placeholder convention
   - All reference docs are cross-referenced properly
   - Grimoire-template matches latest best practices
   - Documentation structure matches actual file system

3. Detect documentation drift:
   - **Critical**: README.md directory structure vs actual filesystem
   - **Critical**: INDEX.md invocation paths match actual subdirectories
   - Broken internal links
   - Outdated examples in invocations (old paths, old structure)
   - Invocation references without subdirectories (invocations/*.md → invocations/grimoire/*.md)
   - Chronicle references to flat structure (*.md → YYYY-MM-DD/*.md)
   - Placeholder drift in formulae
   - Version number inconsistencies
   - Date mismatches (Last Updated fields)
   - Missing cross-references

3a. **Detect semantic clarity issues**:
   - **Critical**: Redundant phrasing (Grimoire Grimoire, grimoire grimoire, grimoire of Grimoire)
   - **Critical**: Old terminology still present (tome/tomes when should be grimoire/grimoires)
   - **Critical**: Ambiguous "Grimoire" references (should specify "Arcana" or "grimoire")
   - Directory names in docs that don't match actual structure
   - Unclear ownership phrasing (needs "domain's grimoire" not "grimoire of Grimoire")
   - Confusing headers (avoid redundancy like "Grimoire - X Grimoire")

**Automation**: Run `validate_structure.py` and `validate_naming.py` (via `validate.py`).

**Manual review**: Review output for structural issues, verify required files exist, check naming compliance.

**Checkpoint**: Reports findings before making any changes

### Phase 2: Invocation Quality Review
4. Review each invocation for:
   - Clear invocation instructions
   - Up-to-date workflow steps
   - Correct file paths and references
   - Magical boundary compliance
   - Examples that match current structure

5. Ensure invocation consistency:
   - All invocations follow the same format
   - Common sections across all invocations
   - Consistent magical language usage

**Automation**: Run `validate_format.py` (via `validate.py`).

**Manual review**: Review invocation sections for completeness, check magical boundary compliance, verify workflow clarity.

### Phase 3: Formula & Template Updates
6. Review formulae for:
   - Current placeholder naming ({{DOMAIN_*}}, {{GRIMOIRE_*}})
   - Magical boundary compliance
   - Practical folder name examples

7. Audit formulae/grimoire:
   - Matches latest best practices
   - All placeholders defined
   - README and INDEX are exemplary
   - chapters/ structure is clean

**Automation**: Run `validate_format.py` (via `validate.py`).

**Manual review**: Check placeholder consistency, verify formula templates are up-to-date, ensure formulae/grimoire matches current patterns.

### Phase 4: Documentation Coherence
8. Review reference docs:
   - quickstart.md is accurate for new users
   - agent_configuration.md reflects current setup patterns
   - operating_model.md reflects current routing patterns
   - governance.md matches actual practices
   - reference.md has all current terminology and conventions
   - CHANGELOG.md (at root) is up to date

9. Ensure cross-references:
   - INDEX.md points to all major sections
   - README.md provides clear navigation
   - All docs link to related content correctly

**Automation**: Run `validate_links.py` (via `validate.py`).

**Manual review**: Check for broken internal references, verify cross-document navigation, ensure reference doc cross-links are correct.

### Phase 5: Semantic Analysis ✨

**Following Script vs AI Intelligence Principle** (see [docs/script_vs_ai.md](../../docs/script_vs_ai.md)):

10. **Rite extracts data** (simple, fast):
    ```bash
    python3 rites/validate_semantics.py
    # Extracts canonical terminology from reference.md
    # Reports mechanical pattern violations
    # Creates: rites/completed/canonical_terminology.txt
    ```

11. **AI analyzes semantics intelligently** (contextual, adaptive):
    - Cast `/grm-domain-analyze-semantics --arcana` invocation
    - AI reads extracted terminology data
    - AI reads docs/reference.md (single source of truth)
    - AI analyzes all Arcana files **with context understanding**:
      - Is this term used appropriately in this context?
      - Does this phrasing align with reference definitions?
      - Are placeholders used correctly for this use case?
      - Is the magical/practical boundary respected here?
    - AI makes **judgment calls** scripts can't:
      - Should this be renamed? (not just "is it wrong")
      - Is this clear enough? (not just "does it match pattern")
      - Would consolidation improve quality? (not just "is it duplicate")
    - AI suggests specific improvements with reasoning

12. **Why this split?**
    - **Scripts extract facts**: Find terms, count usage, check patterns
    - **AI understands meaning**: Analyze context, suggest improvements, explain why
    - **Scripts stay simple forever**: Find, count, extract
    - **AI gets smarter over time**: As AI evolves, this analysis improves automatically

**Manual review**:
- Review AI's semantic analysis and suggestions
- Apply improvements that make sense for Arcana
- Document any new patterns discovered

**Checkpoint**: Report semantic analysis findings and improvements applied

### Phase 6: Duplication Detection & DRY Enforcement ✨
12. Scan for duplicate information across Arcana:
    - **Critical**: Detect duplicate file trees/directory structures in multiple docs
    - **Critical**: Find duplicated explanations of same concepts
    - **Critical**: Identify redundant lists (invocation catalogs, file lists, capability lists)
    - Detect copy-pasted code examples that should be in one canonical location
    - Find duplicated configuration examples
    - Identify repeated section content across multiple files

13. Apply DRY (Don't Repeat Yourself) fixes:
    - **Remove static file trees** - Replace with dynamic discovery or single reference
    - **Consolidate duplicate explanations** - Keep in one canonical location, reference elsewhere
    - **Eliminate duplicate lists** - Generate dynamically or maintain single source
    - **Replace with references** - Use links to canonical source instead of copying
    - **Document canonical locations** - Make clear where authoritative content lives
    - **Prefer composition over duplication** - Link to existing docs rather than repeating

14. Validate anti-drift measures:
    - Ensure no hardcoded file/directory lists that will become stale
    - Verify documentation references dynamic discovery where possible
    - Confirm invocation catalogs are generated from actual invocation files
    - Check that examples reference actual templates/formulae rather than duplicating them

**Checkpoint**: Report duplications found and DRY fixes applied

### Phase 7: Path Reference Validation ✨
15. Scan for improper path references:
    - **Critical**: Detect relative cross-grimoire paths (`../arcana/`, `../olympus-grimoire/`)
    - **Critical**: Find stale doc references (old paths)
    - Find absolute filesystem paths that should be placeholders
    - Identify hardcoded deployment-specific paths

16. Apply path reference fixes:
    - **Replace relative cross-grimoire paths** - Use `GRIMOIRE_ARCANA/` and `GRIMOIRE_{DOMAIN}/`
    - **Update doc references to use docs/ paths
    - **Convert hardcoded paths to placeholders** - Make deployment-agnostic
    - **Document path conventions** - Ensure `docs/reference.md` documents the system

17. Validate path reference standards:
    - Ensure no relative paths (`../`) crossing grimoire boundaries
    - Verify all docs/ files are correctly named
    - Confirm all cross-grimoire references use root placeholders
    - Check that path placeholders are documented in reference.md

**Automation**: Run `validate_naming.py` and `validate_links.py` (via `validate.py`).

**Manual review**: Check for deployment-specific paths, verify placeholder usage consistency, ensure docs/ file naming is correct.

**Checkpoint**: Report path issues found and fixes applied

### Phase 7.5: Security Validation ✨

**New Phase**: Security scanning for credentials and unsafe patterns

**Automation**: Run `validate_security.py` (via `validate.py`).

**Manual review**: Review credential pattern matches, check shell script safety (`set -euo pipefail`), verify no `eval` usage in rites.

### Phase 8: Version Preparation
18. Prepare for version updates:
    - Check semantic versioning compliance
    - Update CHANGELOG.md if needed
    - Ensure breaking changes are documented
    - Update version numbers consistently

### Phase 9: Invocation Effectiveness Tracking ✨
19. Measure invocation performance across domains:
    - Track invocation usage frequency
    - Measure success rates (issues found/fixed)
    - Analyze invocation execution times
    - Identify pain points and friction
    - Compare invocation effectiveness across grimoires

20. Evolve invocation system:
    - Recommend new invocations based on patterns
    - Deprecate ineffective invocations
    - Optimize slow-performing invocations
    - Update invocation documentation based on usage

**Checkpoint**: Report invocation metrics and evolution recommendations

---

## Non-Negotiable Rules

1. **Universal only** - Arcana contains ZERO domain-specific content
2. **Backward compatibility** - Don't break existing domain grimoires
3. **Clear examples** - Use generic examples (Domain A, Knowledge Domain)
4. **No platform assumptions** - Generic "domain communication", not "Slack"
5. **Magical boundary** - Invocations/formulae/rites ONLY in Arcana, never in grimoires
6. **Version discipline** - Follow semantic versioning strictly

---

## Scope

This invocation audits only Arcana itself.

**Discovery approach**: This invocation dynamically discovers Arcana content rather than hardcoding file lists. It scans:
- Root documentation: `INDEX.md`, `README.md`, `CHANGELOG.md`
- Reference docs: `docs/quickstart.md`, `docs/operating_model.md`, etc.
- Universal invocations: `invocations/grimoire/*.md`, `invocations/arcana/*.md`, `invocations/meta/*.md`
- Universal formulae: `formulae/*.formula.md`
- Universal rites: `rites/*.py`
- Template: `formulae/grimoire/`
- Resources: `resources/`

**Path reference convention**: Cross-grimoire references use root placeholders:
- `GRIMOIRE_ARCANA/docs/quickstart.md` - Reference Arcana from anywhere
- `GRIMOIRE_{DOMAIN}/chapters/build_system/INDEX.md` - Reference domain's own grimoire

**NOT in scope**: Domain grimoires (use `/grm-domain-improve` for those)

**Anti-drift principles**:
- No static file trees or lists (use dynamic discovery)
- No relative paths across grimoire boundaries (use root placeholders)
- No hardcoded deployment paths (deployment-agnostic references)

---

## Deliverables

### 1. Fixes Applied Directly
All improvements are applied directly to Arcana files:
- Broken links fixed
- Outdated examples updated
- Placeholder consistency enforced
- Cross-references added/updated
- Version numbers synchronized
- Semantic clarity issues corrected
- Directory/path references updated
- Duplicate information eliminated (DRY enforcement)
- Static lists replaced with dynamic discovery

### 2. Concise Summary Output
Display to user (not saved to file):
- Component inventory count
- Issues found and fixed
- Semantic clarity improvements
- Duplications detected and eliminated
- DRY violations fixed
- Pattern insights (if analyzing domain grimoires)
- Invocation effectiveness summary (if tracking metrics)
- Remaining TODOs for manual review
- CHANGELOG.md update recommendation (if significant changes)

### 3. Documentation Only for Major Changes
**ONLY create documentation files when:**
- Preparing a major version bump
- Breaking changes that affect domains
- Significant architectural changes requiring migration guide

**Default behavior:** Apply fixes directly, show summary, update CHANGELOG.md if needed. No bloat.

---

## Example Output

```
✅ Arcana Improvement Complete

📊 Inventory: 9 invocations, 3 formulae, 6 reference docs, 1 template

Changes Applied:
- Updated 2 invocation examples, normalized 3 formula placeholders
- Fixed cross-references in docs/, synchronized version numbers
- Semantic clarity: 23 terminology fixes applied per reference.md
- DRY: removed duplicate file trees, consolidated to canonical locations
- Paths: fixed 11 relative cross-grimoire paths to root placeholders

Quality: all links resolve, format compliant, magical boundary 100%

Remaining TODOs:
- Update CHANGELOG.md, test invocation invocations, review with git diff
```

---

## Maintainer's Checklist

Before running this invocation:
- [ ] Current Arcana is committed (if using Git)
- [ ] Review CHANGELOG.md for recent domain feedback
- [ ] Check for any open governance proposals
- [ ] Understand impact on existing domain grimoires

After running this invocation:
- [ ] Review audit report thoroughly
- [ ] Test invocation invocations (/grm-domain-create-grimoire, /grm-meta-help, /grm-domain-improve)
- [ ] Verify formulae/grimoire creates working grimoires
- [ ] Update CHANGELOG.md if significant changes
- [ ] Announce to domains if breaking changes

---

## Version Update Workflow

When preparing a version bump:

### Patch (v1.0.x)
- Run this invocation to fix bugs
- Update CHANGELOG.md
- No domain announcement needed

### Minor (v1.x.0)
- Run this invocation to ensure quality
- Add new features to CHANGELOG.md
- Announce in domain communication channel
- Example: New invocation added, new formula template

### Major (vx.0.0)
- Run this invocation thoroughly
- Document breaking changes in CHANGELOG.md
- Create migration guide
- Announce 2 weeks in advance
- Example: Placeholder system changed, invocation invocation changed

---

## Quality Standards

Arcana must maintain:

✅ **Zero Domain-Specific Content**
- Generic examples only (Domain A, Domain B, Knowledge Domain)
- No platform names (Slack, SharePoint, GitHub)
- No industry terms (HR, Legal, Marketing)

✅ **Magical Boundary Compliance**
- Invocations, formulae, rites ONLY in Arcana
- Clear guidance that domains use templates/, scripts/, snippets/

✅ **Documentation Excellence**
- Every invocation has clear invocation, purpose, workflow
- Every formula has placeholder reference
- Every reference doc is current and cross-referenced

✅ **Version Discipline**
- CHANGELOG.md tracks all changes
- Version numbers consistent across files
- Semantic versioning followed strictly

---

## Related Invocations

- Improve a domain grimoire: `/grm-domain-improve` (run from grimoire directory)
- Create new invocation: Manually craft in `invocations/grimoire/` or `invocations/arcana/` and update INDEX.md
- Run all validations: `python3 rites/validate.py`
- Individual validations: See [rites/](../../rites/) directory

---

## Questions?

- Arcana maintainer communication channel
- Review governance: `docs/governance.md`
- Version history: `CHANGELOG.md`

---
