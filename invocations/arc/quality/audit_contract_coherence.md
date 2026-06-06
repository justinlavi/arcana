---
type: playbook
title: "Audit Contract Coherence"
aliases: ["audit-contract-coherence", "contract-coherence"]
tags: [arcana/invocations, type/playbook, scope/quality]
authority: grimoire
last_verified: 2026-05-30
---

# Invocation: Audit Contract Coherence

## Purpose

Judgment-based audit of the **semantic truth** of the free-text fields in
Arcana's two machine contracts:

- `rites/data/command_surface.json` - `mutation_behavior`, `log_behavior`,
  `validation_profile`, and `mutation_profile` read as a behavioral claim.
- `rites/data/rite_profiles.json` - `writes`, `idempotency`, `plan_command`,
  `apply_command`, `default_mode`, and `validation_profile`.

The mechanical validators keep the deterministic floor. `rites/command_surface.py`
proves each prose field exists, is the right type, sits in its allowed enum,
points at real `skill_source` / `invocation` / `guard` / `rite_owner` targets,
is unique, and that the contract-vs-disk command set is complete.
`rites/rite_profiles.py` proves the profile enum and reconciles AST
write-detection against the declared profile. `rites/validate_skill_refs.py`
already performs the static cross-contract join: it errors
(`COMMAND_SURFACE_MUTATION_PROFILE_DRIFT`) when a rite-owned command's
`mutation_profile` disagrees with its rite's `rite_profiles.profile`. **None of
them reads what a sentence says.** This invocation owns the one question they
structurally cannot answer: *is each free-text claim TRUE of the code - and,
where the structured result envelope exists, of observed runtime behavior?*

It surfaces drift; it does not silently fix. Where the prose is wrong it edits
the contract JSON and re-runs the floor; where the code is wrong it defers to
Phase 4 rite quality / the maintainer. The deterministic floor stays
deterministic: this phase adds no checks to the validators and never weakens
them. See [[docs/script_vs_ai|script vs ai]] for the rite-vs-judgment split.

## Invocation

Runs as a phase of `/arc-improve`. There is no standalone slash command.

## When to cast

- After editing a rite that has an entry in either contract.
- After editing `command_surface.json` or `rite_profiles.json` prose.
- Before an Arcana release.
- During `/arc-improve`, after Phase 4 rite quality.

## What this audits

| Contract | Field | The claim | How it is checked |
|---|---|---|---|
| `command_surface` | `mutation_behavior` | What on-disk changes the command makes (or that it is read-only / judgment-gated). | Trace to the owner: read the `rite_owner` rite, or the invocation leaf for judgment/hybrid owners. Behavioral probe for the four enveloped-rite-owned commands. |
| `command_surface` | `mutation_profile` (as claim) | The declared safety posture is true of the command's real behavior. | The static `mutation_profile` <-> `rite_profiles.profile` agreement is already proven by `validate_skill_refs.py`; this adds only the runtime check that the declared profile matches the observed envelope `mode` for the four probeable commands. |
| `command_surface` | `log_behavior` | Whether and how the command writes a log entry, quantified. | Probe the `append_log` path (one append to `log.md`); code-read invocation-orchestrated or "does not append" cases. |
| `command_surface` | `validation_profile` | The listed validators exist, accept the named flags, and fit the effect. | Inline path + flag helper, then judgment on aptness. |
| `rite_profiles` | `writes` | The declared paths are exactly what the rite touches - no broader, no narrower. | Probe + before/after disk diff for the five enveloped rites; code-read write call sites for the rest. |
| `rite_profiles` | `idempotency` | The described re-run behavior holds. | Profile-specific probe for the five enveloped rites; code-read control flow for the rest. |
| `rite_profiles` | `plan_command` / `apply_command` / `default_mode` | The literal commands are invocable, flags are real, and they select the claimed mode. | Run the declared commands in `--format json` for enveloped rites; argparse flag check + code-read for the rest. |
| `rite_profiles` | `validation_profile` | The named follow-up validators exist, accept their flags, and fit the rite. | Same inline path + flag helper. |

## Probe vs code-read

Every verdict records how it was reached, so a `TRUE` from a probe is never
confused with a `TRUE` from a reading.

**Behavioral probe** is available only for rites wired to the `ResultReporter`
result envelope (`--format json` emitting `{rite, status, mode, root, summary,
mutations, messages}`). Derive that set at runtime - never hard-code it:

```bash
grep -rln "ResultReporter" rites/ | grep -v diagnostics.py
```

Today that is five rites: `append_log`, `repair_links`, `sync_library`,
`adopt_grimoire`, `clean_artifacts`. Of those, four back a public command
(`/grm-repair-links`, `/arc-sync library`, `/arc-adopt`,
`/arc-clean`); `append_log` is internal. The validator family also
accepts `--format`, but it emits `DiagnosticReporter` (a findings envelope), not
the mutation envelope - so `--format` alone does **not** make a rite probeable
for `writes` / `idempotency` / `mode`. Treat everything else, including
`sync_skills` (`plan_apply` but not enveloped), as **code-read only**, and
never claim a behavioral proof for a reading.

## Workflow

### 1. Inventory the contracts and derive the probe set

Assume the floor is already green (Phase 1): the two mechanical validators have
proven existence, type, enum, path resolution, uniqueness, and set
completeness. Do not re-check any of that.

```bash
python3 -c "import json; print(len(json.load(open('rites/data/command_surface.json'))['commands']), 'commands')"
python3 -c "import json; print(len(json.load(open('rites/data/rite_profiles.json'))['profiles']), 'rites')"
grep -rln "ResultReporter" rites/ | grep -v diagnostics.py   # the probe set
```

### 2. Reduce each prose field to a claim with an evidence tier

For every command and rite, list the claims to audit (the fields above) and tag
each with its tier **before** doing the work, so confidence is never inflated
after the fact. `behavioral_probe` (an enveloped rite, or a command an enveloped
rite owns) outranks `code_read` (everything else). A claim with no isolable
probe is `code_read`, not a guess.

### 3. Dispatch review lanes, or run them serially

Mirror the lane protocol in
[[invocations/arc/quality/review_architecture|review architecture]]. When
subagents are available, dispatch one lane per scope as read-only explorers that
may run probes on their **own** disposable temp target but edit no Arcana file:

| Lane | Scope | Primary question |
|---|---|---|
| cs-judgment | `command_surface` commands with judgment/hybrid owners | Do `mutation_behavior` + `log_behavior` match the owning invocation? |
| cs-rite-join | `command_surface` rite-owned commands | Does the declared `mutation_profile` match the observed envelope `mode`? (the static `mutation_profile` <-> `profile` agreement is already owned by `validate_skill_refs.py`; do not re-do it) |
| rp-envelope | the enveloped set from step 1 | Probe lane: `writes`, `idempotency`, plan/apply/default mode via `--format json`. |
| rp-codeonly | the profiled rites NOT in the step-1 probe set (subtract the `ResultReporter` set from `rite_profiles.json` profiles, e.g. `sync_skills`, `sync_docs`, `summon*`, `build_summon_binary`, `validate`) | Do `writes` / `idempotency` / commands match the code? (code-read) |
| vp-crosscut | `validation_profile` across both contracts | Do named validators exist, accept named flags, and fit the effect? |

Dispatch template:

```text
Audit contract coherence for this lane only.
Repo root: ARCANA_HOME. Lane: <name>. Scope: <commands/rites/fields>.
For any behavioral probe, create your OWN disposable target with mktemp -d
(a throwaway grimoire scaffold, or a throwaway HOME via --home <tmp> for
sync_library / adopt_grimoire); never touch a real grimoire, ~/grimoires, or
~/grimoires/library.json. If a probe cannot be isolated, downgrade the claim to
code_read and say so. Do not edit any file - surface findings only.
Return one verdict object per claim using the schema in
audit_contract_coherence.md.
```

Each probe lane is isolated by its own tempdir, so lanes run concurrently
safely. **Serial fallback** (no subagents): run the same five lanes
sequentially in the maintainer context, each minting and tearing down its own
temp target, keep each lane's verdicts separate until synthesis, and report in
the `/arc-improve` summary that the pass was serialized. The probe lane is
mandatory in both modes; only the temp-target lifecycle differs. Probes need
Python and a writable temp dir; an agent lacking them degrades to
code-read-and-say-so, never fakes a probe result.

### 4. Run the behavioral probes on disposable temp targets

Temp-target safety is absolute: every probe runs on a fresh `mktemp -d` target
seeded with the minimal fixable condition. Assert only on `status`, `mode`, and
`mutations[].path` / `mutations[].action` (deterministic); ignore summary counts
and message text. The `noop` rerun status is derived: it appears only when a run
emits zero mutations and no error message (the reporter returns `ok` when
mutations exist, `error` on an error message), so a no-op second apply is the
right signal for idempotency.

- **repair_links** (temp grimoire seeded with a filename-only wikilink):
  `--format json` -> `mode plan`, `mutations []`; `--apply --format json` ->
  `mode apply`, `status ok`, mutations on `*.md`; `--apply` again -> `status
  noop`, `mutations []`.
- **sync_library** (temp HOME with an unsynced grimoire):
  `--home <tmp> --format json` -> `mode plan` / `mutations []`; `--home <tmp>
  --apply --format json` -> `mode apply` / write `library.json`; rerun
  `--apply` -> `noop`.
- **adopt_grimoire** (temp HOME with an unmanaged dir):
  `<dir> --home <tmp> --skill-prefix <p> --format json` -> `mode apply` /
  `status ok` / write `grimoire.json`; rerun same dir -> `status error` /
  `blocked` (verifies refuse-to-overwrite).
- **clean_artifacts** (temp tree with a seeded `rites/.artifacts`):
  `--dry-run --format json` -> `mode plan` / `mutations []`; without `--dry-run`
  -> `mode apply` / mutation `remove`; rerun -> `noop`.
- **append_log** (temp grimoire): `--grimoire <tmp> --op <op> --title "x"
  --format json` -> `mode append`, exactly one mutation `append` to
  `<grimoire>/log.md`. Append-only: assert one append per call, **not**
  noop-on-rerun.

For `writes`, add an independent before/after disk diff of the temp tree and
fail the probe if any path outside the declared `writes` scope changed - the
envelope is self-reported, so the disk diff is the oracle that catches an
undeclared write. If a flag is absent or a temp target cannot be built, emit
`UNVERIFIABLE` - a setup failure is not a contract lie. Never execute
`summon*` / `sync_skills` / `sync_docs` / `build_summon_binary`.

### 5. Code-read the rest and run the validation-profile helper

For non-enveloped rites and all judgment/hybrid-owned command prose, trace each
claim to source: read the rite (or the invocation leaf) and confirm
`mutation_behavior` / `log_behavior` / `writes` / `idempotency` match the actual
write and log call chain. Cite `tests/test_sync_skills.py` as corroboration
for `sync_skills`, but label it `code_read`, not a behavioral proof. The
`summon_core.py` path with `apply_command` `python rites/summon.py` is intended
(`summon.py` is the dispatcher that imports `summon_core`); record it as a
judgment note, not a failure.

For `validation_profile` in both contracts, run the inline helper (a snippet in
this invocation, not a new rite):

```bash
# For each 'python rites/X.py ...' token: assert the rite exists and the flag is real.
test -f rites/X.py || echo "MISSING rite: rites/X.py"
grep -q -- '--grimoire' rites/X.py || echo "FLAG not in argparse: --grimoire"
```

File-existence and flag-presence failures are factual `FALSE` / `UNDERSPECIFIED`;
whether the named validators are the apt post-write checks is judgment.

### 6. Synthesize verdicts and decide fix vs defer

Concatenate every lane's verdicts and group by `verdict`, `fix_target`, and
`evidence_type` so a probe-proven finding is never merged with a read-judgment
one. For each non-`TRUE` verdict, decide which side is correct **before** acting:

- **PROSE-WRONG** (code correct, sentence misdescribes it): edit the contract
  JSON so the prose matches reality, then re-run the floor
  (`python3 rites/validate.py`) plus the originating probe to confirm the floor
  stays green and the prose now matches behavior. This is the only edit this
  phase makes directly, and it edits **data**, never code.
- **CODE-WRONG** (prose describes correct intent, code violates it): do not edit
  the rite here - that behavior change belongs to Phase 4. Surface it with
  `fix_target=code`, a `file:line` or failing envelope excerpt, and a first
  step; persist to [[docs/architecture_backlog|architecture backlog]] if it
  outlives the conversation.
- **UNVERIFIABLE** (non-enveloped, judgment owner, or un-isolable probe): record
  it and state the evidence type; never guess `TRUE`.

Never edit contract JSON to match buggy code - that launders a bug into
documented behavior.

### 7. Report

In the final `/arc-improve` report, include:

- Claims audited, split by evidence tier (behavioral_probe vs code_read).
- Verdict tally (`TRUE` / `FALSE` / `UNDERSPECIFIED` / `EXCEEDS_SCOPE` /
  `UNVERIFIABLE`).
- Lanes run, skipped, or serialized, with reason.
- Prose-wrong contract edits applied, with the re-validated floor result.
- Code-wrong findings deferred, with `file:line` / envelope excerpt and backlog
  IDs created.
- Any capability change (a rite that gained or lost the envelope since the last
  pass, since the probe set is derived at runtime).

State plainly which `TRUE` verdicts are probe-backed and which are read-only.

## Verdict schema

Each lane returns one object per claim, for machine aggregation:

- `claim_id`, `contract`, `subject`, `field`
- `prose_claim` - the contract sentence under audit
- `evidence_type` - `behavioral_probe` or `code_read`
- `probe_invocation`, `envelope_excerpt` - for probed claims
- `code_evidence` - `file:line` for read claims
- `verdict` - `TRUE` / `FALSE` / `UNDERSPECIFIED` / `EXCEEDS_SCOPE` / `UNVERIFIABLE`
- `drift_kind`, `fix_target` (`prose` / `code` / none), `proposed_fix`, `blast_radius`

## What this invocation is NOT

- **Not the mechanical floor.** `command_surface.py`, `rite_profiles.py`, and
  `validate_skill_refs.py` own existence, type, enum, path resolution,
  uniqueness, set completeness, and the static `mutation_profile` <-> `profile`
  join; they treat the prose as opaque. This pass reads what the prose says.
- **Not `validate_rites`** ([[invocations/arc/quality/validate_rites|validate
  rites]], Phase 4), which judges rite **script quality** - docstrings, error
  handling, exit codes, portability, size. Idempotency appears in both passes,
  but here it is read as a contract claim, not re-reviewed as script quality;
  code-wrong findings are handed back to Phase 4, not re-reviewed here.
- **Not `review_architecture`**
  ([[invocations/arc/quality/review_architecture|review architecture]], Phase
  3), which audits layout, source-of-truth ownership, and read paths, and at the
  command surface checks only that each command has one workflow home. This pass
  goes one level deeper: not "does each command have one home?" but "does each
  contract field tell the truth about that home's behavior?"

## Related

- Orchestrator: [[invocations/arc/improve_arcana|improve arcana]]
- Rite quality (Phase 4): [[invocations/arc/quality/validate_rites|validate rites]]
- Architecture review (Phase 3): [[invocations/arc/quality/review_architecture|review architecture]]
- Command-surface contract: [[docs/command_surface|command surface]]
- Rite-profile contract: [[docs/rite_profiles|rite profiles]]
- Script vs AI split: [[docs/script_vs_ai|script vs ai]]
- Deferred queue: [[docs/architecture_backlog|architecture backlog]]
