---
type: playbook
title: "Add Content"
aliases: ["add", "add-content"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-06-05
---

# Invocation: Add Content

## Purpose

Add knowledge to the active grimoire as the right-sized unit — a single **page**
under an existing chapter, or a whole new **chapter** (folder + hub) when the
topic warrants its own home. The material can be written fresh from a short
conversation, or distilled from the current chat session (an analysis,
comparison, or derived insight worth keeping). External files and source
artifacts go through `/grm-import` instead.

This is the one command for putting LLM-authored knowledge into a grimoire:
`/grm-create` makes the grimoire itself, **`/grm-add`** fills it, and
`/grm-import` brings in external sources.

## Invocation

```
/grm-add
```

Or with a topic or material:

```
/grm-add <topic, or "this answer">
```

## Non-Negotiable Rules

1. Paths and chapter names are `snake_case`, lowercase, specific (`pto_policies`, not `hr_stuff`).
2. A chapter hub follows the folder-name convention: `chapters/<chapter>/<chapter>.md`, `type: hub`.
3. Practical folder names only inside chapters (`templates/`, `scripts/`, `snippets/`). Never `invocations/`, `formulae/`, or `rites/` — those live only in Arcana.
4. Every page (hub + leaves) carries v2 frontmatter (`type`, `title`, `tags`, …). See `ARCANA_HOME/docs/page_schema.md`.
5. Authored knowledge is `authority: grimoire`. If the content directly summarizes one external source, file the source with `/grm-import` instead.
6. Link to sources of truth; don't duplicate their content.
7. New content must be wired into a hub (a chapter's `## Routes`, or the root hub) before the operation is complete. One `log.md` entry per addition. Don't file trivial one-liners — add what compounds.

---

## Step 0: Precondition

Resolve the active grimoire with the shared grimoire directory guard. Set
`GRIMOIRE_ROOT` before writing files. Arcana is not a grimoire.

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

---

## Step 1: Understand the material and where it comes from

- **What** is being added — a topic the user describes, or a recent chat answer
  to capture ("save this", "file the comparison we just did"). If unclear, ask.
- **Where from** — written fresh in conversation, or distilled from the current
  chat session. For an external **file, folder, or source artifact**, stop and
  use [[invocations/grimoire/import|import]] (`/grm-import`) — that is the
  source-ingestion path, not this one.

---

## Step 2: Size it — page or chapter

Choose the smallest unit that fits the material, and confirm with the user when
it is ambiguous:

- **Page** — one focused idea (a concept, entity, playbook, or reference) that
  belongs inside an existing chapter. Go to **Step 3a**.
- **Chapter** — a new area with several facets, or material that no existing
  chapter fits. Go to **Step 3b**.

A single captured answer is almost always a page. Reach for a chapter only when
the material clearly opens a new routable area.

---

## Step 3a: Add a page

1. **Placement and type.** Pick the most relevant existing chapter and a `type:`:
   - `concept` — a topic, technique, or idea.
   - `entity` — a specific person, project, or product.
   - `playbook` — a procedure (most common for "how do I X" answers).
   - `reference` — a comparison table, glossary entry, or cheatsheet.

   Pick a `snake_case` slug. If no chapter fits, that is the signal to make a
   chapter instead (Step 3b).

2. **Stamp the page** with `new_page.py` (it fills frontmatter and stamps today's
   `last_verified`, so a leaf never ships with a placeholder date):

   ```bash
   python3 ARCANA_HOME/rites/new_page.py \
     --grimoire GRIMOIRE_ROOT \
     --path chapters/<chapter>/<slug>.md \
     --type <concept|entity|playbook|reference> \
     --title "<Title>" \
     --apply
   ```

   Run it without `--apply` first to preview. It derives a `chapter/<chapter>`
   tag and refuses to overwrite. Add `--tags domain/<facet>,…` for extra facets;
   use `--authority hybrid --sources <path-or-url>` only when the page synthesizes
   filed source material.

3. **Write the body.** When capturing an answer, the conversation is the source
   material — distill it into clean prose (`Purpose`, `When to Use`, content,
   `Gotchas`, `Related`); never hallucinate beyond what was established.

4. **Wire it in.** Add a full-path wikilink under the chapter hub's `## Routes`.

---

## Step 3b: Add a chapter

1. **Gather inputs** (one question at a time): chapter name (`snake_case`),
   one-line purpose, when-to-route-here, knowledge sources to point at, and 2–5
   sub-topics. Capture `chapter_name`, `chapter_title` (Title Case), `purpose`,
   `when_to_use`, `sources[]`, `sub_topics[]`.

2. **Scaffold from formula:**

   ```bash
   mkdir -p chapters/<chapter_name>
   cp ~/grimoires/arcana/formulae/chapter_hub.formula.md chapters/<chapter_name>/<chapter_name>.md
   ```

   The hub takes the folder's name — the convention that keeps Obsidian's graph
   meaningful.

3. **Customize the hub.** Replace `{{CHAPTER_TITLE}}`, `{{CHAPTER_NAME}}`,
   `[purpose]`, `[when to use]`; set tag `chapter/<chapter_name>`. The formula
   defaults to `hub/chapter`; if this chapter is nested inside another
   (`chapters/<existing>/<new>/`), change it to `hub/sub`. Add a `## Routes` line
   per child with full-path wikilinks. Verify no placeholders remain:

   ```bash
   grep -nE '\[(Chapter Name|purpose|when to use)\]|\{\{' chapters/<chapter_name>/<chapter_name>.md
   ```

4. **Seed leaf pages (optional)** with `new_page.py` as in Step 3a, one per
   sub-topic; stubs with TODOs are fine.

5. **Register in the parent hub** — the grimoire root hub for a top-level chapter
   (`<grimoire>/<grimoire>.md`, under `## Route By Chapter`), or the containing
   chapter's hub for a sub-chapter:

   ```markdown
   - <chapter description>: [[chapters/<chapter_name>/<chapter_name>|<Chapter Title>]]
   ```

---

## Step 4: Append to log.md

```bash
python3 ARCANA_HOME/rites/append_log.py \
  --grimoire GRIMOIRE_ROOT \
  --op create \
  --title "<page or chapter title>" \
  --skill /grm-add \
  --field pages=chapters/<chapter>/<slug-or-hub>.md
```

---

## Step 5: Validate

```bash
python3 ARCANA_HOME/rites/validate_grimoire_structure.py --grimoire GRIMOIRE_ROOT
python3 ARCANA_HOME/rites/validate_frontmatter.py --grimoire GRIMOIRE_ROOT
python3 ARCANA_HOME/rites/validate_links.py --grimoire GRIMOIRE_ROOT
```

Or invoke `/grm-validate` for the full mechanical pass.

## Report

Surface in chat: what was added (page or chapter) and where, the hub(s) updated,
the log entry, and validator pass/fail.

## Related

- **Page formula**: `~/grimoires/arcana/formulae/page.formula.md`
- **Chapter hub formula**: `~/grimoires/arcana/formulae/chapter_hub.formula.md`
- **Page stamping rite**: `~/grimoires/arcana/rites/new_page.py`
- **Page schema**: `~/grimoires/arcana/docs/page_schema.md`
- **Grimoire creation**: [[invocations/grimoire/create_grimoire|create grimoire]]
- **External sources**: [[invocations/grimoire/import|import]]
- **Structure validator**: `/grm-validate structure`
