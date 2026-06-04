---
type: playbook
title: "Health Check Grimoire"
aliases: ["lint", "domain-lint", "health-check"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-05-12
---

# Invocation: Health Check Grimoire

## Purpose

Health-check the active grimoire. Combines mechanical rites (orphans, provenance, frontmatter, structure, links) with judgment-based passes (stale claims, ghost references, contradictions). Surface findings; apply only the fixes the user approves.

This is the LLM-wiki health pass: keeps the wiki maintained as it grows.

## Invocation

From the active grimoire context:

```
/grm-health-check
```

Flags:
- `--apply-mechanical` — apply deterministic repair rites, such as link repair, without asking per-fix. Orphan wiring, stale-claim verification, ghost-reference promotion, and contradiction resolution still require confirmation.
- `--quick` — only run the cheap mechanical rites; skip judgment passes.

## Preconditions

1. Resolve `GRIMOIRE_ROOT` with the shared grimoire directory guard. Refuse for Arcana itself.
2. The grimoire must have `sources/`, `log.md`, and a root hub.

## Workflow

### Phase 1: Mechanical rites

Run these against `GRIMOIRE_ROOT` and capture output:

```bash
python3 ARCANA_HOME/rites/validate.py --grimoire GRIMOIRE_ROOT
```

Stop and report if structure or frontmatter has hard errors — they invalidate later phases.

### Phase 2: Stale claims

For every page with `last_verified` older than the stale window (default 90 days; or a window the user specifies):

- List page, last_verified, and chapter.
- Categorize: critical (referenced by hubs), normal (leaf), historical (status: deprecated).
- Surface for review; do not auto-update `last_verified` — verification is a human/LLM judgment act.

### Phase 3: Ghost references

Scan all chapter markdown for entity-shaped tokens (capitalized phrases, code identifiers, recurring proper nouns). For any token that:

- appears in 3+ pages, AND
- has no canonical page path representing it,

propose creating a page. List frequency and source pages. The user picks which to promote.

### Phase 4: Contradictions

For pages that share `tags` (especially same `chapter/<chapter>`), look for opposing claims:

- Numerical conflicts (different version numbers, different counts).
- Procedural conflicts (different steps for the same task).
- Definitional conflicts (different meanings for the same term).

Flag contradictions with file:line citations. Resolution is the user's call — do not silently pick a winner.

### Phase 5: Missing cross-references

For each pair of pages in the same chapter or sharing a `domain/<...>` tag:

- If they discuss the same entity/concept, ensure each links to the other.
- Suggest full-path wikilink additions where bidirectional links are missing.

### Optional: parallelize the judgment passes

Phases 2-5 (stale claims, ghost references, contradictions, missing cross-references) are independent read-only scans. If, and only if, this agent can spawn subagents, you MAY run them as parallel read-only lanes; otherwise run the phases exactly as written above, in order. The orchestrator always owns Phase 1 mechanical rites, Phase 6 confirm-then-apply, Phase 7 log append, and Phase 8 re-validate; lanes only surface and propose. Lane mechanics, the per-lane output contract, and the serial fallback live in [[invocations/meta/subagent_lanes|subagent lanes]]. The lanes for this workflow:

| Lane | Covers | Primary question |
|---|---|---|
| stale-claims | Phase 2 | Which pages are past the stale window, categorized critical (hub-referenced) / normal (leaf) / historical (deprecated)? Surface only; never auto-update last_verified. |
| ghost-references | Phase 3 | Which entity-shaped tokens appear in 3+ pages with no canonical page, with frequency and source pages listed for the user to promote? |
| contradictions | Phase 4 | Where do numerical, procedural, or definitional claims conflict, with file:line citations? Flag only; do not pick a winner. |
| missing-cross-refs | Phase 5 | Which page pairs in the same chapter or sharing a domain tag discuss the same concept but lack reciprocal full-path wikilinks, and what wikilinks close the gap? |

### Phase 6: Apply fixes

Group findings by category. For each group ask the user:

- **Auto-apply**: clearly mechanical fixes (broken markdown links the rite already located, missing wikilinks where target exists, frontmatter format issues).
- **Confirm-then-apply**: orphan wiring (which hub should own this orphan?), terminology standardization, page promotions.
- **Surface only**: contradictions, stale claims, ghost references -> list them; do not act without explicit approval.

### Phase 7: Append to log.md

```bash
python3 ARCANA_HOME/rites/append_log.py \
  --grimoire GRIMOIRE_ROOT \
  --op health-check \
  --title "<short summary>" \
  --skill /grm-health-check \
  --field orphans=<n> \
  --field stale=<n> \
  --field ghost-refs=<n> \
  --field contradictions=<n> \
  --field fixes-applied=<n>
```

### Phase 8: Re-validate

Re-run Phase 1 rites. They must all pass before declaring the health check complete.

## Non-negotiable rules

1. Mechanical rites' output is the source of truth for orphan/provenance/frontmatter findings. Don't override.
2. Contradictions and stale claims are surfaced, not silently fixed.
3. Every page touched by Phase 6 is reflected in the log entry.
4. The health check operates on the active grimoire only. Never reach into other grimoires.

## Report

Surface in chat:

| Category | Count | Status |
|---|---|---|
| Structure errors | n | pass/fail |
| Frontmatter violations | n | pass/fail |
| Broken links / wikilinks | n | pass/fail |
| Orphans | n | listed |
| Provenance violations | n | listed |
| Stale (>90d) | n | listed |
| Ghost references | n | listed |
| Contradictions | n | listed |
| Missing cross-refs | n | listed |
| Fixes applied | n | itemized |

## Related

- Mechanical: `/grm-validate`
- Semantic / naming: `/grm-audit-semantics`
- Page schema: `ARCANA_HOME/docs/page_schema.md`
- Optional parallel analysis: [[invocations/meta/subagent_lanes|subagent lanes]]
- Comprehensive grimoire pass: `/grm-improve` (health-check runs as one phase of improve)
