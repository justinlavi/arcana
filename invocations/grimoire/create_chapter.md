---
type: playbook
title: "Create Chapter"
aliases: ["create-chapter", "scaffold-chapter"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-05-12
---

# Invocation: Create Grimoire Chapter

## Purpose

Scaffold a new knowledge chapter inside the active grimoire — copy `chapter_hub.formula.md` to `chapters/<chapter>/<chapter>.md`, customize placeholders, optionally seed leaf docs from `page.formula.md`, and register the chapter in the grimoire's root hub.

## Invocation

```
/grm-create-chapter
```

Or with a topic:

```
/grm-create-chapter for <topic>
```

## Non-Negotiable Rules

1. Chapter names are `snake_case`, lowercase, specific (`pto_policies`, not `hr_stuff`).
2. The chapter hub file follows the folder-name convention: `chapters/<chapter>/<chapter>.md`.
3. Practical folder names only inside chapters (`templates/`, `scripts/`, `snippets/`). Never `invocations/`, `formulae/`, or `rites/` — those live only in Arcana.
4. Every page (hub + leaves) carries v2 frontmatter (`type`, `title`, `tags`, etc.). See `ARCANA_HOME/docs/page_schema.md`.
5. Link to source systems; don't duplicate their content.
6. Update the grimoire's root hub so the chapter is routable. Use a wikilink.

---

## Step 0: Precondition

Resolve the active grimoire with the shared grimoire directory guard. Set `GRIMOIRE_ROOT` before creating files. Arcana is not a grimoire.

---

## Step 1: Gather Inputs

Have a short conversation. Ask one question at a time:

- **Chapter name** (`snake_case`, specific, scope-appropriate)
- **One-line purpose** — what knowledge does this chapter hold?
- **When to route here** — what kinds of questions land here?
- **Knowledge sources** — wikis, drives, repos, tribal knowledge to point at
- **Sub-topics** — 2-5 leaf docs the chapter will eventually contain

Capture: `chapter_name`, `chapter_title` (Title Case), `purpose`, `when_to_use`, `sources[]`, `sub_topics[]`.

---

## Step 2: Scaffold from Formula

```bash
mkdir -p chapters/{{chapter_name}}
cp ~/grimoires/arcana/formulae/chapter_hub.formula.md chapters/{{chapter_name}}/{{chapter_name}}.md
```

The chapter hub takes the folder's name (not a generic `INDEX`) — this is the v2 hub convention that keeps Obsidian's graph view meaningful.

---

## Step 3: Customize the Chapter Hub

Edit `chapters/{{chapter_name}}/{{chapter_name}}.md` and replace placeholders:

- Frontmatter: `{{CHAPTER_TITLE}}`, `{{CHAPTER_NAME}}`. Tags should include `chapter/{{chapter_name}}`.
- **Hub level tag** — the formula defaults to `hub/chapter` (top-level). If this chapter is being created *inside* another chapter (i.e., the new path is `chapters/<existing>/<new>/`), change the tag to `hub/sub`. The level distinction drives the Obsidian graph color (chapter hubs vs sub-hubs); the routing model itself works identically at every depth.
- `[Chapter Name]` -> `{{chapter_title}}`
- `[purpose]` -> `{{purpose}}`
- `[when to use]` -> `{{when_to_use}}`
- Routes block — one line per child, using full-path wikilinks. A child can be a leaf (a page with `type: concept`/`entity`/`playbook`/etc.) or a sub-hub (a folder with its own `<folder>.md`):

  ```markdown
  - <child description> -> [[chapters/{{chapter_name}}/<child_name>|<child label>]]
  ```

Verify no placeholder syntax remains:

```bash
grep -nE '\[(Chapter Name|purpose|when to use)\]|\{\{' chapters/{{chapter_name}}/{{chapter_name}}.md
```

---

## Step 4: Seed Leaf Docs (Optional)

For each sub-topic the user wants stubbed now:

```bash
cp ~/grimoires/arcana/formulae/page.formula.md chapters/{{chapter_name}}/{{sub_topic}}.md
```

Edit each leaf to fill in frontmatter (`type`, `title`, `tags`, `authority`, `sources`, `last_verified`) and body sections (`Purpose`, `When to use`, content, `Gotchas`, `Related`).

Content rules:

- **Do** point at sources of truth for drift-sensitive values; include "as of <date> — VERIFY BEFORE USE" when snapshotting.
- **Do** use Grimoire as the canonical home for grimoire-native knowledge (`authority: grimoire`).
- **Do** cite source artifacts (`sources: ["sources/<slug>.md"]`) when the page synthesizes external material.
- **Don't** duplicate content from another chapter — full-path wikilink to it.
- **Don't** store implementation values without query instructions.

Stubs with TODOs are acceptable — leaf authoring can happen later.

---

## Step 5: Register in the Parent Hub

Edit the parent hub — the grimoire root hub for a top-level chapter (`<grimoire>/<grimoire>.md`), or the containing chapter's hub for a sub-chapter (`chapters/<parent>/<parent>.md`). Under the routing section (typically `## Route By Chapter` at root, `## Routes` inside a chapter), add:

```markdown
- <chapter description>: [[chapters/{{chapter_name}}/{{chapter_name}}|{{chapter_title}}]]
```

Keep entries alphabetized or grouped by domain — match the existing convention in the file. Hubs are idempotent: wikilinks always target repository-root relative paths, even from deeply-nested chapters.

---

## Step 6: Append to log.md

```bash
python3 ARCANA_HOME/rites/append_log.py \
  --grimoire GRIMOIRE_ROOT \
  --op create \
  --title "{{chapter_title}} chapter" \
  --skill /grm-create-chapter \
  --field pages=chapters/{{chapter_name}}/{{chapter_name}}.md
```

---

## Step 7: Validate

```bash
ls chapters/{{chapter_name}}/
grep -n "{{chapter_name}}" {{grimoire_directory}}.md   # must find the new route
python3 ARCANA_HOME/rites/validate_grimoire_structure.py --grimoire GRIMOIRE_ROOT
python3 ARCANA_HOME/rites/validate_frontmatter.py --grimoire GRIMOIRE_ROOT
```

Or invoke `/grm-validate-all` for the full mechanical pass.

---

## Related

- **Chapter hub formula**: `~/grimoires/arcana/formulae/chapter_hub.formula.md`
- **Page formula**: `~/grimoires/arcana/formulae/page.formula.md`
- **Page schema**: `~/grimoires/arcana/docs/page_schema.md`
- **Grimoire creation**: [`create_grimoire.md`](create_grimoire.md)
- **Structure validator**: `/grm-validate-structure`
