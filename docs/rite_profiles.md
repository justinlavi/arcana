---
type: reference
title: "Mutating Rite Profiles"
aliases: ["rite-profiles", "mutation-profiles", "plan-apply-profile"]
tags: [type/reference, arcana/docs, scope/rites]
authority: grimoire
last_verified: 2026-05-25
---

# Mutating Rite Profiles

Arcana's write-capable rite contract lives in
[`../rites/data/rite_profiles.json`](../rites/data/rite_profiles.json).
That file names each rite that writes durable state or managed transient
artifacts, the mode it uses, what it writes, and how to validate it.

## Profiles

| Profile | Meaning |
|---|---|
| `read_only` | Does not change durable Arcana, grimoire, or user state. Managed transient artifacts must be named. |
| `plan_apply` | Has a planning command and an apply command. The plan must be specific enough to summarize before writing. |
| `apply_only` | Writes only through an explicit operation where a separate plan is not useful. The scope and refusal behavior must be clear. |
| `append_only` | Appends one record to an append-only target. Invocation workflows own when one append is warranted. |

## Current Write-Capable Rites

| Rite | Profile | Plan command | Apply command | Writes |
|---|---|---|---|---|
| `rites/adopt_grimoire.py` | `apply_only` | none | `python rites/adopt_grimoire.py <directory> --skill-prefix <prefix> --description "<description>"` | `<target grimoire>/grimoire.json` |
| `rites/append_log.py` | `append_only` | none | `python rites/append_log.py --grimoire <path> --op <op> --title "<title>"` | `<grimoire>/log.md` |
| `rites/build_summon_binary.py` | `apply_only` | none | `python rites/build_summon_binary.py` | build artifacts, release archives, checksum files |
| `rites/clean_artifacts.py` | `plan_apply` | `python rites/clean_artifacts.py --dry-run` | `python rites/clean_artifacts.py` | `rites/.artifacts` directories |
| `rites/new_page.py` | `plan_apply` | `python rites/new_page.py --grimoire <path> --path chapters/<chapter>/<slug>.md --type <type> --title "<title>"` | `python rites/new_page.py --grimoire <path> --path chapters/<chapter>/<slug>.md --type <type> --title "<title>" --apply` | a new `<grimoire>/chapters/<chapter>/<slug>.md` page |
| `rites/sync_skills.py` | `plan_apply` | `python rites/sync_skills.py --dry-run` | `python rites/sync_skills.py` | supported agent skill directories |
| `rites/repair_links.py` | `plan_apply` | `python rites/repair_links.py --grimoire <path>` | `python rites/repair_links.py --grimoire <path> --apply` | active-grimoire Markdown files |
| `rites/summon.sh` | `apply_only` | none | `bash rites/summon.sh` | install tree, selected grimoires, library, agent files |
| `rites/summon_core.py` | `apply_only` | none | `python rites/summon.py` | install tree, selected grimoires, library, agent files |
| `rites/summon_gui.py` | `apply_only` | none | `python rites/summon.py --gui` | GUI settings, install tree, selected grimoires, library, agent files |
| `rites/sync_docs.py` | `plan_apply` | `python rites/sync_docs.py` | `python rites/sync_docs.py --apply` | `docs/skills.md` |
| `rites/sync_library.py` | `plan_apply` | `python rites/sync_library.py` | `python rites/sync_library.py --apply` | `~/grimoires/library.json` |
| `rites/update_grimoires.py` | `plan_apply` | `python rites/summon.py --update` | `python rites/summon.py --update --apply` | grimoire working trees (fast-forward-only pulls) and Arcana-owned managed scaffold during heal |
| `rites/validate.py` | `read_only` | none | `python rites/validate.py --parallel` | transient validator reports under `rites/.artifacts` |

## Rules

- Any new top-level rite that writes files, directories, build artifacts,
  agent files, install state, or managed transient artifacts must be added to
  `rites/data/rite_profiles.json`.
- A `plan_apply` rite must name both commands. If its default mode writes, it
  must also provide a preview flag such as `--dry-run`.
- An `apply_only` rite must refuse unsafe overwrites or make its replacement
  scope explicit.
- An `append_only` rite is intentionally not idempotent; the invocation that
  calls it must ensure there is one append per completed operation.
- A `read_only` rite may refresh named transient artifacts, but it must not
  change durable source, grimoire, agent, library, or install state.
- `rites/sync_skills.py` stamps generated `SKILL.md` files with
  `ARCANA_SKILL_OWNERSHIP`; cleanup and overwrites are allowed only when that
  marker or generated provenance proves Arcana ownership.

## Related

- Script vs AI split: [script vs ai](script_vs_ai.md)
- Rite quality review: [validate rites](../invocations/arcana/quality/validate_rites.md)
- Rite profile helper: [`../rites/rite_profiles.py`](../rites/rite_profiles.py)
