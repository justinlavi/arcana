---
type: hub
title: "Arcana"
aliases: ["arcana-root", "grimoire-arcana"]
tags: [grimoire/grm, type/hub, hub/root]
---

# Arcana

Meta-knowledge about Grimoire itself — invocations, formulae, rites, and governance. For domain knowledge, route to your grimoire's own root hub instead.

Arcana is the engine. Every grimoire references it; nothing copies it.

## Read Model

- Hub convention: every folder F has a hub at `F/<basename(F)>.md`. A hub may route to sub-hubs, to leaves, or both. Depth is open-ended — `arcana.md` → `<area>.md` → … → leaf, however deep the topic warrants.
- Page schema (frontmatter, types, authority): [docs/page_schema.md](docs/page_schema.md).
- Layers: `sources/` (immutable source artifacts), `inbox/` (transient drop zone), `chapters/`-equivalent content under `docs/` `invocations/` `formulae/`, `log.md` for activity.

## Documentation

- [README.md](README.md) — Overview and architecture
- [docs/installation.md](docs/installation.md) — Summoning rite + manual install
- [docs/quickstart.md](docs/quickstart.md) — 5-minute smoke test after install
- [docs/agent_configuration.md](docs/agent_configuration.md) — Per-agent setup (Claude / Codex / Copilot)
- [docs/skills.md](docs/skills.md) — Canonical Arcana skill catalog (auto-generated)
- [docs/reference.md](docs/reference.md) — Terminology, library/manifest schemas, path keys, formula placeholders
- [docs/operating_model.md](docs/operating_model.md) — Storage layers and routing
- [docs/page_schema.md](docs/page_schema.md) — Frontmatter spec for every page
- [docs/obsidian.md](docs/obsidian.md) — Vault setup and graph-view color groups
- [docs/script_vs_ai.md](docs/script_vs_ai.md) — When to use scripts vs AI
- [docs/governance.md](docs/governance.md) — Maintenance policies and versioning
- [docs/release.md](docs/release.md) — Release workflow for Summoning Rite binaries
- [CHANGELOG.md](CHANGELOG.md) — Version history

## Invocations

**Grimoire (domain operations)** — see [invocations/grimoire/grimoire.md](invocations/grimoire/grimoire.md):

- [create_grimoire.md](invocations/grimoire/create_grimoire.md) — `/grm-domain-create-grimoire`
- [create_chapter.md](invocations/grimoire/create_chapter.md) — `/grm-domain-create-chapter`
- [ingest.md](invocations/grimoire/ingest.md) — `/grm-domain-ingest`
- [file_answer.md](invocations/grimoire/file_answer.md) — `/grm-domain-file-answer`
- [lint.md](invocations/grimoire/lint.md) — `/grm-domain-lint`
- [improve_grimoire.md](invocations/grimoire/improve_grimoire.md) — `/grm-domain-improve`
- [analyze_semantics.md](invocations/grimoire/analyze_semantics.md) — `/grm-domain-analyze-semantics`
- [validate_structure.md](invocations/grimoire/validate_structure.md) — `/grm-domain-validate-structure`

**Arcana (maintainer only)** — see [invocations/arcana/arcana.md](invocations/arcana/arcana.md):

- [improve_arcana.md](invocations/arcana/improve_arcana.md) — `/grm-arcana-improve`
- [validate_boundaries.md](invocations/arcana/validate_boundaries.md) — `/grm-arcana-validate-boundaries`
- Validators hub: [invocations/arcana/validators/validators.md](invocations/arcana/validators/validators.md)
- Quality hub: [invocations/arcana/quality/quality.md](invocations/arcana/quality/quality.md)

**Meta** — see [invocations/meta/meta.md](invocations/meta/meta.md):

- [help.md](invocations/meta/help.md) — `/grm-meta-help`
- [base_invocation.md](invocations/meta/base_invocation.md)

## Formulae

- [formulae/grimoire/](formulae/grimoire/) — Full grimoire scaffold (copy for new domains)
  - [formulae/grimoire/root_hub.formula.md](formulae/grimoire/root_hub.formula.md) — Root-hub template (becomes `<grimoire>/<grimoire>.md`)
- [formulae/chapter_hub.formula.md](formulae/chapter_hub.formula.md) — Chapter hub template
- [formulae/page.formula.md](formulae/page.formula.md) — Knowledge page template
- [formulae/invocation.formula.md](formulae/invocation.formula.md) — Custom invocation template
- [formulae/log_entry.formula.md](formulae/log_entry.formula.md) — `log.md` entry shape
- [formulae/source.formula.md](formulae/source.formula.md) — Source artifact template

## Skills

- [docs/skills.md](docs/skills.md) — Canonical Arcana skill catalog (auto-generated)
- [skills/](skills/) — Skill source directory; registered via `rites/register_skills.py`

## Rites

- [rites/summon.sh](rites/summon.sh) — One-command summoning
- [rites/register_skills.py](rites/register_skills.py) — Skill registration
- [rites/sync_library.py](rites/sync_library.py) — Library reconciliation
- [rites/sync_docs.py](rites/sync_docs.py) — Generate `docs/skills.md`
- [rites/adopt_grimoire.py](rites/adopt_grimoire.py) — Manifest writer for unmanaged dirs
- [rites/append_log.py](rites/append_log.py) — Append to a grimoire's `log.md`
- [rites/validate.py](rites/validate.py) — Orchestrator for the full validator suite
- Validators: `rites/validate_<aspect>.py` (structure, naming, semantics, format, links, security, skill-refs, frontmatter, orphans, provenance)
- [library.json](library.json) — Discoverable grimoires shipped with this Arcana

## Resources

- [resources/](resources/) — Branding assets
