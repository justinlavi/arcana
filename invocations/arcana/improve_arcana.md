---
type: playbook
title: "Improve Arcana"
aliases: ["improve-arcana", "arcana-improve"]
tags: [arcana/invocations, type/playbook, scope/arcana]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Improve Arcana

## Purpose

Maintainer-only orchestrator for Arcana itself. Combines mechanical
validation with judgment-based architecture, rite, and documentation review;
applies low-risk fixes; re-validates; and reports deferred design work.

For grimoires use `/grm-improve`. This invocation only audits Arcana.

## Invocation

```
/arc-improve
```

Run from the Arcana directory. Safe to rerun at any time.

## When to cast

- Before an Arcana release or version bump
- After bulk doc/feature changes
- After command-family, scaffold, installer, or validator changes
- When something feels stale, repetitive, or out of sync
- When Arcana feels correct but harder to explain or navigate than it should

## Workflow

### Phase 1: Run the validator suite

Use the orchestrator rite through `/arc-validate` or directly through `rites/validate.py`:

```bash
python3 rites/validate.py              # sequential
python3 rites/validate.py --parallel   # faster
python3 rites/validate.py --summary    # summary-only output
```

Equivalent skill: `/arc-validate`.

This runs every mechanical validator and aggregates results. Individual skills
exist for targeted reruns; the orchestrator is the default entry point.

### Phase 2: Triage violations

Review the aggregated output:

- **Mechanical fixes** (broken link, snake_case path, missing heading, hyphenated example): apply directly.
- **Structural issues** (missing hub, misplaced file): fix the structure, then re-run the offending validator.
- **Security hits**: treat as blocking. Investigate every credential pattern and unsafe construct before continuing.
- **Boundary violations**: invocations / formulae / rites belong in Arcana only. Move violators or rewrite.

Re-run `python3 rites/validate.py` after fixes until clean. Judgment work
starts from a mechanically stable tree so the AI spends context on design,
not basic breakage.

### Phase 3: Architecture quality

Cast the whole-repo architecture review:

- [[invocations/arcana/quality/review_architecture|review architecture]]

This is the AI-heavy pass. It inventories every surface, dispatches isolated
review lanes when subagents or parallel AI reviewers are available, builds a
source-of-truth map, reviews naming and folder boundaries, checks AI-agent
read paths, and looks for scalability risks.

Use the lane protocol in `quality/review_architecture.md` for S-tier passes:
root/docs, invocations, rites, formulae/tests, skills/agents, release/install,
and cross-cutting AI efficiency. Keep validation, synthesis, and final edits in
the maintainer context. If subagents are unavailable, run the same lanes
serially and report that the pass was serialized.
Require each lane to return the lane output contract from
[[invocations/meta/subagent_lanes|subagent lanes]], then merge findings into the
synthesis matrix before editing.

Apply local fixes directly; defer large moves, public command changes,
generated-output rewrites, or changes affecting more than ten files with a
clear benefit and blast radius. Persist substantial deferred items in
[[docs/architecture_backlog|architecture backlog]]
when they need maintainer review after the current conversation.

### Phase 4: Rite quality

Follow the rite-specific quality check at [[invocations/arcana/quality/validate_rites|validate rites]]. It's a judgment-based invocation (no dedicated skill - it runs as part of this orchestrator) that inspects rite scripts for style, error handling, exit codes, and idempotency. Apply fixes and re-run the validator suite from Phase 1.

### Phase 5: Contract coherence

Cast the contract-coherence audit:

- [[invocations/arcana/quality/audit_contract_coherence|audit contract coherence]]

It is judgment-based (no standalone slash command - it runs as part of this
orchestrator) and verifies that the free-text fields in
`rites/data/command_surface.json` and `rites/data/rite_profiles.json` are TRUE of
the code. It behaviorally probes the envelope-wired rites on disposable temp
targets via `--format json` and code-reads the rest. Apply prose-wrong fixes to
the contract JSON; defer code-wrong findings to Phase 4 or the maintainer; then
re-run the validator suite from Phase 1.

### Phase 6: Documentation quality

Cast the documentation improvement invocation:

- [[invocations/arcana/quality/improve_documentation|improve documentation]]

This invocation covers both **duplication** (same fact in two places, copy-pasted file trees, drifting lists) and **clarity** (jargon, unclear antecedents, structural overload). It is judgment-based - no slash command - and is intended to run as part of this orchestrator.

Apply the fixes it surfaces. Prefer:

- A single canonical home for any fact, with links from elsewhere.
- Generated views over hand-maintained lists (see `rites/sync_docs.py` for the pattern).
- Splitting overloaded docs; deleting docs nothing else needs.

### Phase 7: Re-validate

After applying architecture, contract-coherence, rite, and documentation fixes,
run the validator suite once more:

```bash
python3 rites/validate.py
```

Link anchors, skill references, and structure checks are the most likely to break from a documentation reshuffle.

### Phase 8: Sync generated docs

If anything that feeds an auto-generated index changed (skills, invocation catalog, chapters):

```bash
python3 rites/sync_docs.py --apply
```

Then re-run validators a final time.

### Phase 9: Version & changelog

If the pass produced user-visible changes:

- Decide the version bump with the Compatibility Rule in [[docs/governance|governance]] §Versioning, **not** by how large the pass felt: existing grimoires still valid with no migration ⇒ MINOR (or PATCH for fixes/wording only); prior grimoires broken or needing migration ⇒ MAJOR. Version bumps and tags are human-sign-off — propose the bump, don't apply it unattended.
- Update `CHANGELOG.md` at the Arcana root.
- Before the current version is tagged as final, update that version's entry
  in place as the current architecture. After a version is tagged final,
  collect future changes under `[Unreleased]` until the next release entry is
  cut.
- Confirm version numbers are consistent across `VERSION`, `CHANGELOG.md`, and
  release docs.
- For breaking changes: document the migration path and announce to domain leads.

## Phase dependencies

- Phase 2 depends on Phase 1 output.
- Phase 3 should happen after Phase 1 is clean - judgment work is wasted if mechanical issues are still masking real problems.
- Phase 5 (contract coherence) depends on Phase 1 being clean - the structural floor must hold before semantic claims are worth auditing - and runs after Phase 4 so the rite-quality reading is fresh. Its prose edits touch only the contract JSON, so the renumbered Phase 7 (re-validate) must run after it.
- Phase 6 should happen after Phase 3 so documentation cleanup can use the architecture review's source-of-truth map.
- Phase 7 must run after Phases 3-6 (link anchors drift when docs move).
- If Phase 8 changes generated docs, rerun Phase 7 afterward.
- Phase 9 happens last so the changelog describes the final validated state.

## Non-negotiable rules

1. **Universal only** - no domain-specific content in Arcana.
2. **Backward compatible by default** - don't break existing grimoires; a deliberate break requires a MAJOR bump and a deprecation cycle (see [[docs/governance|governance]] §Versioning / Deprecation Policy).
3. **Canonical examples only** - `cooking-grimoire` (personal), `hr-grimoire` (workplace); plus `Alice/Bob`, `Project Alpha`, `{your-grimoire}` for sub-examples. No real product/company names, no industry-narrowing assumptions.
4. **Magical boundary** - invocations, formulae, rites live ONLY in Arcana.
5. **Semantic versioning** - the bump is decided by the Compatibility Rule (compatibility, not change size); see [[docs/governance|governance]] §Versioning. Reflected in `CHANGELOG.md`.
6. **Path conventions** - cross-grimoire references use root placeholders (`ARCANA_HOME/`) and library-key paths such as `cooking-grimoire/...`, never `../`.
7. **Single source of truth** - every repeated fact is either a short navigation summary, generated view, intentional release snapshot, or a bug.
8. **AI efficiency** - preserve deterministic read paths; prefer one hub, one invocation, and only the needed canonical docs for common tasks.

## Scope

In scope:

- Root: hub, `README.md`, `CHANGELOG.md`
- Root config and project files: `arcana.json`, `VERSION`, `pyproject.toml`, `CONTRIBUTING.md`, `.editorconfig`, `.gitattributes`, `.gitignore`
- `docs/*.md`
- `invocations/arcana/`, `invocations/grimoire/`, `invocations/agent/`, `invocations/library/`, `invocations/workspace/`, `invocations/help/`, and `invocations/meta/`
- `formulae/*.formula.md` and `formulae/grimoire/` (the master template)
- `rites/*.py`
- `skills/<family>/<slug>/SKILL.md`
- `tests/` fixtures and validator coverage
- `.github/` release automation and `.obsidian/` shareable settings
- `resources/`

Out of scope: grimoires (use `/grm-improve`).

## Deliverables

Apply fixes directly to Arcana files. Report to the user, and write to
`docs/architecture_backlog.md` only when a deferred item creates a reusable
architecture queue:

- Validator pass/fail summary
- Architecture review summary (review lanes, source-of-truth issues, naming/boundary findings, AI-efficiency findings)
- Contract coherence summary (claims audited by evidence tier, verdict tally, prose-wrong contract edits applied, code-wrong findings deferred)
- Fixes applied (counts by category)
- Documentation duplication / clarity fixes applied
- Remaining items needing human follow-up
- Architecture backlog items created, updated, or resolved
- Whether `CHANGELOG.md` should be updated

Only create new documentation files when they create a reusable canonical home,
support a major version or breaking change, or prevent a recurring quality pass
from being re-explained in chat.

## Maintainer checklist

Before:

- [ ] Working tree clean (committed)
- [ ] Recent CHANGELOG / governance items reviewed

After:

- [ ] Validator suite green
- [ ] Architecture review completed or explicitly skipped with reason
- [ ] Contract coherence audited or explicitly skipped with reason
- [ ] Generated docs synced (`rites/sync_docs.py --apply`)
- [ ] Smoke-test key skills: `/grm-create`, `/arc-help`, `/grm-improve`
- [ ] `CHANGELOG.md` updated if changes are user-visible
- [ ] Breaking changes announced to domain leads

## Related

- All validators: `/arc-validate` - `python3 rites/validate.py`
- Individual validator selectors: see `invocations/arcana/validators/validators.md`
- Architecture quality: [[invocations/arcana/quality/review_architecture|review architecture]]
- Rite quality: [[invocations/arcana/quality/validate_rites|validate rites]]
- Contract coherence: [[invocations/arcana/quality/audit_contract_coherence|audit contract coherence]]
- Documentation quality: [[invocations/arcana/quality/improve_documentation|improve documentation]]
- Doc generator: `rites/sync_docs.py`
- Grimoire equivalent: `/grm-improve`
