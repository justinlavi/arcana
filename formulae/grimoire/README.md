# {{GRIMOIRE_NAME}} Grimoire

This is the **{{GRIMOIRE_NAME}}** domain grimoire — a structured, AI-navigable knowledge base for {{GRIMOIRE_PURPOSE_DETAILED}}.

The framework that powers it (Arcana) lives at `~/grimoires/arcana/`. See [Arcana README](GRIMOIRE_ARCANA/README.md) for the full architecture.

## Layout

```
{{GRIMOIRE_DIRECTORY}}/
├── {{GRIMOIRE_DIRECTORY}}.md     # Root hub (start here for routing)
├── README.md                     # This file (human-facing project README)
├── grimoire.json                 # Manifest: name, namespace, description
├── log.md                        # Append-only activity log
├── sources/                          # Immutable source artifacts (LLM never edits)
├── inbox/                        # Transient drop zone (mixed content awaiting classification)
├── chapters/                     # LLM-authored knowledge pages
{{CHAPTER_TREE}}
└── skills/                       # Domain skills (slash commands)
```

## How to Use

1. Open `{{GRIMOIRE_DIRECTORY}}.md` for routing.
2. Follow hub pointers — every folder F has a hub at `F/<basename(F)>.md`.
3. Wikilinks (`[[page]]`) inside this grimoire surface in Obsidian's graph and backlinks panes.
4. Each page declares its provenance and authority via YAML frontmatter (see `GRIMOIRE_ARCANA/docs/page_schema.md`).

## Operations

| Goal | Skill |
|---|---|
| Add a new chapter | `/grm-domain-create-chapter` |
| Ingest a new source from `sources/` and update affected pages | `/grm-domain-ingest` |
| Promote a chat answer into a page | `/grm-domain-file-answer` |
| Health-check the grimoire (orphans, stale, ghost refs) | `/grm-domain-lint` |
| Audit naming and structure | `/grm-domain-improve` |

## Layers (the LLM-wiki model)

- **Sources** (`sources/`) — Immutable source artifacts. Articles, transcripts, papers, screenshots. The LLM reads them but never modifies them.
- **Wiki** (`chapters/`) — LLM-authored markdown synthesis. Hubs, concept pages, entity pages, playbooks, references. Updated incrementally as new sources arrive.
- **Schema** — `grimoire.json` plus the Arcana-injected block in `~/.claude/CLAUDE.md` / `~/.codex/AGENTS.md`. Tells agents how to operate this grimoire.

## Maintenance Principles

- Routers are pointer lists — no prose narrative inside a hub.
- Pages declare their authority (`external` / `grimoire` / `hybrid`) and cite sources.
- Stale claims (over `last_verified` window) are flagged by `/grm-domain-lint` and revisited.
- The activity log is append-only; never delete entries.
- All paths are relative inside this grimoire; cross-grimoire references use `GRIMOIRE_ARCANA/`-style placeholders.

## Identity

Manifest at `grimoire.json`:

```json
{
  "name": "{{GRIMOIRE_DIRECTORY}}",
  "namespace": "{{SKILL_NAMESPACE}}",
  "description": "{{GRIMOIRE_PURPOSE}}"
}
```

Skills under `skills/<area>-<verb>-<object>/` register as `/{{SKILL_NAMESPACE}}-<area>-<verb>-<object>`.

## Library Registration

Listed in `~/grimoires/library.json`:

```json
"{{GRIMOIRE_DIRECTORY}}": {
  "local_path": "$HOME/grimoires/{{GRIMOIRE_DIRECTORY}}",
  "online_path": null
}
```

The summoning rite (`GRIMOIRE_ARCANA/rites/summon.sh`) handles this automatically.

## Help

- Skill catalog: `/grm-meta-help`
- Arcana docs: `GRIMOIRE_ARCANA/README.md` and `GRIMOIRE_ARCANA/docs/`
- About this grimoire's content: see the maintainer.
