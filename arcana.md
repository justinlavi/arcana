---
type: hub
title: "Arcana"
aliases: ["arcana-root", "grimoire-arcana"]
tags: [arcana/root, type/hub, hub/root]
---

# Arcana

Meta-knowledge about Arcana itself: invocations, formulae, rites, and governance. For grimoire knowledge, route to the grimoire's own root hub instead.

Arcana is the engine. Every grimoire references it; nothing copies it.

## Read Model

- Routing: hub-per-folder, open-ended depth -> [[docs/operating_model|operating model]]
- Frontmatter: type / authority / sources / last_verified -> [[docs/page_schema|page schema]]
- Engine layers: `docs/`, `invocations/`, `formulae/`, `rites/`, `skills/`, and `resources/`
- Grimoire scaffold layers (`chapters/`, `sources/`, `inbox/`, `log.md`) -> [[formulae/grimoire/README|README]]

## Documentation

- Overview and architecture -> [[README|README]]
- Update & skill-less self-update -> [[UPDATE|UPDATE]]
- Contributing guide -> [[CONTRIBUTING|CONTRIBUTING]]
- Installation and smoke test -> [[docs/installation|installation]]
- Summoning behavior contract -> [[docs/summoning_contract|summoning contract]]
- Agent target registry -> [[docs/agent_targets|agent targets]]
- Agent setup -> [[docs/agent_configuration|agent configuration]]
- Skill catalog -> [[docs/skills|skills]]
- Skill naming schema -> [[docs/skill_schema|skill schema]]
- Public command matrix -> [[docs/command_surface|command surface]]
- Terminology and schemas -> [[docs/reference|reference]]
- Storage layers and routing -> [[docs/operating_model|operating model]]
- Page frontmatter schema -> [[docs/page_schema|page schema]]
- Obsidian setup -> [[docs/obsidian|obsidian]]
- VS Code wikilink setup -> [[docs/vscode|vscode]]
- Script vs AI boundaries -> [[docs/script_vs_ai|script vs ai]]
- Invocation eval tier -> [[docs/evals|evals]]
- Rite mutation profiles -> [[docs/rite_profiles|rite profiles]]
- Architecture backlog -> [[docs/architecture_backlog|architecture backlog]]
- Governance and versioning -> [[docs/governance|governance]]
- Release workflow -> [[docs/release|release]]
- Version history -> [[CHANGELOG|CHANGELOG]]
- Temporary 1.3.0 handoff -> [[docs/temp_1_3_0_handoff|temp 1 3 0 handoff]]

## Invocations

**Grimoire operations** -> [[invocations/grimoire/grimoire|grimoire]]

- Create a grimoire -> [[invocations/grimoire/create_grimoire|create grimoire]]
- Create a chapter -> [[invocations/grimoire/create_chapter|create chapter]]
- Update the grimoire and its Arcana -> [[invocations/grimoire/update|update]]
- Sync active-grimoire agent skills -> [[invocations/grimoire/agent_sync_skills|agent sync skills]]
- Import a source -> [[invocations/grimoire/import|import]]
- Capture a chat answer -> [[invocations/grimoire/capture_answer|capture answer]]
- Health-check a grimoire -> [[invocations/grimoire/health_check|health check]]
- Improve a grimoire -> [[invocations/grimoire/improve_grimoire|improve grimoire]]
- Audit grimoire semantics -> [[invocations/grimoire/audit_semantics|audit semantics]]
- Validate a grimoire -> [[invocations/grimoire/validators/validate|validate]]
- Validate grimoire structure -> [[invocations/grimoire/validate_structure|validate structure]]
- Audit grimoire boundaries -> [[invocations/grimoire/audit_boundaries|audit boundaries]]
- Grimoire validator hub -> [[invocations/grimoire/validators/validators|validators]]

**Arcana maintenance** -> [[invocations/arcana/arcana|arcana]]

- Improve Arcana -> [[invocations/arcana/improve_arcana|improve arcana]]
- Update Arcana and grimoires -> [[invocations/arcana/update|update]]
- Arcana validator hub -> [[invocations/arcana/validators/validators|validators]]
- Arcana quality hub -> [[invocations/arcana/quality/quality|quality]]

**Agent operations** -> [[invocations/agent/agent|agent]]

- Sync agent skills -> [[invocations/agent/sync_skills|sync skills]]
- Update agent instructions -> [[invocations/agent/sync_instructions|update agent block]]

**Library operations** -> [[invocations/library/library|library]]

- Sync the local library -> [[invocations/library/sync|sync]]
- Adopt an unmanaged grimoire -> [[invocations/library/adopt|adopt]]

**Workspace operations** -> [[invocations/workspace/workspace|workspace]]

- Clean workspace artifacts -> [[invocations/workspace/clean|clean]]

**Help** -> [[invocations/help/help|help]]

**Meta support** -> [[invocations/meta/meta|meta]]

- Base invocation template -> [[invocations/meta/base_invocation|base invocation]]
- Grimoire directory guard -> [[invocations/meta/grimoire_directory_guard|grimoire directory guard]]

## Formulae

- Full grimoire scaffold -> [[formulae/grimoire/README|README]]
- Root-hub template -> [[formulae/grimoire/root_hub.formula|root hub.formula]]
- Chapter hub template -> [[formulae/chapter_hub.formula|chapter hub.formula]]
- Knowledge page template -> [[formulae/page.formula|page.formula]]
- Custom invocation template -> [[formulae/invocation.formula|invocation.formula]]
- Log entry shape -> [[formulae/log_entry.formula|log entry.formula]]
- Source artifact template -> [[formulae/source.formula|source.formula]]
- Scaffold contract: `formulae/grimoire/scaffold_contract.json`

## Skills

- Canonical skill catalog -> [[docs/skills|skills]]
- Public command matrix -> [[docs/command_surface|command surface]]
- Skill source directory: `skills/`; registered via `rites/register_skills.py`

## Rites

- One-command summoning: `rites/summon.sh`
- Agent target registry loader and validator: `rites/agent_targets.py`
- Skill registration: `rites/register_skills.py`
- Library reconciliation: `rites/sync_library.py`
- Generated docs sync: `rites/sync_docs.py`
- Manifest writer for unmanaged dirs: `rites/adopt_grimoire.py`
- Grimoire log appender: `rites/append_log.py`
- Full validator orchestrator: `rites/validate.py`
- Validators: `rites/validate_<aspect>.py`

## Resources

- Branding assets: `resources/`
