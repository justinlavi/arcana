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

- **Backlinks pane** (`Ctrl/Cmd+Shift+B`) — every page lists who wikilinks to it.
- **Dataview plugin** (community plugin) — runs queries against frontmatter (`type`, `tags`, `last_verified`, `authority`). Add a Dataview block to a chapter hub to auto-list its leaves filtered by `chapter/<name>` instead of hand-maintaining the routes section.
- **Folder Notes plugin** (community plugin) — clicking a folder in the file explorer opens its `<folder>.md` hub. Aligns the file tree with the hub convention.
- **Graph filters** — *Filters* tab in graph settings:
  - Hide attachments: focus on pages.
  - Hide orphans: temporarily hide unconnected pages while you triage.
  - Search filter: e.g. `path:chapters/build_system/` to focus on one chapter.
- **Local graph** (`Ctrl/Cmd+P` → *Open local graph*) — graph centered on the current page; great for chapter exploration.

## Full-path wikilinks

Arcana supports only repository-root relative wikilinks. Write `[[chapters/projects/cf_sw/overview|overview]]`, not `[[cf_sw_overview|overview]]` or `[[overview]]`. The `.md` suffix is optional in wikilinks for Obsidian compatibility.

If a wikilink includes display text after `|`, keep it to the target filename only, normalized for reading. The path already carries chapter, project, trip, and parent-folder context, so `[[chapters/travel/trips/2026/06_fukuoka_kyoto_tokyo/overview|overview]]` is preferred over `[[chapters/travel/trips/2026/06_fukuoka_kyoto_tokyo/overview|fukuoka kyoto tokyo trip overview]]`.

Aliases remain useful as page metadata, but they are never link targets. This keeps routing deterministic, prevents global alias collisions, and avoids Ctrl/Cmd-click creating empty alias-named stubs.

`validate_links` rejects alias-based and filename-only wikilinks unless the target is an actual path relative to the grimoire root, such as `[[README]]`. It also warns when display text repeats parent context instead of matching the target filename.

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
