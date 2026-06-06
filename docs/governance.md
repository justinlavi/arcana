---
type: reference
title: "Arcana Governance"
aliases: ["governance", "release-policy"]
tags: [type/reference, arcana/docs]
authority: grimoire
last_verified: 2026-05-25
---

# Arcana Governance

## Purpose

Defines how **Arcana** itself is maintained, versioned, and updated to keep all installed grimoires in sync.

This is for the *Arcana maintainer* - the person who owns the Arcana fork your grimoires reference. If you are only writing chapters in a grimoire, you don't need this document.

---

## Core Principle

**Arcana is the single source of truth for the system.** Grimoires *reference* Arcana - they don't copy from it.

Updates to Arcana propagate to every grimoire that points at the same installation. Breaking changes follow a deprecation protocol so downstream grimoires can adapt.

---

## Arcana Maintainer

The Arcana maintainer is whoever owns the Arcana fork others reference. For a personal install that's you; for a shared fork it's whoever the contributors agreed on.

**Responsibilities**:
- Maintain universal invocations, formulae, rites, and documentation.
- Review and approve changes to Arcana.
- Cut versioned releases and maintain `CHANGELOG.md`.
- Provide migration guides for breaking changes (see [Deprecation](#deprecation-policy)).
- Triage feedback from grimoire authors and incorporate improvements.

The role is transferable — record handovers in the CHANGELOG.

---

## Autonomous Maintainer

Arcana is built to be kept current by an agent, not only a person. The
machine-readable signals the system emits — validator diagnostics, the
mutating-rite result envelopes (`--format json`), and the contract-coherence
audit — let an agent **verify its own work**, which is what makes unattended
maintenance safe.

"Autonomous" means *no prior approval is needed*, never *invisible*: every
unattended action is recorded (an Arcana-visible change in `CHANGELOG.md` under
`[Unreleased]`; a grimoire operation in `log.md`), and the rite envelopes leave a
machine-readable trail.

### The unattended-safe gate

An agent may act **unattended** only when all four conditions hold:

1. **Deterministic** — the change is mechanical (a fix with one correct form), or
   a prose-wrong contract fix the
   [contract-coherence audit](../invocations/arc/quality/audit_contract_coherence.md)
   flagged: a verifiable claim about the code, edited in contract data only, with
   code-wrong findings deferred. A content change that needs a judgment call is
   not deterministic — propose it instead.
2. **Verifiable** — `python3 rites/validate.py` exits 0 afterward, or the rite's
   `--format json` envelope reports the expected `status` and `mutations`.
3. **Non-destructive** — it deletes no unowned content and is reversible through
   git.
4. **Not on the human-sign-off list** below.

If any condition fails, the change is **proposed**, not applied: surface it for
one confirmation (the `/grm-health-check` model) or escalate to the
human maintainer.

### Unattended

| Action | Rite / command | Verification |
|---|---|---|
| Run the validator suite | `/arc-validate` (`python3 rites/validate.py`) | exit 0 |
| Apply mechanical fixes (broken links the rite located, format, frontmatter, encoding, snake_case) | an `/arc-validate` finding plus a direct edit | re-run the validator to exit 0 |
| Repair unambiguous wikilinks | `/grm-repair-links --apply` | envelope `status` `ok`; ambiguous links are surfaced, never guessed |
| Regenerate generated indexes | `python3 rites/sync_docs.py --apply` | drift gate clean afterward |
| Correct prose-wrong contract drift | the contract-coherence audit | the originating probe plus a validator pass |
| Append the changelog | edit `CHANGELOG.md` under `[Unreleased]` | — |
| Append a grimoire log entry | `append_log` | envelope: one `append` mutation |

### Propose, then apply on one confirmation

Reversible but judgment-bearing, or writing outside the repo:

- Orphan wiring, terminology standardization, page promotion, merging duplicates.
- Any change touching more than ten files.
- Reconciling the grimoire library or registering skills into agent directories
  under the user's home (`/arc-sync library`, `/arc-sync skills`,
  `/grm-sync`).

### Human sign-off required

- **Version bumps and release tags** — semver decisions across `VERSION`,
  `CHANGELOG.md`, and git tags, decided by the [Compatibility Rule](#the-compatibility-rule)
  (compatibility, not change size) — see [Versioning](#versioning) and
  [Change Workflow](#change-workflow).
- **Breaking changes** and **deprecations** (see
  [Deprecation Policy](#deprecation-policy)). Never break a grimoire without a
  deprecation cycle.
- **Deleting or removing content**, changing the public command surface, or any
  force-overwrite.
- **Running the installer** against a real environment, and **transferring the
  maintainer role**.

### In every tier

- **Never auto-delete unowned content.** Skill cleanup removes only Arcana-owned,
  generated-provenance directories; everything else is preserved.
- **Leave the tree green.** An unattended pass that cannot return
  `python3 rites/validate.py` to exit 0 reverts its change and surfaces the
  problem instead.
- **Record what was done** — unattended is not unlogged.

The skill layer already encodes part of this: destructive and maintainer-only
skills set `disable-model-invocation: true` so an agent will not auto-invoke them
(see [agent configuration](agent_configuration.md)); propose-tier commands stay
auto-invocable — the propose-then-confirm step gates the apply, not whether an
agent may surface the command. The safety posture of every command lives in the
[command surface](command_surface.md) and [rite profiles](rite_profiles.md)
contracts.

---

## What Belongs in Arcana

### ✅ Universal content (Arcana)

Include in Arcana if it applies to **every** grimoire that references it:

- **Documentation**: README, installation, operating model, reference, governance.
- **Invocations**: grimoire operations (`invocations/grm/`), Arcana maintenance (`invocations/arc/`, with sync, adopt, clean, validators, and quality sub-areas), and shared meta fragments (`invocations/meta/`).
- **Formulae**: grimoire scaffold, chapter hubs, pages, sources, log entries, and invocation skeletons.
- **Rites**: validation, registration, library sync, etc.
- **Resources**: branding assets.

### ❌ Domain-specific content

Do **not** include in Arcana:

- Chapters specific to one subject area (recipes, HR policies, codebase structure, ...).
- Skills specific to one domain (those live under `<grimoire>/skills/`, prefixed by the grimoire's manifest).
- Custom rites only one grimoire uses.
- Real-world data: company names, project names, employee data, customer data, credentials.
- Grimoire storage layers at Arcana root (`chapters/`, `sources/`, `inbox/`, `log.md`). Arcana keeps their templates under `formulae/grimoire/`.

**Where these belong**: in the relevant `<grimoire>-grimoire/chapters/` or `<grimoire>-grimoire/skills/`.

---

## Versioning

Arcana follows [Semantic Versioning 2.0.0](https://semver.org/) — `MAJOR.MINOR.PATCH` — read through a framework-specific lens. Arcana is a **grimoire-generation framework**, so a change is judged by its effect on grimoires — both the ones already on disk and the future ones an AI agent will generate — not by how large, ambitious, or impactful the change feels.

### The Compatibility Rule

**Compatibility decides the bump — not the size or perceived importance of the change.** Answer two questions, in order:

1. **Do existing grimoires stay valid?** Does any grimoire already on disk break, fail validation, or need a hand-migration self-healing cannot perform because of this change? (See [Self-healing and the compatibility line](#self-healing-and-the-compatibility-line) — an auto-healable transition does not count as a break.)
2. **Does future generation behavior change?** Will Arcana now generate, validate, or guide grimoires differently going forward?

The answers map straight to the bump:

| Existing grimoires… | Future generation… | Bump |
|---|---|---|
| stay valid (no migration) | unchanged | **PATCH** |
| stay valid (no migration) | improves or changes | **MINOR** |
| would break, but Arcana can **auto-heal** them (a rite, `/grm-update`, or a documented [Update](../UPDATE.md) step) | (either) | **MINOR** — ship the heal |
| break and need **manual, judgment-bearing** migration that self-healing cannot perform | (either) | **MAJOR** |

"Existing grimoires" means **every grimoire the change could affect, not only the ones you can currently see** — compatibility is about the validation *outcome*, so a grimoire that validated yesterday and fails today is broken even if no file or schema changed. On a shared Arcana fork you often cannot enumerate downstream private grimoires; when that coverage is unknown, treat a newly-enforcing check as potentially breaking (ship it warn-only first, or lean MAJOR) rather than assuming MINOR.

Two consequences of this rule are easy to get wrong:

- **Many minors do not add up to a major.** A long run of backward-compatible releases — `v1.0.0 → v1.17.0` — can leave Arcana dramatically more capable than it started and it is still `1.x`, as long as every existing grimoire stayed valid the whole way. A major version is **not** "enough minors accumulated"; it is a specific event — a compatibility break. Signal a big leap in the `CHANGELOG` / release notes, never by inflating MAJOR.
- **Smarter future grimoires are usually MINOR.** Better formulae, improved standards, smarter AI guidance, new or additively-stricter validators, refined generation behavior — these change what *future* grimoires look like while leaving *existing* ones valid. That is the textbook MINOR, not a MAJOR.

### Self-healing and the compatibility line

Arcana is built to be **self-healing**: a grimoire is brought current not by hand but by Arcana's own update path — the mechanical repair rites, `/grm-update` (which re-syncs the managed scaffold), and, when the installed skills are themselves too old to run, the skill-less [Update](../UPDATE.md) procedure. The update first **pulls every grimoire in the library** and heals only the ones it confirmed current, so a grimoire whose fix already exists upstream is fast-forwarded rather than re-derived locally. That sharpens where the MINOR/MAJOR line falls, and it is *why* "must migrate" in the table above means **must migrate by hand**:

- A transition Arcana can perform **automatically and deterministically** — re-syncing managed scaffold, refreshing the README update block, or repairing wikilinks — is **not** a manual migration. If every existing grimoire can be healed to current with no human judgment, the change is **MINOR**, even though grimoire files change in the heal.
- **The obligation rides with the change author: ship the heal with the change.** A change that would otherwise break grimoires must land together with the heal that fixes them — the update rite's mechanical pass and/or the grimoire formula, so the update converges any grimoire to current. An un-shipped heal is theoretical — without it, the change is a real break (MAJOR).
- A change is **MAJOR** only when bringing grimoires current needs **human judgment** — content or semantics a rite cannot supply. If you can automate the heal, automate it and ship MINOR; if you genuinely cannot, it is MAJOR.

**Whenever a change alters what a current grimoire must look like, make the update rite bring it there** — extend the mechanical heal and the formula so any grimoire converges to current from the source tree alone, even when its installed skills are too stale to run. Record *what* changed in [the changelog](../CHANGELOG.md), not as steps in the update procedure.

### What each bump means for Arcana

**PATCH** (`v1.0.0 → v1.0.1`) — no behavior change; neither existing nor future grimoires change in substance.
- Typo and wording fixes, broken-link repairs, small documentation clarifications.
- Validator or rite **bug** fixes that correct an implementation without changing intended behavior — but only if the fix does not flip the pass/fail verdict of any existing grimoire. A crash-fix that makes a grimoire the validator never actually evaluated start failing is a break; treat it as MAJOR.

**MINOR** (`v1.0.0 → v1.1.0`) — existing grimoires stay valid; future grimoires improve or change.
- A new formula, a new optional skill, a new validator (or a stricter check that every grimoire already on disk still passes — if a stricter check makes existing grimoires fail, that is MAJOR).
- Improved standards, better AI guidance, a sharpened convention that newly-generated grimoires follow.
- *Worked example:* refining a grimoire's free-form activity log into a structured **content change log** — so future grimoires record meaningful content changes instead of VCS or development noise — changes future AI behavior and the shape of future generated grimoires, so it is more than a PATCH; but because existing grimoires remain valid and need no migration, it is a **MINOR**, not a MAJOR.

**MAJOR** (`v1.0.0 → v2.0.0`) — a compatibility break: existing grimoires become invalid or must be migrated **by hand** because self-healing cannot bring them current (see [Self-healing and the compatibility line](#self-healing-and-the-compatibility-line)).
- Removing a concept, renaming a required file, or changing a schema (page frontmatter, the manifest, a contract) such that prior grimoires no longer validate **and no rite can mechanically migrate them**.
- Any change that forces downstream grimoires into a **manual, judgment-bearing** migration or hand-edit that self-healing cannot perform.
- A new or stricter validator/check that makes any existing grimoire **fail validation** — even when no file, schema, or concept changed (the break is in the validation outcome). To tighten validation *without* a hard break, ship the check **warn-only in a MINOR first, then enforce it in the next MAJOR** — the deprecation cycle applied to validation.
- Removing a deprecated capability (deprecations land in a MINOR first — see [Deprecation Policy](#deprecation-policy)).

### Before you change the version (humans and AI agents)

A version bump is **human-sign-off territory** (see [Autonomous Maintainer](#autonomous-maintainer)). Before touching `VERSION`, `CHANGELOG.md`, or release notes — whether you are a human or an AI agent working in this repo — consult this section and reason the bump through explicitly:

1. **Inspect the nature of the change**, not its size. What actually changed in framework behavior?
2. **Ask: do existing grimoires stay valid?** If none break, you are in PATCH/MINOR territory.
3. **If some would break, ask: can Arcana auto-heal them** through the update rite's mechanical pass (scaffold re-sync, README block, link repair) or the formula? If yes, **ship the heal** → **MINOR**. If healing needs human judgment → **MAJOR**.
4. If **no migration** is required but **future generation behavior improves or changes** → **MINOR**.
5. If only wording or fixes changed with **no behavior change** → **PATCH**.
6. When torn between MINOR and MAJOR, the deciding test is **how the heal happens**: *no migration, or one Arcana can auto-heal (the update rite / formula), ⇒ MINOR; a migration needing human judgment ⇒ MAJOR*.

The current version lives in three places that must agree:
- `VERSION` (single source of truth)
- `CHANGELOG.md` (entry per release)
- Git tags (`v1.x.y`)

---

## Change Workflow

Decide the bump with the [Compatibility Rule](#the-compatibility-rule) first, then follow the path below for that bump.

### Patch / Minor

1. Make changes; run `/arc-validate` (or `python3 rites/validate.py`).
2. Update `CHANGELOG.md`. Before the first tag for a version, edit that version's entry as the current state. After a version is tagged, collect future changes under `[Unreleased]` until the next release entry is cut.
3. Commit (`fix:` for patch, `feat:` for minor).
4. Tag and push when cutting the release.

### Major (Breaking)

1. Document the proposed change and the migration path *before* implementing.
2. Mark anything being removed as deprecated for at least one minor release first (see [Deprecation](#deprecation-policy)).
3. Implement the change. Run the full validator suite.
4. Add a `CHANGELOG.md` entry. Use the `### Removed (breaking)` heading and write a migration recipe inline.
5. If the change requires user-side action (e.g. running a migration rite), state the command explicitly.
6. Commit (`BREAKING:` prefix), tag, push.

---

## Deprecation Policy

When removing or replacing Arcana content:

1. **Mark deprecated** in a minor release. Add a note at the top of the file (or a `Deprecated:` row in the relevant table) stating the replacement and the planned removal version.
2. **Announce** in the `CHANGELOG.md` entry under `### Deprecated`. Include the migration path.
3. **Remove** in a major release. Delete the deprecated content; update every reference; document the removal under `### Removed (breaking)`.

**Minimum window**: at least one minor release between deprecation and removal.

---

## Quality Standards

Arcana files must:

- ✅ Apply universally — no domain-specific content (see [What Belongs in Arcana](#what-belongs-in-arcana)).
- ✅ Use generic example names (`cooking-grimoire`, `hr-grimoire`, `Domain A`, `Project Alpha`, `Alice/Bob`). Real product/company/person names appear only when documenting an actual integration.
- ✅ Use relative paths inside the repo. Use `{{ARCANA_PATH}}` / `{{GRIMOIRE_PATH}}` placeholders in skill files; the registration rite resolves them.
- ✅ Preserve the text file standard: UTF-8 without BOM, LF line endings, and no mojibake or repair artifacts. Unicode is allowed when it improves readability.
- ✅ Pass the full validator suite (`/arc-validate`) before commit.

Arcana files must **not**:

- ❌ Contain hardcoded user paths or machine-specific values.
- ❌ Reference real grimoire content (chapter contents, real policy text, real recipes).
- ❌ Include secrets, credentials, PII, or proprietary data.
- ❌ Break existing grimoires without a deprecation cycle.

---

## Grimoire Responsibilities

Each grimoire is responsible for:

1. **Its own content**: chapters, skills, manifest. Use Arcana's `/grm-add` and the page formula for new pages.
2. **Staying in step with Arcana**: pull updates periodically; run `/grm-validate` after pulling.
3. **Reporting issues** in Arcana itself (broken invocations, formula bugs, validator false positives).

Grimoires must **not**:

- ❌ Copy Arcana files into their own repo (reference instead).
- ❌ Modify Arcana files directly. Propose changes to the maintainer of the Arcana fork they use.
- ❌ Create chapters / formulae / rites in Arcana folder names (`invocations/`, `formulae/`, `rites/`) inside their own grimoire — those folder names are reserved for Arcana.
- ❌ Ignore breaking-change announcements. Re-run `/grm-validate` after a major Arcana version bump.

---

## Security

Arcana is meant to be public-friendly. Whether a fork lives on github.com, a private GitLab, or a corporate-internal git host, the same rules apply:

- ❌ Never commit credentials, tokens, API keys, PII, customer data, or proprietary information to Arcana.
- ✅ When pages need to reference where sensitive data lives, point to the external system *by name and location*, never with the data inline:
  ```markdown
  ## Primary Sources
  - Production credentials: secrets manager → path/to/secret (auth required)
  - User contact data: CRM / identity provider (auth required)
  ```
- Read/write access to the Arcana repo is whatever your fork's git host enforces. The maintainer decides who can merge.
