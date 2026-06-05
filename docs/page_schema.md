---
type: reference
title: "Page Schema"
aliases: ["frontmatter", "page-frontmatter", "frontmatter-spec"]
tags: [type/reference, arcana/schema]
authority: grimoire
last_verified: 2026-05-12
---

# Page Schema

Every authored Markdown page in a Grimoire (Arcana itself, or any grimoire)
carries YAML frontmatter. Raw artifacts under `sources/` may be copied exactly
as received; source wrapper Markdown under `sources/` uses this schema.

This document is the canonical specification: what's required, what's
optional, and what each field means.

The `validate_frontmatter` rite enforces this schema mechanically. Any page that fails - missing required fields for its `type`, unknown `type`, malformed YAML - is a structural violation.

---

## Page Types

A page declares its `type` so the agent knows how to treat it and so validators can apply the right rules.

| Type | Purpose | Lives in |
|---|---|---|
| `hub` | Folder router. Lists pointers to children; never holds knowledge. | `<folder>/<folder>.md` |
| `concept` | A standing topic, idea, or technique. | `chapters/<chapter>/<topic>.md` |
| `entity` | A specific person, place, organization, product, project. | `chapters/<chapter>/<entity>.md` |
| `source` | A source wrapper: capture metadata plus source body or pointer for one immutable artifact. | `sources/<slug>.md` |
| `playbook` | A procedural runbook the user follows. | `chapters/<chapter>/<procedure>.md` |
| `reference` | Glossary-style or schema-style definition page. | `chapters/<chapter>/<term>.md` or `docs/*.md` |
| `log-entry` | A single entry in `log.md`. Reserved for tooling that splits the log per entry; `log.md` itself is not annotated. | tooling output only |

If a page genuinely doesn't fit, prefer `concept` and add a precise `tags:` entry instead of inventing a new type.

---

## Authority Models

Every page (except `hub` and `log-entry`) declares where its truth lives:

| Authority | Meaning | Source citation |
|---|---|---|
| `external` | Source of truth lives elsewhere (a code repo, an article, a paper, a service). The page summarizes and routes. | Required: list `sources:` (paths under `sources/`, repo paths, or external URLs). |
| `grimoire` | This page IS the source of truth. Editing it is how truth changes. | `sources:` may be empty; provide change-control notes in body. |
| `hybrid` | Grimoire owns the synthesis, external systems own implementation details. | Required: list `sources:`. |

`hub` and `log-entry` pages omit `authority`.

---

## Source Layer Boundary

The `sources/` layer is citation-stable storage. It may contain raw artifacts,
source wrapper Markdown, or both:

- **Raw artifact**: a copied PDF, article export, transcript, image, dataset,
  or original Markdown file. Raw artifacts do not need Arcana frontmatter and
  are not rewritten to satisfy the page schema.
- **Source wrapper**: a Markdown file created from
  `formulae/source.formula.md`. It declares `type: source`,
  `authority: external`, and `sources:` pointing to the original URL, capture
  origin, or a sibling raw artifact such as `sources/<slug>/<file>.pdf`.
- **Both together**: use `sources/<slug>.md` as the wrapper and store bulky or
  binary originals under `sources/<slug>/`.

Authored wiki pages live under `chapters/` and are not source wrappers. A page
that synthesizes a source should use `type: concept`, `entity`, `playbook`, or
`reference` as appropriate, then cite the stable source wrapper or raw artifact
in `sources:`.

External URLs may appear directly in `sources:` when the URL itself is the
stable source pointer. When content has been filed locally, cite the local
`sources/` path so provenance survives link rot and inbox cleanup.

---

## Frontmatter Fields

```yaml
---
type: hub | concept | entity | source | playbook | reference | log-entry
title: "Human-readable title"
aliases: ["alt name", "abbreviation"]
tags: [chapter/<chapter>, type/<type>, custom/<...>]
sources: ["sources/<artifact>.md", "https://...", "<repo>/<path>"]
authority: external | grimoire | hybrid
last_verified: 2026-05-12
---
```

### Field rules

| Field | Required for | Notes |
|---|---|---|
| `type` | every page | Must be one of the seven values above. |
| `title` | every page | Free text; what Obsidian shows as the document title. |
| `aliases` | optional | List of alternate names for search, Dataview, and human metadata. Aliases are metadata only; wikilinks never resolve through aliases. |
| `tags` | every page | Use `/`-separated namespaces: `chapter/<name>`, `type/<type>`, `domain/<...>`. Drives Dataview and Obsidian tag panes. |
| `sources` | required for `authority: external`, `authority: hybrid`, and `type: source` | Paths or URLs. At least one entry must resolve. Validator checks `sources/...` paths exist on disk. |
| `authority` | every page except `hub` / `log-entry` | One of the three values above. |
| `last_verified` | every page except `hub` / `log-entry` | ISO date (`YYYY-MM-DD`) the page was last hand-verified or auto-checked. Must be a real verification date, not an implausibly early sentinel: `validate_frontmatter` rejects any date before a fixed static floor (`2020-01-01`), which catches epoch-style placeholders like `1970-01-01`. `/grm-health-check` flags pages older than the stale window (default: 90 days). |

### Required-fields matrix

| Type | type | title | tags | authority | sources | last_verified |
|---|---|---|---|---|---|---|
| `hub` | required | required | required | - | - | - |
| `concept` | required | required | required | required | required if external/hybrid | required |
| `entity` | required | required | required | required | required if external/hybrid | required |
| `source` | required | required | required | required, always external | required | required |
| `playbook` | required | required | required | required | required if external/hybrid | required |
| `reference` | required | required | required | required | required if external/hybrid | required |
| `log-entry` | required | required | - | - | - | - |

`aliases` is optional everywhere. Use it for alternate names and discovery, not for routing.

---

## Tag conventions

Tags use `/`-separated namespaces. The recommended top-level tags:

- `chapter/<chapter_name>` - locates the page in the chapter taxonomy. Hubs include their own chapter tag.
- `type/<type>` - mirrors the `type:` field; useful for Dataview cross-tag queries.
- `domain/<...>` - **optional** owner-defined topical facets for cross-cutting subjects (e.g. `domain/cmake`, `domain/build`, `domain/onboarding`). The namespace is the owner's choice - a grimoire may use `topic/<...>` instead - but pick one and apply it consistently.
- `status/<state>` - optional lifecycle (`status/draft`, `status/stable`, `status/deprecated`).
- `hub/<level>` - hub level: `hub/root` (grimoire root, one per grimoire), `hub/chapter` (top-level chapter hub), `hub/sub` (any deeper hub). Used by Obsidian graph color groups to make hubs visually distinct.

Tags are flat strings inside YAML (Dataview-compatible). Avoid spaces; use `_` or `-` if needed.

### Topical facets as a second retrieval axis

The hub tree is the primary navigation path: every page has one home, reached by routing from hub to hub. A topical facet (`domain/<...>`, or a grimoire's chosen equivalent such as `topic/<...>`) is an **optional second axis** - it groups cross-cutting pages that span chapters so an agent can find them by lexical tag search (for example, grep for `domain/cmake`) without walking every hub. It is recommended when a grimoire has subjects that recur across chapters, but it is not mechanically required: whether and how to use it is an editorial choice the owner curates. Arcana does not impose a domain vocabulary - keeping framework taxonomy out of grimoire content - so facet quality is reviewed by judgment (`/grm-audit-semantics`), not a validator.

### Hub level tags (recap)

| Hub depth | File path | Required tags |
|---|---|---|
| Root | `<grimoire>/<grimoire>.md` | `type/hub`, `hub/root`, `grimoire/<name>` |
| Chapter | `chapters/<chapter>/<chapter>.md` | `type/hub`, `hub/chapter`, `chapter/<chapter>` |
| Sub-chapter | `chapters/<chapter>/<sub>/<sub>.md` (or deeper) | `type/hub`, `hub/sub`, `chapter/<sub>` |

For Obsidian graph view configuration that uses these tags to color hubs, see [obsidian](obsidian.md).

---

## Worked Examples

### Hub page

```yaml
---
type: hub
title: "Build System"
aliases: ["build", "build-system"]
tags: [chapter/build_system, type/hub]
---
```

### External concept page derived from a source

```yaml
---
type: concept
title: "Lamination"
aliases: ["laminating dough", "book folds"]
tags: [chapter/techniques, technique/dough, type/concept]
sources: ["sources/example_recipe_method.md"]
authority: external
last_verified: 2026-05-12
---
```

### Grimoire-authoritative playbook

```yaml
---
type: playbook
title: "VM Handover Procedure"
aliases: ["vm-handover", "handover-runbook"]
tags: [chapter/operations, type/playbook]
authority: grimoire
last_verified: 2026-05-12
---
```

### Source wrapper

```yaml
---
type: source
title: "Example Recipe Method - Lamination Chapter"
tags: [type/source]
sources: ["https://example.com/recipe-method"]
authority: external
last_verified: 2026-05-12
---
```

This file lives at `sources/example_recipe_method.md`. Derived chapter pages
cite it with `sources: ["sources/example_recipe_method.md"]`.

---

## Validation

`python3 rites/validate_frontmatter.py` enforces:

1. Every `.md` file under `chapters/`, `docs/`, `invocations/`, `formulae/` (and the grimoire root) has YAML frontmatter delimited by `---` on the first line and a closing `---`.
2. `type:` is present and matches one of the seven values.
3. The required-fields matrix above holds for the declared `type`.
4. `authority` (when present) is one of `external`, `grimoire`, `hybrid`.
5. `type: source` pages are reserved for source wrappers under `sources/`.
6. `sources` paths under `sources/` resolve on disk; URLs are not network-checked.
7. `last_verified` is a parseable `YYYY-MM-DD` date and is not an implausibly early sentinel (rejected below a fixed static floor of `2020-01-01`; the check never compares against the current date, so validation stays reproducible).
8. `tags` and `aliases` are YAML lists of plain strings.

`python3 rites/validate_provenance.py` enforces:

1. Every `authority: external` or `authority: hybrid` page cites at least one
   source.
2. Pages never cite transient `inbox/` paths.
3. Source wrapper Markdown under `sources/` declares `type: source`,
   `authority: external`, and non-empty `sources:`.
4. Source wrappers do not cite themselves.

The `/arc-validate frontmatter` skill validates Arcana itself; `/grm-validate frontmatter` validates an active grimoire.

---

## Why frontmatter

Three concrete payoffs:

1. **Obsidian wikilinks** - full-path wikilinks such as `[[chapters/build_system/cmake|CMake]]` make routes explicit while still giving contributors readable labels.
2. **Dataview** - `tags`, `last_verified`, and `authority` are queryable. Hubs can include Dataview blocks that auto-list their children, eliminating hand-maintained route lists.
3. **Mechanical lint** - provenance (`sources:`), staleness (`last_verified`), orphan detection (cross-referenced with hub link analysis) all become rite-checkable instead of judgment calls.

See `script_vs_ai.md` for the broader principle: structured metadata is what separates "the LLM can audit this" from "the human has to read every page."
