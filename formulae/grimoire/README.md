# {{GRIMOIRE_NAME}} Grimoire

This README is the canonical home for the long-form description. Other surfaces (the manifest in `grimoire.json`, the root hub `{{GRIMOIRE_DIRECTORY}}.md`) intentionally just say *"{{GRIMOIRE_NAME}} Grimoire"* - keep the description here so it lives in exactly one place.

{{GRIMOIRE_PURPOSE_DETAILED}}

<!-- BEGIN ARCANA UPDATE -->
## Out of date? Update.

If anything here seems wrong, broken, or behind the current Arcana, bring this grimoire (and the Arcana it references) back to a current, validated, synchronized state with **Update**. Two ways to start it:

1. **Run the skill:** `/grm-update`.
2. **Or tell your AI agent:**

   > Pull the latest Arcana, then follow its update process.
<!-- END ARCANA UPDATE -->

## Installation

This grimoire is part of the **Grimoire** ecosystem powered by **Arcana**, the framework that handles agent integration, the validator suite, the canonical `/arc-*` and `/grm-*` skill sets, and library registration. The recommended way to install both is the Arcana summoning rite - one command, end-to-end.

### Recommended - Arcana summoning rite

Run the public summoning rite, passing this grimoire's repo URL as `--scope`:

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash -s -- --scope {{GRIMOIRE_REPO_URL}}
```

Works whether or not you already have Arcana installed. The rite:

1. Installs (or pulls) Arcana into `~/grimoires/arcana/`
2. Injects the Grimoire routing block into your agent instruction file (Claude Code's `~/.claude/CLAUDE.md`, Codex's `~/.codex/AGENTS.md`)
3. Registers the canonical `/arc-*` skills
4. Discovers this grimoire at the URL you passed
5. Offers it in the interactive menu, clones it into `~/grimoires/{{GRIMOIRE_DIRECTORY}}`
6. Updates `~/grimoires/library.json`
7. Registers this grimoire's `/{{SKILL_PREFIX}}-*` skills

For private GitLab / GitHub hosts, you may need to configure git credentials (HTTPS helper or SSH keys) and/or export an API token so repository discovery can authenticate:

```bash
export GITLAB_TOKEN=<your token>     # GitLab
export GITHUB_TOKEN=<your token>     # GitHub
```

Open a new agent session and try `/arc-help` to confirm the new skills are available. Full reference for scope shapes, auth, and troubleshooting: [github.com/justinlavi/arcana - docs/installation.md](https://github.com/justinlavi/arcana/blob/main/docs/installation.md).

### Manual install

If you'd rather drive each step yourself - or the summoning rite can't reach your host - Arcana and this grimoire can be installed by hand. The path layout is the one thing that matters: Arcana goes at `~/grimoires/arcana/` and this grimoire goes at `~/grimoires/{{GRIMOIRE_DIRECTORY}}/`, because the other rites resolve each other through those locations.

```bash
# 1. Clone Arcana
git clone https://github.com/justinlavi/arcana.git ~/grimoires/arcana

# 2. Clone this grimoire
git clone {{GRIMOIRE_REPO_URL}} ~/grimoires/{{GRIMOIRE_DIRECTORY}}

# 3. Register the library entry and skills
python3 ~/grimoires/arcana/rites/sync_library.py --apply
python3 ~/grimoires/arcana/rites/sync_skills.py
```

Add the canonical Grimoire instruction block to your agent file using `/arc-sync agentfile` once skills are registered, or paste it manually from [`rites/templates/grimoire_block.md`](https://github.com/justinlavi/arcana/blob/main/rites/templates/grimoire_block.md).

## Layout

```
{{GRIMOIRE_DIRECTORY}}/
├── {{GRIMOIRE_DIRECTORY}}.md     # Root hub (start here for routing)
├── README.md                     # This file (human-facing project README)
├── grimoire.json                 # Manifest: name, skill prefix, description
├── log.md                        # Append-only content-change history (not a VCS log)
├── sources/                      # Immutable source artifacts and wrappers
├── inbox/                        # Transient drop zone (mixed content awaiting classification)
├── chapters/                     # LLM-authored knowledge pages
{{CHAPTER_TREE}}
└── skills/                       # Grimoire skills (slash commands)
```

## How to Use

1. Open `{{GRIMOIRE_DIRECTORY}}.md` for routing.
2. Follow hub pointers - every folder F has a hub at `F/<basename(F)>.md`.
3. Full-path wikilinks (`[[chapters/path/to/page|label]]`) inside this grimoire surface in Obsidian's graph and backlinks panes.
4. Each page declares its provenance and authority via YAML frontmatter (see `ARCANA_HOME/docs/page_schema.md`).

## Operations

| Goal | Skill |
|---|---|
| Add a page or chapter (fresh, or capturing a chat answer) | `/grm-add` |
| Import a new source into `sources/` and update affected pages | `/grm-import` |
| Health-check the grimoire (orphans, stale, ghost refs) | `/grm-health-check` |
| Audit naming and structure | `/grm-health-check` |

## Layers (the LLM-wiki model)

- **Sources** (`sources/`) - Immutable source artifacts and source wrappers.
  Articles, transcripts, papers, screenshots, and datasets land here during
  import; wiki pages cite these stable paths.
- **Wiki** (`chapters/`) - LLM-authored markdown synthesis. Hubs, concept pages, entity pages, playbooks, references. Updated incrementally as new sources arrive.
- **Schema** - `grimoire.json` plus the Arcana-injected block in `~/.claude/CLAUDE.md` / `~/.codex/AGENTS.md`. Tells agents how to operate this grimoire.

## Maintenance Principles

- Routers are pointer lists - no prose narrative inside a hub.
- Pages declare their authority (`external` / `grimoire` / `hybrid`) and cite sources.
- Stale claims (older than the stale window, default 90 days) are flagged by `/grm-health-check` and revisited.
- The activity log is append-only and records content changes (pages/sources added, removed, changed), not version-control mechanics; never delete entries.
- All paths are relative inside this grimoire; cross-grimoire references use `ARCANA_HOME/`-style placeholders.
- Text files use UTF-8 without BOM and LF line endings. Unicode is allowed; mojibake and repair artifacts are not.

## Identity

Manifest at `grimoire.json`:

```json
{
  "name": "{{GRIMOIRE_DIRECTORY}}",
  "skill_prefix": "{{SKILL_PREFIX}}",
  "description": "{{GRIMOIRE_PURPOSE}}"
}
```

(The manifest description is a short tagline - a few words like "personal cooking knowledge" or "HR runbooks and policies". The long-form description lives in this README; do not paste the long form into the manifest or hub.)

Skills under `skills/<area>-<verb>-<object>/` register as `/{{SKILL_PREFIX}}-<area>-<verb>-<object>`.

## Library Registration

Listed in `~/grimoires/library.json`:

```json
"{{GRIMOIRE_DIRECTORY}}": {
  "local_path": "$HOME/grimoires/{{GRIMOIRE_DIRECTORY}}",
  "online_path": null
}
```

The summoning rite (`ARCANA_HOME/rites/summon.sh`) handles this automatically.

## Help

- Skill catalog: `/arc-help`
- Arcana docs: `ARCANA_HOME/README.md` and `ARCANA_HOME/docs/`
- About this grimoire's content: see the maintainer.
