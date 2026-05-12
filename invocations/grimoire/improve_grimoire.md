# 🪄 Invocation: Improve Your Grimoire

## ⚡ Purpose

Continuously improve your domain's grimoire for maximum token-efficiency and deterministic routing:
`INDEX.md` → `chapter INDEX.md` → `1–2 canonical leaf docs`

**This invocation is safe to rerun at any time.**

---

---

## ⚡ The Magical Boundary ⚡

**This invocation operates within the magical boundary:**

### Magical Language for System Operations
- I'll use wizardly language to describe Grimoire operations: "audit your grimoire", "wire routers", "canonicalize knowledge"
- The audit process itself is magical (how Grimoire knowledge is organized)

### Practical Assessment of Content
- I'll examine your PRACTICAL domain content: `templates/`, `scripts/`, `snippets/`, `policies/`
- Recommendations stay domain-appropriate and searchable
- No magical folder names (`invocations/`, `formulae/`, `rites/`) will be created in your grimoire

**This invocation improves the SYSTEM (routing, organization) while respecting the CONTENT (practical knowledge).**

---

## Preconditions

Before executing any phase, verify:

1. **The current directory is a registered domain grimoire.** Check `~/grimoire/catalog.json` — the working directory must match a grimoire's `local_path`.
2. **If it does not match**: display an error listing available grimoires from the catalog, tell the user to `cd` to one, and **stop**. Do not proceed.

Arcana is not a grimoire. This invocation never operates on Arcana and never suggests `/grm-arcana-improve` as a fallback — they are unrelated operations.

---

## When to Cast

- Your grimoire has grown and feels cluttered
- Routing is taking too many hops to reach knowledge
- You've accumulated orphan docs or broken links
- AI agents are reading more files than necessary
- Content feels duplicated across multiple docs

---

## Invocation

From your domain grimoire's root directory, cast:

```
/grm-domain-improve
```

The AI will audit your grimoire and apply improvements automatically.

---

## What This Invocation Does

### Phase 1: Inventory & Health Check
1. Enumerate all routers (INDEX.md files)
2. Enumerate all leaf docs and classify as wired or orphaned
3. Validate all pointers (detect broken links)
4. Detect non-deterministic routing language ("search", "look around")
5. Identify token bloat in routers
6. Find duplicate content and deprecated docs

**Checkpoint**: Reports findings before making any changes

### Phase 2: Router Normalization
7. Normalize all router structures (keep them short)
8. Trim router bloat (move prose to leaf docs)
9. Enforce router limits (root → chapter → 1-2 leaves)

### Phase 2.5: Semantic Analysis ✨

**AI-Powered Analysis** (see [docs/script_vs_ai.md](../../docs/script_vs_ai.md)):

This phase uses **AI intelligence** to understand context and meaning, not just pattern matching:

10. Run semantic clarity analysis on all chapters **with contextual understanding**
11. Score naming quality based on **judgment**, not just rules
12. Detect terminology inconsistencies **in context** (config vs configuration - which is better here?)
13. Measure discoverability and searchability **for your domain**
14. Generate renaming recommendations **with reasoning** and impact analysis
15. Identify quick wins (high impact, low effort improvements **specific to your grimoire**)

**Why AI, not scripts?**
- Scripts can count files and find patterns
- Only AI can judge "Is this name clear enough?" "Would users find this?"
- AI adapts to your domain's domain and evolves with AI capabilities

**Checkpoint**: Report semantic issues and prioritized improvements

### Phase 3: Canonicalization
16. Choose ONE canonical doc for duplicate topics
17. Split oversized docs only if it reduces total reads
18. Wire or remove orphan docs

### Phase 3.5: Boundary Validation ✨ NEW
19. Validate magical boundary compliance
20. Detect platform-specific language (Slack → domain communication)
21. Find team/department buzzwords (HR → policy domain)
22. Verify generic examples only
23. Check for magical contamination (no invocations/formulae/rites in grimoire)
24. Ensure practical terminology in chapter content

**Checkpoint**: Report boundary violations (critical vs warnings)

### Phase 4: Validation
25. Define minimal-read paths for representative requests
26. Run integrity checks (all pointers resolve)
27. Grep checks (no absolute paths, no "search" instructions)
28. Scope hygiene (no scope leakage)

### Phase 5: Freshness Check
29. Review pages for outdated content (stale snapshot values, broken file references)
30. Prioritize freshness remediation
31. Include freshness status in audit report

### Phase 6: Quality Scoring ✨ NEW
33. Calculate overall grimoire quality grade (A-F)
34. Generate accessibility score (how discoverable is knowledge?)
35. Measure discoverability metrics (search term coverage)
36. Compute routing efficiency score (avg hops, token cost)
37. Compare against best practice benchmarks
38. Compare against previous run (if available in git history)
39. Generate improvement roadmap prioritized by impact

---

## Non-Negotiable Rules

1. **Do NOT invent new conventions** - Only restructure based on what exists
2. **Deterministic routing only** - Explicit file pointers, no "search/look around"
3. **Grimoires are maps** - Don't duplicate implementation details
4. **No absolute paths** - Use relative repo paths only
5. **Preserve meaning** - Refactors are structural, not changing technical intent
6. **Stay in grimoire scope** - This invocation improves YOUR grimoire only, not Arcana

---

## Scope

This invocation audits only your domain's grimoire:

```
grimoire-{your-domain}/
├── INDEX.md                  ← Root router
├── README.md                 ← Domain documentation
└── chapters/                 ← All chapter routers and leaves
    ├── **/INDEX.md           ← Chapter routers
    ├── **/*.md               ← Leaf docs
    ├── **/templates/         ← Templates (not formulae!)
    ├── **/scripts/           ← Scripts (not rites!)
    └── **/snippets/          ← Snippets
```

**NOT in scope**: Arcana itself (use `/grm-arcana-improve` for that)

---

## Working Directory Context

This invocation is **grimoire-contextual**. It operates on the grimoire in your current working directory.

**Example**: If you run this from `olympus-grimoire/`, it improves only the Olympus grimoire.

**To improve a different grimoire**:
```bash
cd grimoire-{other-domain}/
/grm-domain-improve
```

---

## Deliverables

### 1. Fixes Applied Directly
All improvements applied directly to grimoire files:
- Routers normalized
- Broken pointers fixed
- Duplicate content merged
- Orphan docs wired or removed
- Bloat trimmed
- Semantic clarity issues corrected
- Magical boundary violations fixed

### 2. Comprehensive Summary Output
Display to user (not saved to file):
- Quality grade (A-F) and score (0-100)
- Component inventory
- Issues found and fixed
- Semantic analysis results
- Boundary validation status
- Freshness check results
- Quick wins applied
- Remaining TODOs for manual review

**No chronicle files created** - keeps grimoires lean and focused on actual knowledge, not audit history.

---

## Example Output

```
✅ Grimoire Improvement Complete - Olympus Engineering Domain

Quality Grade: B+ → A- (+8 points) 🌟

Changes Applied:
- Normalized 8 chapter routers (trimmed bloat)
- Fixed 3 broken pointers (chapters/build_system/INDEX.md)
- Merged 2 duplicate CMake docs → cmake_overrides.md (canonical)
- Removed 1 orphan doc (chapters/deprecated/old_build.md)
- Reduced average read path from 4 hops to 2.5 hops

Semantic Analysis:
- Renamed chapters/misc → chapters/utilities (+36 quality points)
- Standardized "config" vs "configuration" → "config" (17 files)
- Terminology consistency: 78% → 95%
- 3 quick wins applied (<30 min total)

Boundary Validation:
- ✅ No magical contamination (no invocations/formulae in grimoire)
- ✅ No platform assumptions detected
- ⚠️  Fixed 2 team buzzwords (Engineering → domain)
- ✅ All examples use generic names

Freshness:
- 42 docs healthy (validated <90 days)
- 6 docs stale (>90 days, need revalidation)
- 2 docs with SHA mismatch (sources changed)

Quality Metrics:
- Naming Clarity:        85/100 (A)
- Routing Efficiency:    92/100 (A)
- Discoverability:       88/100 (A)
- Boundary Compliance:   100/100 (A+)
- Freshness:            86/100 (A)
- Overall Grade:        A- (90/100)

Trending: ↑ +8 points from last audit (B+ → A-)

TODOs:
- Consider splitting chapters/code (12 sub-chapters)
- Revalidate chapters/build_system/deps/cmake_first.md (185 days old)
- Update chapters/platform/ops_boundaries.md (source SHA mismatch)

Next Steps:
1. Review changes with git diff
2. Test routing (ask AI to navigate to a chapter)
3. Apply any remaining TODOs manually
4. Commit improvements
```

---

## Common Improvements

### Router Bloat Reduction
**Before**:
```markdown
# Build System Chapter

This chapter contains all the information about our build system,
including CMake configuration, toolchain setup, dependency management,
CI/CD integration, and much more. The build system is complex...
[200 more words of prose]

## Routes
- For CMake → cmake_overrides.md
- For toolchains → toolchains/compiler_baseline.md
```

**After**:
```markdown
# Build System Chapter

## Routes
- CMake configuration → cmake_overrides.md
- Toolchain setup → toolchains/compiler_baseline.md
- Dependency management → deps/cmake_first_policy.md
- CI/CD integration → ci/gitlab_shell_ci.md
```

### Canonicalization
**Before**: 3 docs about CMake overrides (scattered, duplicated)
**After**: 1 canonical doc with all knowledge consolidated

### Broken Pointer Fix
**Before**: `chapters/old_name/INDEX.md` (404)
**After**: `chapters/current_name/INDEX.md` (resolves)

---

## Tips

### Run Regularly
- **Monthly**: Quick improvement pass
- **Quarterly**: Full audit with freshness validation
- **After major changes**: Whenever you add 5+ new docs

### Watch for Signs
Your grimoire needs improvement when:
- AI reads >3 files to answer simple questions
- You have >5 orphan docs
- Routers have >200 words of prose
- Domain members report "can't find X" despite it existing

### Before Running
- Commit current state (if using Git)
- Review the audit report before accepting all changes
- Test routing after improvements

---

## Related Invocations

**This invocation automatically invokes:**
- `analyze-semantics` - Semantic clarity analysis (Phase 2.5)
- `validate-boundaries` - Magical boundary validation (Phase 3.5)

**Other invocations:**
- Create chapter: `/grm-domain-create-chapter [topic]`
- Improve Arcana: `/grm-arcana-improve` (maintainer only)
- Standalone semantic analysis: `/grm-domain-analyze-semantics`
- Standalone boundary check: `/grm-arcana-validate-boundaries`

---

## Questions?

- Domain communication channel
- Operating model: `../../docs/operating_model.md`
- The Arcana maintainer: For guidance on complex improvements

---

**Cast this invocation regularly to keep your grimoire sharp and efficient!** 🪄
