# Invocation: Analyze Semantic Clarity

## Purpose

Judgment-based analysis of naming and organization in a domain grimoire. Evaluates whether chapter and file names are clear, discoverable, terminologically consistent, and token-efficient — and proposes prioritized renames.

This is the AI counterpart to `/grm-arcana-validate-semantics`, which only mechanically scans Arcana for deprecated terms and hyphenated paths. This invocation reads meaning; the validator matches patterns.

## Invocation

From a registered domain grimoire directory:

```
/grm-domain-analyze-semantics
```

Flags:
- `--quick` — quick wins only
- `--chapter=<name>` — single chapter
- `--arcana` — analyze Arcana itself

## Preconditions

Verify the working directory is a registered domain grimoire (check `~/grimoire/catalog.json`). If not, list available grimoires and stop. Arcana is not a grimoire (use `--arcana` for that case).

## When to cast

- Before committing new chapters
- After major refactors
- When users or AI agents struggle to find or route to knowledge
- Quarterly grimoire quality review
- As Phase 2.5 of `/grm-domain-improve` (auto-invoked)

## Workflow

### 1. Load context

Read `INDEX.md`, the chapter list, and `docs/reference.md` (if present) to learn the grimoire's canonical vocabulary. Note the dominant naming pattern (snake_case is standard).

### 2. Score each chapter and file name

Apply four dimensions, 0–100 each:

- **Specificity** — Penalize vague names (`misc`, `other`, `stuff`, `utils`). Reward domain-specific compound names (`build_system`, `cmake_overrides`). Penalize over-specific names that bake in versions or dates (`cmake_3_28_workaround`, `new_build_system`).
- **Searchability** — Does the name contain terms a user or agent would actually query? Does it match domain vocabulary in `reference.md`? Is it reachable from `INDEX.md`?
- **Comprehension** — Self-explanatory without surrounding context? Abbreviations unambiguous (`ms_sw` is not; `mission_support_sw` is)? Jargon level appropriate for the audience?
- **Token efficiency** — Name length vs. knowledge contained. Router hop count to reach the content. Long names compound across every read.

Aggregate to a letter grade:

| Score | Grade | Action |
|-------|-------|--------|
| 80–100 | A | Keep |
| 70–79 | B | Optional polish |
| 60–69 | C | Consider rename |
| 50–59 | D | Should rename |
| 0–49 | F | Must rename |

### 3. Detect terminology drift

Build a synonym map across chapter names, headings, and prose. Flag inconsistent variants and pick a canonical form:

- `config` vs `configuration` vs `cfg`
- `repo` vs `repository`
- `cmake` vs `CMake` vs `CMAKE`
- Mixed case styles in filenames (snake_case is standard; flag camelCase or kebab-case)

If `docs/reference.md` exists, treat it as authoritative. Otherwise propose canonical terms.

### 4. Assess discoverability

- **Search-term coverage** — For 5–10 plausible queries against this grimoire, can the answer be reached in ≤3 hops from `INDEX.md`? List the queries that fail.
- **Orphans** — Knowledge present on disk but not linked from any router or index.
- **Single points of failure** — Critical knowledge with only one route in.
- **Hot paths** — Frequently-needed chapters buried behind extra hops; recommend promoting.

### 5. Assess structure

- **Hierarchy depth** — Ideal 2–3 levels. Flag anything ≥4.
- **Chapter balance** — Bloated chapters (split candidates) and tiny chapters (merge candidates).
- **Sub-chapter sprawl** — >8 siblings suggests reorganization.
- **Parent/child coherence** — Names should compose logically (`code/cpp/formatting` good; `build/config/stuff` bad).

### 6. Token efficiency

- Average hops from root to a typical answer (target <2.5, acceptable ≤3.5).
- Router file token cost (roughly word count × 1.3). Flag bloated routers.
- Cumulative cost of long names across a typical multi-chapter read.

### 7. Generate recommendations

Group by priority:

1. **Critical renames** (score <50) — current name, proposed name, files affected, what breaks, estimated effort, predicted score gain.
2. **Suggested renames** (50–69) — same fields, lower priority.
3. **Terminology standardization** — chosen canonical term plus the variants to replace.
4. **Structure changes** — splits, merges, flattenings; estimated effort.
5. **Quick wins** — anything <30 min effort with ≥10-point gain. Surface these separately.

For each rename, include impact: incoming links to update, router entries to edit, downstream grimoires that reference the path.

## What to report

Three deliverables:

1. **Semantic analysis report** — overall grades (naming, terminology, discoverability, structure, token efficiency); top 5 and bottom 5 chapters by score; terminology conflicts with chosen canonical forms; critical and suggested renames with impact and effort; structure recommendations.
2. **Quick wins list** — high-impact, low-effort items the user can apply immediately.
3. **Terminology registry** — JSON mapping of canonical terms, abbreviations, and per-chapter scores, suitable for re-use by other tooling.

Surface the report in the chat. Do not write files unless the user asks.

## Apply guidance

- **Always apply**: critical renames, terminology standardization, quick wins.
- **Consider carefully**: structure refactors >2 hours, renames touching >10 files, changes to stable well-known chapter names.
- **Defer or reject**: cosmetic changes worth <10 points, anything mid-sprint, anything that conflicts with project conventions the user has set.

## Naming heuristics (quick reference)

- Chapter names are nouns or noun phrases (`build_system`, not `building` or `how_to_build`).
- Use technical domain vocabulary, not casual paraphrases (`toolchain_config`, not `compiler_stuff`).
- Avoid temporal or version-specific names (`cmake_overrides`, not `cmake_v3_28`).
- Prefer clarity over brevity (`platform_operations`, not `plat_ops`).
- snake_case for filesystem paths.

## Related

- **Mechanical counterpart**: `/grm-arcana-validate-semantics` (deprecated terms, hyphenated paths)
- **Apply changes**: `/grm-domain-improve`
- **Structure validation**: `/grm-domain-validate-structure`
- **Boundary validation**: `/grm-arcana-validate-boundaries`
