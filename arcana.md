---
type: hub
title: "Arcana"
aliases: ["arcana-root", "grimoire-arcana"]
tags: [arcana/root, type/hub, hub/root]
---

# Arcana

Meta-knowledge about Arcana itself — invocations, formulae, rites, and governance. For grimoire knowledge, route to the grimoire's own root hub instead.

Arcana is the engine. Every grimoire references it; nothing copies it.

## Read Model

How Arcana is laid out — for the rules themselves, follow the links:

- Routing: hub-per-folder, open-ended depth. Full rules in [docs/operating_model.md](docs/operating_model.md).
- Frontmatter: type / authority / sources / last_verified. Spec in [docs/page_schema.md](docs/page_schema.md).
- Arcana is the engine layer: `docs/`, `invocations/`, `formulae`, `rites`, `skills`, and `resources`. Grimoire layers (`chapters/`, `sources/`, `inbox/`, `log.md`) are scaffolded by [formulae/grimoire/](formulae/grimoire/), not kept at Arcana root.

## Documentation

- [README.md](README.md) — Overview and architecture
- [docs/installation.md](docs/installation.md) — Summoning rite, manual install, 5-minute smoke test
- [docs/agent_configuration.md](docs/agent_configuration.md) — Per-agent setup (Claude / Codex / Copilot)
- [docs/skills.md](docs/skills.md) — Canonical Arcana skill catalog (auto-generated)
- [docs/skill_schema.md](docs/skill_schema.md) — Command-family skill naming schema
- [docs/command_surface.md](docs/command_surface.md) — Public command matrix validated by `/arc-validate-skill-refs`
- [docs/reference.md](docs/reference.md) — Terminology, library/manifest schemas, path keys, formula placeholders
- [docs/operating_model.md](docs/operating_model.md) — Storage layers and routing
- [docs/page_schema.md](docs/page_schema.md) — Frontmatter spec for every page
- [docs/obsidian.md](docs/obsidian.md) — Vault setup and graph-view color groups
- [docs/vscode.md](docs/vscode.md) — VS Code setup (uninstall Markdown Preview Enhanced + install Foam) to avoid recursive-directory bug on Ctrl-click
- [docs/script_vs_ai.md](docs/script_vs_ai.md) — When to use scripts vs AI
- [docs/rite_profiles.md](docs/rite_profiles.md) — Mutation profiles for write-capable rites
- [docs/architecture_backlog.md](docs/architecture_backlog.md) — Deferred S-tier architecture opportunities from `/arc-improve`
- [docs/governance.md](docs/governance.md) — Maintenance policies and versioning
- [docs/release.md](docs/release.md) — Release workflow for Summoning Rite binaries
- [CHANGELOG.md](CHANGELOG.md) — Version history

## Invocations

**Grimoire (grimoire operations)** — see [invocations/grimoire/grimoire.md](invocations/grimoire/grimoire.md):

- [create_grimoire.md](invocations/grimoire/create_grimoire.md) — `/grm-create`
- [create_chapter.md](invocations/grimoire/create_chapter.md) — `/grm-create-chapter`
- [update_arcana.md](invocations/grimoire/update_arcana.md) — `/grm-update-arcana`
- [register_skills.md](invocations/grimoire/register_skills.md) — `/grm-register-skills`
- [ingest.md](invocations/grimoire/ingest.md) — `/grm-ingest`
- [file_answer.md](invocations/grimoire/file_answer.md) — `/grm-file-answer`
- [lint.md](invocations/grimoire/lint.md) — `/grm-lint`
- [improve_grimoire.md](invocations/grimoire/improve_grimoire.md) — `/grm-improve`
- [analyze_semantics.md](invocations/grimoire/analyze_semantics.md) — `/grm-analyze-semantics`
- [validate_structure.md](invocations/grimoire/validate_structure.md) — `/grm-validate-structure`
- [validate_boundaries.md](invocations/grimoire/validate_boundaries.md) — `/grm-validate-boundaries`
- Validators hub: [invocations/grimoire/validators/validators.md](invocations/grimoire/validators/validators.md)

**Arcana (maintainer only)** — see [invocations/arcana/arcana.md](invocations/arcana/arcana.md):

- [improve_arcana.md](invocations/arcana/improve_arcana.md) — `/arc-improve`
- Validators hub: [invocations/arcana/validators/validators.md](invocations/arcana/validators/validators.md)
- Quality hub: [invocations/arcana/quality/quality.md](invocations/arcana/quality/quality.md)

**Agent** — see [invocations/agent/agent.md](invocations/agent/agent.md):

- [register_skills.md](invocations/agent/register_skills.md) — `/arc-agent-register-skills`
- [update_agent_block.md](invocations/agent/update_agent_block.md) — `/arc-agent-update`

**Library** — see [invocations/library/library.md](invocations/library/library.md):

- [sync.md](invocations/library/sync.md) — `/arc-library-sync`
- [adopt.md](invocations/library/adopt.md) — `/arc-library-adopt`

**Workspace** — see [invocations/workspace/workspace.md](invocations/workspace/workspace.md):

- [clean.md](invocations/workspace/clean.md) — `/arc-workspace-clean`

**Help**:

- [help.md](invocations/help/help.md) — `/arc-help`

**Meta support** — see [invocations/meta/meta.md](invocations/meta/meta.md):

- [base_invocation.md](invocations/meta/base_invocation.md)
- [grimoire_directory_guard.md](invocations/meta/grimoire_directory_guard.md)

## Formulae

- [formulae/grimoire/](formulae/grimoire/) — Full grimoire scaffold (copy for new domains)
  - [formulae/grimoire/root_hub.formula.md](formulae/grimoire/root_hub.formula.md) — Root-hub template (becomes `<grimoire>/<grimoire>.md`)
  - [formulae/grimoire/scaffold_contract.json](formulae/grimoire/scaffold_contract.json) — Machine-readable scaffold inventory used by creation, audit, validation, and tests
- [formulae/chapter_hub.formula.md](formulae/chapter_hub.formula.md) — Chapter hub template
- [formulae/page.formula.md](formulae/page.formula.md) — Knowledge page template
- [formulae/invocation.formula.md](formulae/invocation.formula.md) — Custom invocation template
- [formulae/log_entry.formula.md](formulae/log_entry.formula.md) — `log.md` entry shape
- [formulae/source.formula.md](formulae/source.formula.md) — Source artifact template

## Skills

- [docs/skills.md](docs/skills.md) — Canonical Arcana skill catalog (auto-generated)
- [docs/command_surface.md](docs/command_surface.md) — Validated public command matrix
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

## Resources

- [resources/](resources/) — Branding assets
