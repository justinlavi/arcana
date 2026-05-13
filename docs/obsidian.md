---
type: reference
title: "Obsidian Setup"
aliases: ["obsidian", "obsidian-setup", "graph-view"]
tags: [type/reference, arcana/docs]
authority: grimoire
last_verified: 2026-05-12
---

# Obsidian Setup

How to open a grimoire as an Obsidian vault and configure the graph view so hubs, sources, and playbooks pop visually.

Arcana ships a recommended `.obsidian/graph.json` in every grimoire scaffold and in Arcana itself. The page-schema tags (`hub/root`, `hub/chapter`, `hub/sub`, `type/source`, `type/playbook`, `type/reference`) drive the color groups.

---

## Open the vault

1. **Open Obsidian** → *Open another vault* → *Open folder as vault* → pick the grimoire's root directory (e.g. `~/grimoires/cooking-grimoire`).
2. Obsidian reads the bundled `.obsidian/graph.json` automatically.
3. Open the grimoire root hub (`<grimoire>.md`) — that's the routing entry point.
4. Open the **Graph view** (icon in the left sidebar, or `Ctrl/Cmd+G`).

If your vault doesn't already have `.obsidian/graph.json`, copy the one from `GRIMOIRE_ARCANA/formulae/grimoire/.obsidian/graph.json`.

---

## Color groups (what ships)

A vaporwave-leaning palette: pinks, purples, cyan, electric blue. Cool and high-contrast against Obsidian's dark theme.

| Color | Hex | Query | Matches |
|---|---|---|---|
| **Hot pink** | `#FF71CE` | `tag:#hub/root` | The single grimoire-root hub |
| **Cyan** | `#01CDFE` | `tag:#hub/chapter` | Top-level chapter hubs (immediately under `chapters/`) |
| **Purple** | `#B967FF` | `tag:#hub/sub` | Any deeper hub (depth is open-ended) |
| **Lavender** | `#C996FF` | `["type":"source"]` | Source pages (summaries of artifacts in `sources/`) |
| **Electric blue** | `#4D4DFF` | `["type":"playbook"]` | Procedural runbooks |
| **Pale pink** | `#FFB3DE` | `["type":"reference"]` | Glossary / schema-style pages |
| Default | (Obsidian default) | (everything else) | Concept and entity leaves |

Open *Graph view → settings → Groups* to tweak colors or add new groups. The bundled queries use Obsidian's built-in search syntax:

- `tag:#hub/root` — page has `hub/root` in its `tags:` frontmatter list.
- `["type":"source"]` — page has `type: source` in its frontmatter.
- `path:chapters/projects/` — files under that folder.

You can combine queries: `tag:#hub/chapter -path:chapters/projects/` colors only chapter hubs outside the projects folder.

---

## Why each tag exists

- **`hub/root`** — there's exactly one per grimoire; hot pink marks the entry point at a glance.
- **`hub/chapter`** — top-level chapters (immediately under `chapters/`); cyan tells you "these are the grimoire's major branches."
- **`hub/sub`** — any hub deeper than a top-level chapter; purple tells you "this is a sub-router, not a leaf." Hub depth is open-ended — a sub-hub can route to its own sub-hubs, and so on. The tag flattens all those depths into one visual class because the routing rules are identical at every level.
- **`type/source`** — derived directly from a `sources/` artifact; lavender surfaces source-backed synthesis at a glance.
- **`type/playbook`** — procedural; electric blue separates "things to do" from "things to know."
- **`type/reference`** — definitional / schema-style; soft pink for the glossary class.

---

## Other useful Obsidian features

- **Backlinks pane** (`Ctrl/Cmd+Shift+B`) — every page lists who wikilinks to it. Replaces the v1 "Read order" / "Grimoire-first route" breadcrumbs.
- **Dataview plugin** (community plugin) — runs queries against frontmatter (`type`, `tags`, `last_verified`, `authority`). Add a Dataview block to a chapter hub to auto-list its leaves filtered by `chapter/<name>` instead of hand-maintaining the routes section.
- **Folder Notes plugin** (community plugin) — clicking a folder in the file explorer opens its `<folder>.md` hub. Aligns the file tree with the hub convention.
- **Graph filters** — *Filters* tab in graph settings:
  - Hide attachments: focus on pages.
  - Hide orphans: temporarily hide unconnected pages while you triage.
  - Search filter: e.g. `path:chapters/build_system/` to focus on one chapter.
- **Local graph** (`Ctrl/Cmd+P` → *Open local graph*) — graph centered on the current page; great for chapter exploration.

## Alias-resolved wikilinks: a Ctrl+click gotcha

When a wikilink uses an alias-resolved target — e.g. `[[cf_sw_overview|overview]]` resolves to `chapters/projects/cf_sw/overview.md` via that page's `aliases:` frontmatter — Obsidian *displays* and *renders* the link correctly, but **Ctrl/Cmd+click navigation may sometimes create a new empty stub file at the alias name** instead of opening the aliased target. This depends on Obsidian's settings and version.

If you find a 1–2 line stub like `# cf_sw_overview` appearing in a chapter folder, it's almost certainly this gotcha. Safe to delete — the real content is at the actual filename, and the alias still resolves for AI agents and the validator.

To avoid it: prefer the file picker (`Ctrl/Cmd+O`) when opening alias-resolved pages, or check that *Settings → Files & Links → Use Wikilinks → On* and *Detect all file extensions → Off* are configured. If stubs keep appearing, switch the wikilink to its full path form (`[[chapters/projects/cf_sw/overview|overview]]`) for that specific link.

`/grm-domain-lint` and `validate_orphans` will catch these stubs (they're orphan pages with no inbound links and no real content), so the quality gates protect you even if you forget.

---

## When to update color groups

Add a color group whenever you introduce a new structural distinction worth surfacing in the graph. Examples:

- A `status/deprecated` color (e.g. dim crimson) once you start lifecycle-tagging pages.
- A `domain/<facet>` color when one cross-cutting concern needs visual emphasis.

Stay opinionated about how many colors you ship — past ~8 groups the graph becomes a rainbow and the signal flattens. The default vaporwave palette (pink/cyan/purple/blue) leaves headroom: extra groups should pick muted or saturated outliers from the same family, not bright primaries that fight the existing ones.

---

## What is *not* Arcana's job

- **Per-user UI state** — pane layout, recently opened files, plugin enablement choices. These live in `.obsidian/workspace.json` and friends, which are gitignored by default.
- **Graph node positioning** — Obsidian computes layout dynamically; we don't pin positions.
- **Plugin recommendations beyond the schema** — Dataview and Folder Notes are useful but optional. Arcana doesn't depend on either.

---

## Related

- Page schema (the source of the tags): [page_schema.md](page_schema.md)
- Operating model: [operating_model.md](operating_model.md)
- Agent configuration: [agent_configuration.md](agent_configuration.md)
