# Arcana Governance

## Purpose

Defines how **Arcana** itself is maintained, versioned, and updated to keep all installed grimoires in sync.

This is for the *Arcana maintainer* — the person who owns the Arcana fork your domain grimoires reference. If you are only writing chapters in a domain grimoire, you don't need this document.

---

## Core Principle

**Arcana is the single source of truth for the system.** Domain grimoires *reference* Arcana — they don't copy from it.

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

## What Belongs in Arcana

### ✅ Universal content (Arcana)

Include in Arcana if it applies to **every** grimoire that references it:

- **Documentation**: README, installation, quickstart, operating model, reference, governance.
- **Invocations**: domain operations (create-grimoire, create-chapter, improve), Arcana maintenance (validators, quality), meta (help).
- **Formulae**: chapter-index, page, invocation, grimoire scaffolding.
- **Rites**: validation, registration, library sync, etc.
- **Resources**: branding assets.

### ❌ Domain-specific content

Do **not** include in Arcana:

- Chapters specific to one subject area (recipes, HR policies, codebase structure, …).
- Skills specific to one domain (those live under `<grimoire>/skills/`, namespaced by the grimoire's manifest).
- Custom rites only one grimoire uses.
- Real-world data: company names, project names, employee data, customer data, credentials.

**Where these belong**: in the relevant `<grimoire>-grimoire/chapters/` or `<grimoire>-grimoire/skills/`.

---

## Versioning

Arcana follows [Semantic Versioning 2.0.0](https://semver.org/) — `MAJOR.MINOR.PATCH`.

| Bump | Trigger | Examples |
|---|---|---|
| **PATCH** (`v1.0.0 → v1.0.1`) | Bug fixes, typo corrections, doc clarifications | Fix a typo, repair a broken link, fix a rite that errors on edge cases |
| **MINOR** (`v1.0.0 → v1.1.0`) | New features, additions, improvements (backward compatible) | New formula, new validator, new optional skill |
| **MAJOR** (`v1.0.0 → v2.0.0`) | Breaking changes — downstream grimoires must adapt | Renamed file, restructured router, removed skill, changed manifest schema |

The current version lives in three places:
- `VERSION` (single source of truth)
- `CHANGELOG.md` (entry per release)
- Git tags (`v1.x.y`)

---

## Change Workflow

### Patch / Minor

1. Make changes; run `/grm-arcana-validate-all` (or `python3 rites/validate.py`).
2. Add a `CHANGELOG.md` entry under `[Unreleased]`.
3. Commit (`fix:` for patch, `feat:` for minor).
4. Tag and push.

### Major (Breaking)

1. Document the proposed change and the migration path *before* implementing.
2. Mark anything being removed as deprecated for at least one minor release first (see [Deprecation](#deprecation-policy)).
3. Implement the change. Run the full validator suite.
4. Add a `CHANGELOG.md` entry. Use the `### Removed (breaking)` heading and write a migration recipe inline.
5. If the change requires user-side action (e.g. running a migration rite), state the command explicitly.
6. Commit (`BREAKING:` prefix), tag, push.

For an example of a clean breaking-change entry, see the `~/grimoire/` → `~/grimoires/` rename in `CHANGELOG.md`.

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
- ✅ Pass the full validator suite (`/grm-arcana-validate-all`) before commit.

Arcana files must **not**:

- ❌ Contain hardcoded user paths or machine-specific values.
- ❌ Reference real grimoire content (chapter contents, real policy text, real recipes).
- ❌ Include secrets, credentials, PII, or proprietary data.
- ❌ Break existing grimoires without a deprecation cycle.

---

## Domain Grimoire Responsibilities

Each domain grimoire is responsible for:

1. **Its own content**: chapters, skills, manifest. Use Arcana's `/grm-domain-create-chapter` and the page formula for new pages.
2. **Staying in step with Arcana**: pull updates periodically; run `/grm-domain-validate-structure` after pulling.
3. **Reporting issues** in Arcana itself (broken invocations, formula bugs, validator false positives).

Domain grimoires must **not**:

- ❌ Copy Arcana files into their own repo (reference instead).
- ❌ Modify Arcana files directly. Propose changes to the maintainer of the Arcana fork they use.
- ❌ Create chapters / formulae / rites in Arcana folder names (`invocations/`, `formulae/`, `rites/`) inside their own grimoire — those folder names are reserved for Arcana.
- ❌ Ignore breaking-change announcements. Re-run `/grm-domain-validate-structure` after a major Arcana version bump.

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
