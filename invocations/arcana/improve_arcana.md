# Invocation: Improve Arcana

## Purpose

Maintainer-only orchestrator for Arcana itself. Sequences the validator suite, the rite quality check, and the documentation quality pass — applies fixes, re-validates, and reports.

For domain grimoires use `/grm-domain-improve`. This invocation only audits Arcana.

## Invocation

```
/grm-arcana-improve
```

Run from the Arcana directory. Safe to rerun at any time.

## When to cast

- Before an Arcana release or version bump
- After bulk doc/feature changes
- When something feels stale, repetitive, or out of sync

## Workflow

### Phase 1: Run the validator suite

Use the orchestrator rite — do **not** invoke each `/grm-arcana-validate-*` skill one at a time:

```bash
python3 rites/validate.py              # sequential
python3 rites/validate.py --parallel   # faster
python3 rites/validate.py --summary    # summary-only output
```

Equivalent skill: `/grm-arcana-validate-all`.

This runs every validator (structure, naming, format, links, security, semantics, skill-refs, boundaries) and aggregates results. Individual skills exist for targeted reruns; the orchestrator is the default entry point.

### Phase 2: Triage violations

Review the aggregated output:

- **Mechanical fixes** (broken link, snake_case path, missing heading, deprecated term): apply directly.
- **Structural issues** (missing INDEX, misplaced file): fix the structure, then re-run the offending validator.
- **Security hits**: treat as blocking. Investigate every credential pattern and unsafe construct before continuing.
- **Boundary violations**: invocations / formulae / rites belong in Arcana only. Move violators or rewrite.

Re-run `python3 rites/validate.py` after fixes until clean.

### Phase 3: Rite quality

Follow the rite-specific quality check at [`quality/validate_rites.md`](quality/validate_rites.md). It's a judgment-based invocation (no dedicated skill — it runs as part of this orchestrator) that inspects rite scripts for style, error handling, exit codes, and idempotency. Apply fixes and re-run the validator suite from Phase 1.

### Phase 4: Documentation quality

Cast the documentation improvement invocation:

- [`quality/improve_documentation.md`](quality/improve_documentation.md)

This single invocation now covers both **duplication** (same fact in two places, copy-pasted file trees, drifting lists) and **clarity** (jargon, unclear antecedents, structural overload). It is judgment-based — no slash command — and is intended to run as part of this orchestrator.

Apply the fixes it surfaces. Prefer:

- A single canonical home for any fact, with links from elsewhere.
- Generated views over hand-maintained lists (see `rites/sync_docs.py` for the pattern).
- Splitting overloaded docs; deleting docs nothing else needs.

### Phase 5: Re-validate

After applying documentation fixes, run the validator suite once more:

```bash
python3 rites/validate.py
```

Link anchors, skill references, and structure checks are the most likely to break from a documentation reshuffle.

### Phase 6: Sync generated docs

If anything that feeds an auto-generated index changed (skills, invocation catalog, chapters):

```bash
python3 rites/sync_docs.py --apply
```

Then re-run validators a final time.

### Phase 7: Version & changelog

If the pass produced user-visible changes:

- Update `CHANGELOG.md` at the Arcana root.
- Confirm version numbers are consistent across files.
- For breaking changes: document the migration path and announce to domain leads.

## Phase dependencies

- Phase 2 depends on Phase 1 output.
- Phase 4 should happen after Phase 1 is clean — judgment work is wasted if mechanical issues are still masking real problems.
- Phase 5 must run after Phase 4 (link anchors drift when docs move).
- Phase 6 must run before Phase 5's final clean check if generated indexes changed.

## Non-negotiable rules

1. **Universal only** — no domain-specific content in Arcana.
2. **Backward compatible** — don't break existing domain grimoires.
3. **Generic examples** — Domain A, Knowledge Domain; no platform names (Slack, GitHub), no industry terms.
4. **Magical boundary** — invocations, formulae, rites live ONLY in Arcana.
5. **Semantic versioning** — strict; reflected in `CHANGELOG.md`.
6. **Path conventions** — cross-grimoire references use root placeholders (`GRIMOIRE_ARCANA/`, `GRIMOIRE_{DOMAIN}/`), never `../`.

## Scope

In scope:

- Root: `INDEX.md`, `README.md`, `CHANGELOG.md`
- `docs/*.md`
- `invocations/grimoire/`, `invocations/arcana/`, `invocations/meta/`
- `formulae/*.formula.md` and `formulae/grimoire/` (the master template)
- `rites/*.py`
- `resources/`

Out of scope: domain grimoires (use `/grm-domain-improve`).

## Deliverables

Apply fixes directly to Arcana files. Report to the user (do not write to disk):

- Validator pass/fail summary
- Fixes applied (counts by category)
- Documentation duplication / clarity fixes applied
- Remaining items needing human follow-up
- Whether `CHANGELOG.md` should be updated

Only create new documentation files for major version bumps, breaking changes, or migration guides.

## Maintainer checklist

Before:

- [ ] Working tree clean (committed)
- [ ] Recent CHANGELOG / governance items reviewed

After:

- [ ] Validator suite green
- [ ] Generated docs synced (`rites/sync_docs.py --apply`)
- [ ] Smoke-test key skills: `/grm-domain-create-grimoire`, `/grm-meta-help`, `/grm-domain-improve`
- [ ] `CHANGELOG.md` updated if changes are user-visible
- [ ] Breaking changes announced to domain leads

## Related

- All validators (orchestrated): `/grm-arcana-validate-all` — `python3 rites/validate.py`
- Individual validators: see `invocations/arcana/validators/INDEX.md`
- Rite quality: [`quality/validate_rites.md`](quality/validate_rites.md)
- Documentation quality: [`quality/improve_documentation.md`](quality/improve_documentation.md)
- Doc generator: `rites/sync_docs.py`
- Domain grimoire equivalent: `/grm-domain-improve`
