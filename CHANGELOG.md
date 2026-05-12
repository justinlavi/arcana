# Changelog

## [1.0.0] — 2026-05-12

First public release of Arcana.

### Core capabilities

**Grimoire structure**
- Deterministic three-level routing: root `INDEX.md` → chapter `INDEX.md` → leaf document
- Each grimoire declares its identity in a `grimoire.json` manifest (`name`, `namespace`, `description`)
- Domain grimoires are pure content repositories — no engine code, no Arcana submodules
- Domain grimoires can ship their own `skills/` directory with domain-specific slash commands

**Installation and library management**
- One-command summoning rite (`rites/summon.sh`) with release-first binary bootstrap and Python source fallback
- Interactive grimoire discovery via GitHub/GitLab API, with static `library.json` fallback
- Local grimoire library at `~/grimoires/library.json` — a pure path registry separate from grimoire identity
- GUI mode via Dear PyGui for interactive selection during summoning
- `rites/sync_library.py` (`/grm-library-sync`) — reconciles the local library against disk; detects missing, stale, mismatched, and unmanaged grimoires
- `rites/adopt_grimoire.py` (`/grm-library-adopt`) — writes a `grimoire.json` manifest for an existing unmanaged directory
- `rites/migrate_home.py` — one-shot migration from the pre-1.0 `~/grimoire/` layout to `~/grimoires/`

**Skill system**
- Skills are thin SKILL.md pointer files registered to agent skill directories; no logic embedded in the skill itself
- Arcana ships `/grm-*` skills; each domain grimoire contributes its own `/{namespace}-*` skills
- Skill namespace is declared in `grimoire.json` — a single source of truth shared by the registration rite and all SKILL.md files
- `rites/register_skills.py` (`/grm-skills-register`) — discovers and installs skills from Arcana and every library entry to Claude Code and Codex/ChatGPT
- Source SKILL.md files use `{{NAMESPACE}}` and `{{ARCANA_PATH}}` placeholders resolved at registration time
- `when_to_use` frontmatter field enables Claude Code auto-invocation by intent, without the user typing the slash command
- `disable-model-invocation` frontmatter field prevents auto-invocation for destructive skills

**Grimoire operations (domain-facing skills)**
- `/grm-domain-create-grimoire` — conversational grimoire scaffolding from formula templates
- `/grm-domain-create-chapter` — chapter scaffolding within an active grimoire
- `/grm-domain-improve` — comprehensive grimoire audit and improvement
- `/grm-domain-validate-structure` — structural compliance against Arcana formulae
- `/grm-domain-analyze-semantics` — judgment-based naming and organization audit

**Arcana maintenance (maintainer-facing skills)**
- `/grm-arcana-improve` — full Arcana improvement orchestrator
- `/grm-arcana-validate-all` — runs the complete validator suite via `rites/validate.py`
- `/grm-arcana-validate-{structure,naming,semantics,format,links,security,skill-refs}` — individual mechanical validators, each independently invocable
- `/grm-arcana-validate-boundaries` — magical/practical boundary enforcement
- `/grm-arcana-clean` — removes temporary rite artifacts

**Skill catalog and documentation**
- `rites/sync_docs.py` — generates `docs/skills.md` from SKILL.md frontmatter; single source of truth for the skill catalog
- `/grm-meta-help` — enumerates every installed skill across Arcana and all domain grimoires
- Full documentation suite: `docs/installation.md`, `docs/quickstart.md`, `docs/agent_configuration.md`, `docs/reference.md`, `docs/operating_model.md`, `docs/script_vs_ai.md`, `docs/governance.md`, `docs/release.md`

**Supported agents**
- Claude Code — full skill registration; `when_to_use` auto-invocation; `CLAUDE.md` instruction block injection
- Codex / ChatGPT — pointer-only SKILL.md registration; `AGENTS.md` instruction block injection
- GitHub Copilot, Cursor — via the agent instruction block in `CLAUDE.md` / `AGENTS.md`
