---
type: reference
title: "Skill Orphan Reconcile"
aliases: ["skill-orphan-reconcile", "orphan-reconcile"]
tags: [arcana/invocations, type/reference, scope/meta]
authority: grimoire
last_verified: 2026-06-01
---

# Skill Orphan Reconcile

An optional judgment step for the skill-registration workflows. The registration
rite (`rites/register_skills.py`) is deterministic: it removes a registered skill
directory only when it can **prove** Arcana ownership (an `ARCANA_SKILL_OWNERSHIP`
marker, or a generated-source provenance line pointing under a current Arcana or
grimoire `skills/` root). Anything it cannot prove it owns, it never deletes - it
reports it as `Preserve unowned: /<name>` or as a collision and leaves it byte
for byte.

That deterministic floor is correct and must stay deterministic. This fragment is
the **propose-then-confirm** layer that applies judgment to the residue: the
managed-prefix directories the rite preserved but that are, on inspection, stale
Arcana artifacts - most often a skill whose source directory was **renamed**
(`oly-standards-audit` -> `oly-audit-standards`) or removed, leaving the old
registration behind.

This is **not** a slash command and **not** a rite. It never changes what the
rite decides; it only judges the dirs the rite refused to touch, and removes them
only on one explicit confirmation.

## When to run it

After the registration rite reports one or more `Preserve unowned` entries or
`without Arcana ownership marker` collisions under a managed prefix
(`arc-`, `grm-`, or a grimoire's `skill_prefix`). If the rite reported none, skip
this step.

> Note: the rite recognizes legacy generated provenance (including the older
> em-dash `GENERATED — source:` form), so legacy and renamed orphans are usually
> cleaned mechanically. This step covers the remainder the rite still cannot
> prove - e.g. provenance pointing outside a current `skills/` root, or a marker
> that was hand-edited.

## Procedure

1. **Collect the residue.** From the rite's plan (`--dry-run` is convenient),
   gather every managed-prefix directory reported as `Preserve unowned` or as an
   unowned collision, for each agent skill target.
2. **Classify each by reading its `SKILL.md`:**
   - **Stale Arcana artifact** - it carries Arcana provenance (an
     `ARCANA_SKILL_OWNERSHIP` marker or a `GENERATED … source:` line) whose
     recorded source path lies under a known Arcana or grimoire `skills/` root,
     and that source no longer exists or was renamed (no current source skill
     renders this command name). Propose removal.
   - **User-authored or foreign** - no Arcana provenance, or content that does
     not match the generated shape. Leave it untouched and report it; the user
     decides.
3. **Propose, then confirm.** Present the proposed removals - command name, the
   absent or renamed source it pointed at, and the agent directory it lives in -
   and remove them only after one explicit confirmation. Scope every deletion to
   the agent skill directory and the known managed prefixes; never delete a
   directory that lacks Arcana provenance.
4. **Re-register and report.** Re-run `rites/register_skills.py` so the renamed
   or new skills register cleanly, then report what was removed, what was
   re-registered, and anything left for the user to judge.

## Boundaries

- Removing an unowned managed-prefix directory is an AMBER action (it writes
  under the user's home agent directories): propose first, apply on one
  confirmation. See [[docs/governance|governance]].
- Never auto-delete a directory the rite preserved without surfacing it first.
- The rite stays the source of truth for ownership; this step only acts on what
  the rite explicitly could not prove.

## Related

- Active-grimoire registration: [[invocations/grimoire/register_skills|register skills]]
- Global registration: [[invocations/agent/register_skills|register skills]]
- Update playbook: [[UPDATE|update]]
- Autonomy tiers: [[docs/governance|governance]]
