---
type: playbook
title: "Add"
aliases: ["add", "add-content", "import", "file-a-source"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-11-12
---

# Invocation: Add (put knowledge in)

## Purpose

One verb for putting knowledge into the active grimoire. What the user hands
over decides the mode:

- **Authored material** (a topic, a question answered in this chat, a
  comparison worth keeping) becomes a page under an existing chapter or a new
  chapter when the topic warrants its own home. Authored knowledge is
  `authority: grimoire`.
- **A file, a folder, or the inbox** is filed: external artifacts become
  citation-stable sources under the chapter they support
  (`chapters/<path>/sources/`), drafts and notes are promoted to wiki pages,
  and affected pages and hubs are updated. Nothing is ever filed or cited
  under `publish/`.

`/grm-create` makes the grimoire; `/grm-add` fills it.

## Invocation

```
/grm-add                       # ask what to add; or sweep inbox/ when it holds files
/grm-add <topic>               # author a page or chapter about the topic
/grm-add "this answer"         # capture the answer just given in chat
/grm-add <file>                # file one source artifact (PDF, article, transcript, screenshot)
/grm-add <folder>              # classify and file everything under a folder
/grm-add inbox                 # sweep the grimoire's inbox/
```

## Non-Negotiable Rules

1. Paths and chapter names follow the grimoire's recorded convention
   (`naming` in `grimoire.json`; `snake_case` when absent) and are specific
   (`pto_policies`, not `hr_stuff`). If the convention is not recorded and the
   material arrives in another casing, ask the user once which convention the
   grimoire follows, record the answer in `grimoire.json`, and move on. Never
   rename existing or imported files to fit without asking.
2. A chapter hub follows the folder-name convention:
   `chapters/<chapter>/<chapter>.md`, `type: hub`.
3. Practical folder names only inside chapters (`templates/`, `scripts/`,
   `snippets/`). Never `invocations/`, `formulae/`, or `rites/`; those live
   only in Arcana.
4. Every page carries frontmatter (`type`, `title`, `tags`, `authority`,
   `sources`, `last_verified`); see `ARCANA_HOME/docs/page_schema.md`.
5. Every page derived from a source carries `authority: external` (or
   `hybrid`) and lists the source in `sources:`. Authored pages are
   `authority: grimoire`.
6. Chapter-local `sources/` folders are immutable after a file lands there.
   Never edit a filed source in place; wiki pages carry the provenance
   pointers, source wrappers never carry backlinks.
7. Link to sources of truth; do not duplicate their content. Contradictions
   with existing pages are surfaced to the user; the wiki never silently
   overrides itself.
8. New content is wired into a hub (a chapter's `## Routes`, or the root hub)
   before the operation is complete. Do not file trivial one-liners; add what
   compounds.

---

## Step 0: Precondition

Resolve the active grimoire with the shared grimoire directory guard and set
`GRIMOIRE_ROOT`. Arcana is not a grimoire.

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Step 1: Decide the mode

- The argument names an existing file -> **File one source** (Step F).
- The argument names a folder, or is `inbox`, or there is no argument and
  `inbox/` holds files -> **Sweep a folder** (Step S).
- Anything else (a topic, "this answer", pasted text, or nothing) ->
  **Author** (Step A). If nothing was given and the inbox is empty, ask what
  to add.

---

## Step A: Author a page or chapter

### A1. Understand the material

What is being added: a topic the user describes, or a recent chat answer to
capture ("save this", "file the comparison we just did"). If unclear, ask.

### A2. Size it

Choose the smallest unit that fits, confirming with the user when ambiguous:

- **Page**: one focused idea (concept, entity, playbook, reference) inside an
  existing chapter. Go to A3.
- **Chapter**: a new area with several facets, or material no existing chapter
  fits. Go to A4.

A captured answer is almost always a page; reach for a chapter only when the
material opens a new routable area.

### A3. Add a page

1. **Placement and type.** Pick the most relevant chapter and a `type:`:
   `concept` (topic, technique, idea), `entity` (a specific person, project,
   product), `playbook` (a procedure; most "how do I X" answers), `reference`
   (comparison table, glossary entry, cheatsheet). Pick a slug in the
   grimoire's naming convention. If no chapter fits, make a chapter (A4).
2. **Stamp the page** so it never ships with a placeholder date:

   ```bash
   ARCANA_HOME/bin/arcana new_page \
     --grimoire GRIMOIRE_ROOT \
     --path chapters/<chapter>/<slug>.md \
     --type <concept|entity|playbook|reference> \
     --title "<Title>" \
     --apply
   ```

   Run it without `--apply` first to preview. It derives the
   `chapter/<chapter>` tag and refuses to overwrite. Add `--tags domain/<facet>`
   for extra facets; use `--authority hybrid --sources <path-or-url>` only when
   the page synthesizes filed source material.
3. **Write the body.** When capturing an answer, the conversation is the
   source material: distill it into clean prose (`Purpose`, `When to Use`,
   content, `Gotchas`, `Related`); never go beyond what was established.
4. **Wire it in.** Add a full-path wikilink under the chapter hub's
   `## Routes`.

### A4. Add a chapter

1. **Gather inputs** (one question at a time): chapter name (in the naming
   convention), one-line purpose, when to route here, knowledge sources to
   point at, and two to five sub-topics.
2. **Scaffold from the formula:**

   ```bash
   mkdir -p chapters/<chapter_name>
   cp ARCANA_HOME/formulae/chapter_hub.formula.md chapters/<chapter_name>/<chapter_name>.md
   ```

3. **Customize the hub.** Replace `{{CHAPTER_TITLE}}`, `{{CHAPTER_NAME}}`,
   `[purpose]`, `[when to use]`; set tag `chapter/<chapter_name>`; use
   `hub/sub` instead of `hub/chapter` when the chapter is nested. Add a
   `## Routes` line per child with full-path wikilinks. Verify no placeholders
   remain:

   ```bash
   grep -nE '\[(Chapter Name|purpose|when to use)\]|\{\{' chapters/<chapter_name>/<chapter_name>.md
   ```

4. **Seed leaf pages (optional)** with `new_page.py` as in A3, one per
   sub-topic; stubs with TODOs are fine.
5. **Register in the parent hub**: the root hub (`<grimoire>/<grimoire>.md`,
   under `## Route By Chapter`) for a top-level chapter, or the containing
   chapter's hub for a sub-chapter:

   ```markdown
   - <chapter description>: [[chapters/<chapter_name>/<chapter_name>|<Chapter Title>]]
   ```

Continue at **Step V**.

---

## Step F: File one source

The argument is a single immutable artifact (article, transcript, paper,
screenshot, PDF, dataset).

1. Identify the chapter, sub-chapter, project, or package the source
   supports and use that package's `sources/` folder, creating it if needed.
2. Pick a short slug in the naming convention and decide whether to file a
   raw artifact, a source wrapper, or both. A raw artifact keeps its original
   filename unless the user asks to rename it.
3. Text source: create `chapters/<path>/sources/<slug>.md` from
   `ARCANA_HOME/formulae/source.formula.md` with the cleaned plain-text body
   under `## Source Body`.
4. Binary or large source: copy the raw artifact to
   `chapters/<path>/sources/<slug>/<original-file>` and create
   `chapters/<path>/sources/<slug>.md` as the wrapper pointing at it.
5. A raw artifact that is already citation-ready and needs no wrapper: copy
   it to `chapters/<path>/sources/<slug>.<ext>` and cite that path directly.

Continue at **Step D**.

---

## Step S: Sweep a folder

The folder (or `inbox/`) holds mixed content; classify before doing anything
irreversible. If the user names no folder and `inbox/` does not exist, ask
whether to create it or to point at a specific path.

1. List every file recursively; skip hidden files and `.gitkeep`.
2. **Classify each file with the user** and confirm before acting:

   | Classification | Criteria | Action |
   |---|---|---|
   | **Source** | An external artifact worth citing: PDF, transcript, article, screenshot, dataset. Authored elsewhere. | File it under the relevant `chapters/<path>/sources/` folder with the rules of Step F, then synthesize per Step D. |
   | **Wiki content** | Authored prose meant to be wiki-shaped: notes, drafts, half-finished chapters, generated docs. | Promote to `chapters/<chapter>/<page>.md` with frontmatter (`authority: grimoire`, no `sources:` unless a filed artifact grounds it). Remove the original; its value now lives in the wiki. |
   | **Junk / unclear** | Duplicate, superseded, ambiguous, off-topic, or undecidable. | Leave in place and flag for the user. Never auto-delete. |

3. **Settle naming once.** If the material uses a casing other than the
   recorded convention (or none is recorded), ask once: apply the grimoire's
   convention to the promoted pages (recommended), keep the material's own
   casing (`preserve`), or decide case by case. Record a newly chosen
   convention in `grimoire.json` as `naming`.
4. Process sources first, then wiki content, junk last; for each batch run
   Step D, then continue with the next batch.
5. When done, the swept folder holds only items the user still has to judge.

---

## Step D: Derive and update the wiki (for filed material)

1. **Read the source(s) end to end** and, with the user, identify: existing
   pages that already cover the material (to update), entities or concepts
   mentioned repeatedly with no page (to propose), claims that contradict
   existing pages (to flag), and the chapter the content fits. Wait for
   confirmation before writing.
2. **Update affected pages.** Existing page: edit in place, keep the
   frontmatter, bump `last_verified` to today, add the source path to
   `sources:` without duplicates. New page: scaffold from
   `ARCANA_HOME/formulae/page.formula.md` (or stamp it with `new_page.py`)
   with the right `type:`; source-derived pages get `authority: external` and
   a `sources:` entry, promoted drafts get `authority: grimoire` (or `hybrid`
   when they cite an artifact). Link related pages with full-path wikilinks.
3. **Update the hubs.** Every chapter hub touched gets a wikilink to each new
   page under `## Routes`.

---

## Step V: Validate

```bash
ARCANA_HOME/bin/arcana validate --grimoire GRIMOIRE_ROOT structure frontmatter links provenance
```

Fix and re-run until clean, or run `/grm-check quick` for the whole
mechanical suite.

## Report

Surface in chat: the mode used; pages and chapters added or updated with
paths; sources filed with paths; hubs updated; items left for the user to
judge and why; contradictions surfaced; validator pass or fail.

## Related

- Page formula: `ARCANA_HOME/formulae/page.formula.md`
- Source formula: `ARCANA_HOME/formulae/source.formula.md`
- Chapter hub formula: `ARCANA_HOME/formulae/chapter_hub.formula.md`
- Page stamping rite: `ARCANA_HOME/rites/new_page.py`
- Page schema: `ARCANA_HOME/docs/page_schema.md`
- Drop zone contract: `inbox/README.md` in the grimoire
- Grimoire creation: [[invocations/grm/create_grimoire|create grimoire]]
- Share the result: [[invocations/grm/save|save]]
- Evaluate afterwards: [[invocations/grm/check|check]]
