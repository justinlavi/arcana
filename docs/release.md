---
type: reference
title: "Release Workflow"
aliases: ["release", "tag-release"]
tags: [type/reference, arcana/docs]
authority: grimoire
last_verified: 2026-11-11
---

# Arcana Release Guide

How to cut an Arcana release. Arcana ships as source: a release is a tag on
the repository, and every install path (the summoning rite, `/grm-update`,
manual clone) reads that source directly. There are no built binaries and no
packaged artifacts to publish; the PyInstaller release pipeline and its GitHub
Actions workflow were removed in 1.8.0.

The canonical installer behavior contract lives in
[summoning contract](summoning_contract.md), backed by
`rites/data/summon_contract.json`.

---

## Choosing the Version

Decide the new `vMAJOR.MINOR.PATCH` number with the [Compatibility Rule](governance.md#the-compatibility-rule) **before** tagging - the bump is determined by compatibility, not by how big the release feels:

- **PATCH** - fixes and wording only; no behavior change.
- **MINOR** - existing grimoires stay valid (no migration), but Arcana now generates, validates, or guides future grimoires differently.
- **MAJOR** - a compatibility break: prior grimoires become invalid or must be migrated.

Many backward-compatible releases (`v1.0.0 -> v1.17.0`) do not become `v2.0.0`; only a compatibility break does. The full policy and the agent decision procedure live in [governance -> Versioning](governance.md#versioning).

---

## Release Steps

1. **Gate.** On the release branch run the fast test gate and the validator
   orchestrator; both must be green on Linux and Windows (CI runs both):

   ```bash
   python -m pytest -q
   python rites/validate.py --summary
   ```

2. **Changelog.** Turn the `[X.Y.Z] - Unreleased` heading in `CHANGELOG.md`
   into the release date and make sure every user-visible change is listed
   under Added / Changed / Fixed / Removed.

3. **Version.** Set `VERSION` and the `version` field in `pyproject.toml` to
   the new number. `/grm-update` and `summon.py --check` report this value.

4. **Merge and tag.** Merge the release branch into `main`, then tag:

   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin main vX.Y.Z
   ```

5. **Verify the install path.** From a machine or a scratch home directory
   without Arcana, run the public one-liner and confirm it installs the tagged
   source, injects the routing block, and registers skills:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash
   python3 ~/grimoires/arcana/rites/summon.py --check
   ```

6. **Announce.** Existing installs pick the release up with `/grm-update`
   (or `/arc-update`), which pulls `main`, validates, re-registers skills,
   refreshes routing blocks, and heals every grimoire it confirmed current.

---

## Forks and Private Mirrors

A company that mirrors Arcana into a private host releases the same way: tag
the mirror and point installs at it with `ARCANA_URL`. See
[installation](installation.md#summoning-rite) for the one-liner form and
[summoning contract](summoning_contract.md#bootstrap-environment-controls)
for the environment variables the bootstrap honors.
