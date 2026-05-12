# Changelog

All notable changes to Arcana will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v1.0.0.html).

## [Unreleased]

### Added
- `rites/summon.sh` — one-command grimoire summoning rite (clone, catalog, CLAUDE.md config)
- `catalog.json` — company-wide grimoire catalog
- Dual catalog system: global catalog (company-wide) + local catalog (per-user installs)
- `VERSION` file — single source of truth for framework version
- Validation rites: structure, naming, semantics, format, links, security
- `rites/validate.sh` — unified orchestrator (sequential, parallel, smart modes)
- Validator invocations (`invocations/framework/validators/`) — AI counterparts to rites
- Quality invocations (`invocations/framework/quality/`) — duplication, documentation, rite quality

### Changed
- **Semantic domain rename**: `spells/` → `invocations/`, `rituals/` → `rites/`, `scrolls/` → `formulae/`
- `grimoire_template/` merged into `formulae/grimoire/`
- `base_spell.md` → `base_invocation.md`, `validate_rituals.md` → `validate_rites.md`
- `.scroll.md` extension convention → `.formula.md`
- `scripts/bootstrap.sh` → `rites/summon.sh` (summoning rite)
- `grimoire_catalog_global.json` → `catalog.json`, `grimoire_catalog_local.json` → `catalog.json`
- `appendix/` renamed to `docs/`, numeric prefixes dropped (e.g., `01_quickstart.md` → `quickstart.md`)
- `invocations/framework/core/` renamed to `invocations/framework/validators/`
- Three orchestrator scripts consolidated into `rites/validate.sh`
- Registry renamed to catalog (`grimoire_registry` → `grimoire_catalog` → `catalog`)
- Role terminology: Archmage → framework maintainer, Elder Mage → domain lead
- "Thin Grimoire" concept removed; simplified to framework + domain grimoires
- `formulae/page.formula.md` simplified to single clean template
- Hardcoded version numbers removed from markdown files

### Removed
- `rites/validate_all.sh`, `validate_parallel.sh`, `validate_smart.sh` (merged into `validate.sh`)
- `appendix/07_knowledge_authority_model.md` (concept retained in operating model)
- Old scroll templates: `page_external_reference.scroll.md`, `page_grimoire_canonical.scroll.md`, `page_hybrid_reference.scroll.md`
- `rites/validate_freshness.sh` (depended on removed metadata blocks)
- `scripts/` directory (contents moved to `rites/` and framework root)
- Living Reference Metadata blocks from all Olympus pages

---

## [1.1.0] - 2026-03-23

### Added - Phase 1 Intelligence System ✨
- **New spell**: `spells/meta/help.md` - Interactive spell catalog like `--help` (/gm-help)
- **New spell**: `spells/grimoire/analyze_semantics.md` - Deep semantic analysis with A-F grading
- **New spell**: `spells/framework/validate_boundaries.md` - Magical/practical boundary enforcement
- **New appendix**: `appendix/02_agent_configuration.md` - Ultra-minimal, zero-drift agent config guide
- **New appendix**: `appendix/05_reference.md` - Emoji usage guidelines for AI agents
- **New appendix**: `appendix/05_reference.md` - Complete magical vocabulary reference

### Changed
- **Spell organization**: Reorganized spells into three categories by purpose:
  - `spells/grimoire/` - Domain operations (create-grimoire, create-chapter, improve-grimoire, analyze-semantics) [4 spells]
  - `spells/framework/` - Framework operations (improve-framework, validate-boundaries) [2 spells]
  - `spells/meta/` - System documentation (help, base-spell) [2 spells]
  - **Moved**: help.md → meta/, base_spell.md → meta/, validate_boundaries.md → codex/
  - **Rationale**: Clearer conceptual separation - meta spells are documentation, framework spells can validate Framework itself
- **improve-grimoire**: Now automatically invokes analyze-semantics and validate-boundaries (Phases 2.5, 3.5)
- **improve-grimoire**: Added Phase 6 quality scoring with A-F grades and benchmarks
- **improve-framework**: Added Phase 6 pattern analysis and Phase 7 spell effectiveness tracking
- **improve-framework**: Added documentation drift detection to prevent structure mismatches
- **Simplified INDEX.md** - Now clearly states Framework is meta-knowledge only, not a grimoire
- **Streamlined README.md** - Updated directory structure to reflect current organization
- **Agent configuration philosophy** - Zero-drift approach: agent config works for 2 years without updates

### Removed
- `chapters/` directory from grimoire_framework - Tomes have chapters, Framework does not
- `chapters/README.md` - Instructions moved to create-grimoire spell

### Fixed
- Confusion between Framework (meta-knowledge) and grimoires (actual knowledge)
- Documentation drift: README.md and INDEX.md now accurately reflect filesystem structure
- Spell path references: Updated to use subdirectories throughout documentation

---

## [1.0.0] - 2026-03-22

### Added
- Initial release of The Grimoire Framework (extracted from grimoire_olympus)
- Framework documentation:
  - `README.md` - Universal Grimoire introduction
  - `quickstart.md` - 10-minute setup guide
  - `operating_model.md` - Framework operating principles
  - `governance.md` - Maintenance policies and versioning
  - `CHANGELOG.md` - This file
- Universal spells:
  - `spells/meta/base_spell.md` - Framework spell execution scroll
  - `spells/grimoire/create_chapter.md` - Step-by-step chapter creation guide
  - `spells/grimoire/create_grimoire.md` - AI-guided conversational grimoire setup ⭐
  - `spells/grimoire/improve_grimoire.md and spells/framework/improve_framework.md` - Self-improvement workflow
- Universal scrolls:
  - `scrolls/chapter_index.scroll.md` - Scroll for chapter routers
  - `scrolls/page.scroll.md` - Scroll for knowledge docs
  - `scrolls/spell.scroll.md` - Scroll for custom spells
- Universal rituals:
  - `rituals/validate_freshness.sh` - Validation ritual for content freshness
- Universal resources:
  - `resources/grimoire_icon_512.png` - Grimoire branding icon
- Grimoire scroll:
  - `grimoire_template/` - Ready-to-copy scroll for new grimoires ⭐
  - `grimoire_template/INDEX.md` - Scroll with placeholders
  - `grimoire_template/README.md` - Scroll with placeholders
  - `grimoire_template/chapters/` - Empty directory for new chapters
- Empty `chapters/` directory with README for domain use

### Architecture
- **Shared Framework Pattern**: The Grimoire Framework is the single source of truth for all domains
- **Thin Grimoires**: Domains create lightweight wrappers (INDEX.md, README.md, chapters/)
- **No Duplication**: All universal content lives in core, domains reference it
- **Prevents Drift**: Updates propagate automatically to all domains

### Governance
- Archmage role established (singular Framework maintainer)
- Semantic versioning adopted (MAJOR.MINOR.PATCH)
- Change management process defined:
  - Patch: Bug fixes (no announcement)
  - Minor: New features (domain announcement)
  - Major: Breaking changes (2-week advance notice + migration guide)
- Domain onboarding process documented
- Contribution guidelines established

### Migration from grimoire/
- Extracted meta-knowledge from `grimoire/chapters/grimoire/` to `grimoire_framework/`
- Moved universal assets (rituals, resources) to `grimoire_framework/`
- Renamed `grimoire/` to `grimoire_olympus/` (thin grimoire pattern)
- Updated all cross-references and documentation

---

**Maintained by**: the framework maintainer
