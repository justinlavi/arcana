---
type: playbook
title: "Analyze Semantics"
aliases: ["analyze-semantics", "naming-audit"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-05-12
---

# Invocation: Analyze Semantic Clarity

## Purpose

Judgment-based analysis of naming and organization in a grimoire. Evaluates whether chapter and file names are clear, discoverable, terminologically consistent, and token-efficient — and proposes prioritized renames.

This is the AI counterpart to `/arc-validate-semantics`, which only mechanically scans Arcana for hyphenated path examples in prose. This invocation reads meaning; the validator matches patterns.

## Invocation

From a registered grimoire directory:

```
/grm-analyze-semantics
```

Flags:
- `--quick` — quick wins only
- `--chapter=<name>` — single chapter
- `--arcana` — analyze Arcana itself

## Preconditions

Verify the working directory is a registered grimoire (check `~/grimoires/library.json`). If not, list available grimoires and stop. Arcana is not a grimoire (use `--arcana` for that case).

## When to cast

- Before committing new chapters
- After major refactors
- When users or AI agents struggle to find or route to knowledge
- Quarterly grimoire quality review
- As Phase 2.5 of `/grm-improve` (auto-invoked)

## Workflow

### 1. Load context

Read hub, the chapter list, and `docs/reference.md` (if present) to learn the grimoire's canonical vocabulary. Note the dominant naming pattern (snake_case is standard).

### 2. Score each chapter and file name

Apply four dimensions, 0100 each:

- **Specificity** — Penalize vague names (`misc`, `other`, `stuff`, `utils`). Reward domain-specific compound names (`build_system`, `cmake_overrides`). Penalize over-specific names that bake in versions or dates (`cmake_3_28_workaround`, `new_build_system`).
- **Searchability** — Does the name contain terms a user or agent would actually query? Does it match domain vocabulary in `reference.md`? Is it reachable from hub?
- **Comprehension** — Self-explanatory without surrounding context? Abbreviations unambiguous (`ms_sw` is not; `mission_support_sw` is)? Jargon level appropriate for the audience?
- **Token efficiency** — Name length vs. knowledge contained. Router hop count to reach the content. Long names compound across every read.

Aggregate to a letter grade:

| Score | Grade | Action |
|------|------|-------|
| 80100 | A | Keep |
| 7079 | B | Optional polish |
| 6069 | C | Consider rename |
| 5059 | D | Should rename |
| 049 | F | Must rename |

### 3. Detect terminology drift

Build a synonym map across chapter names, headings, and prose. Flag inconsistent variants and pick a canonical form:

- `config` vs `configuration` vs `cfg`
- `repo` vs `repository`
- `cmake` vs `CMake` vs `CMAKE`
- Mixed case styles in filenames (snake_case is standard; flag camelCase or kebab-case)

If `docs/reference.md` exists, treat it as authoritative. Otherwise propose canonical terms.

### 4. Assess discoverability

- **Search-term coverage** — For 5-10 plausible queries against this grimoire, is the hop count proportionate to the topic's depth? List queries whose path is unreasonably long (a simple FAQ buried five hubs deep) or unreasonably ambiguous.
- **Orphans** — Knowledge present on disk but not linked from any hub or related leaf.
- **Single points of failure** — Critical knowledge with only one route in.
- **Hot paths** — Frequently-needed chapters buried behind extra hops; recommend promoting.

### 5. Assess structure

- **Hierarchy depth** — Depth is open-ended; what matters is *appropriate* depth. Flag chains that feel overly deep for the content (gratuitous nesting) or overly flat for content that has natural sub-topics (missed grouping). Don't impose a fixed limit.
- **Chapter balance** — Bloated chapters (split candidates) and tiny chapters (merge candidates).
- **Sub-chapter sprawl** — >8 siblings under one hub suggests reorganization.
- **Parent/child coherence** — Names should compose logically (`code/cpp/formatting` good; `build/config/stuff` bad).
- **Idempotent hubs** — Verify each hub mixes sub-hubs and leaves cleanly; flag hubs that have only one child (collapse candidate) or that contain leaves with prose more naturally belonging in their own sub-hub.

### 6. Token efficiency

- Compare average hops to topic depth: a simple FAQ should be 2-3 hops, a deeply technical sub-topic may justifiably be 4-5. Flag mismatches.
- Hub file token cost (roughly word count — 1.3). Flag bloated hubs.
- Cumulative cost of long names across a typical multi-chapter read.

### 7. Generate recommendations

Group by priority:

1. **Critical renames** (score <50) — current name, proposed name, files affected, what breaks, estimated effort, predicted score gain.
2. **Suggested renames** (50-69) — same fields, lower priority.
3. **Terminology standardization** — chosen canonical term plus the variants to replace.
4. **Structure changes** — splits, merges, flattenings; estimated effort.
5. **Quick wins** — anything <30 min effort with 10-point gain. Surface these separately.

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

- **Mechanical counterpart**: `/arc-validate-semantics` (hyphenated path examples in prose)
- **Apply changes**: `/grm-improve`
- **Structure validation**: `/grm-validate-structure`
- **Boundary validation**: `/grm-validate-boundaries`
