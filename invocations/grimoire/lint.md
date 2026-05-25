---
type: playbook
title: "Lint Grimoire"
aliases: ["lint", "domain-lint", "health-check"]
tags: [arcana/invocations, type/playbook, scope/domain]
authority: grimoire
last_verified: 2026-05-12
---

# Invocation: Lint Grimoire

## Purpose

Health-check the active grimoire. Combines mechanical rites (orphans, provenance, frontmatter, structure, links) with judgment-based passes (stale claims, ghost references, contradictions). Surface findings; apply only the fixes the user approves.

This is the LLM-wiki "lint" pass: keeps the wiki maintained as it grows.

## Invocation

From the active grimoire's root:

```
/arc-grimoire-lint
```

Flags:
- `--apply-mechanical` — apply mechanical fixes (orphan-wiring suggestions, link repair) without asking per-fix.
- `--quick` — only run the cheap mechanical rites; skip judgment passes.

## Preconditions

1. Working directory must be a registered grimoire (its key in `~/grimoires/library.json`). Refuse for Arcana itself.
2. The grimoire must have `sources/`, `log.md`, and a root hub.

## Workflow

### Phase 1: Mechanical rites

Run these from the grimoire root and capture output:

```bash
python3 ARCANA_HOME/rites/validate_grimoire_structure.py --grimoire .
python3 ARCANA_HOME/rites/validate_frontmatter.py --grimoire .
python3 ARCANA_HOME/rites/validate_links.py --grimoire .
python3 ARCANA_HOME/rites/validate_orphans.py --grimoire .
python3 ARCANA_HOME/rites/validate_provenance.py --grimoire .
```

Stop and report if structure or frontmatter has hard errors — they invalidate later phases.

### Phase 2: Stale claims

For every page with `last_verified` older than 90 days (or older than the user's configured window):

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

### Phase 6: Apply fixes

Group findings by category. For each group ask the user:

- **Auto-apply**: clearly mechanical fixes (broken markdown links the rite already located, missing wikilinks where target exists, frontmatter format issues).
- **Confirm-then-apply**: orphan wiring (which hub should own this orphan?), terminology standardization, page promotions.
- **Surface only**: contradictions, stale claims, ghost references -> list them; do not act without explicit approval.

### Phase 7: Append to log.md

```bash
python3 ARCANA_HOME/rites/append_log.py \
  --grimoire . \
  --op lint \
  --title "<short summary>" \
  --skill /arc-grimoire-lint \
  --field orphans=<n> \
  --field stale=<n> \
  --field ghost-refs=<n> \
  --field contradictions=<n> \
  --field fixes-applied=<n>
```

### Phase 8: Re-validate

Re-run Phase 1 rites. They must all pass before declaring lint complete.

## Non-negotiable rules

1. Mechanical rites' output is the source of truth for orphan/provenance/frontmatter findings. Don't override.
2. Contradictions and stale claims are surfaced, not silently fixed.
3. Every page touched by Phase 6 is reflected in the log entry.
4. Lint operates on the active grimoire only. Never reach into other grimoires.

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

- Mechanical: `/arc-validate-structure`, `/arc-validate-frontmatter`, `/arc-validate-links`, `/arc-validate-orphans`, `/arc-validate-provenance`
- Semantic / naming: `/arc-grimoire-analyze-semantics`
- Page schema: `ARCANA_HOME/docs/page_schema.md`
- Comprehensive grimoire pass: `/arc-grimoire-improve` (lint runs as one phase of improve)
