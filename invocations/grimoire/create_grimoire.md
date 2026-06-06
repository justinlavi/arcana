---
type: playbook
title: "Create Grimoire"
aliases: ["create-grimoire", "scaffold-grimoire"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-05-12
---

# Invocation: Create New Grimoire

## Purpose

AI-guided conversational setup that scaffolds a complete grimoire from the scaffold contract, registers it in the local library, and validates the result. Output is a working grimoire directory with customized root hub, README, manifest, `sources/`, `log.md`, and initial chapter skeletons (each with its own folder-named hub and frontmatter).

## Invocation

```
/grm-create
```

## Non-Negotiable Rules

1. One grimoire per domain.
2. Reference universal invocations/formulae via Arcana — don't copy them.
3. Practical folder names only (`templates/`, `scripts/`, `snippets/`). Never `invocations/`, `formulae/`, or `rites/` inside a grimoire.
4. No credentials, PII, or secrets.
5. Link to source systems; don't duplicate their content.
6. Designate an owner.
7. Every page carries canonical frontmatter (see `ARCANA_HOME/docs/page_schema.md`).
8. Hub naming: every folder F has a hub at `F/<basename(F)>.md`.

---

## Step 1: Discovery

Have a conversation, not a form. Ask one question at a time and probe for specifics:

- What subject area is this grimoire for? (Personal hobby? Team / project knowledge base? Something else?)
- What questions should the grimoire answer?
- What documents, processes, or knowledge does it cover?
- Who are the primary users — just you, a team, public?
- What 2-4 letter slug should prefix this grimoire's skills? Must match `^[a-z][a-z0-9]*$` (e.g. `cook` for a cooking grimoire yields `/cook-recipe-add`; `hr` for an HR grimoire yields `/hr-onboarding-checklist`).

Capture: `name`, `directory` (snake_case, conventionally `<topic>-grimoire`), `token` (all-caps), `skill_prefix`, `purpose` (one sentence), `purpose_detailed`, `owner` (whoever maintains it — a person, team, or "personal"), `creation_date` (today as `YYYY-MM-DD`), `repo_url` (the canonical git URL you intend to push this grimoire to — public GitHub, private GitLab, internal Gitea, etc. If you don't know it yet, accept the placeholder `<set this when you push to a git host>` and fix it later).

---

## Step 2: Suggest Chapters

Propose 5-10 chapters grounded in what the user described. Recommend they start with 3-5.

Chapter naming:
- `snake_case`, lowercase
- Specific (`sourdough` not `breads_stuff`; `pto_policies` not `hr_stuff`)
- Topic or action — typically nouns

Examples by grimoire flavor:
- Cooking grimoire: `recipes`, `techniques`, `equipment`, `ingredients`, `meal_plans`
- HR grimoire: `onboarding`, `policies`, `benefits`, `performance_reviews`, `offboarding`
- Engineering grimoire: `repo_structure`, `build_system`, `runbooks`, `code_standards`

Let the user select, rename, drop, or add chapters and provide a one-line description for each.

---

## Step 3: Scaffold from Contract

The scaffold inventory lives in
`ARCANA_HOME/formulae/grimoire/scaffold_contract.json`. Load that contract
before creating files. It is the only source for scaffold directories,
templated files, copied support files, managed Obsidian settings, and empty
directory markers.

Create the grimoire by applying the contract:

1. Create the target grimoire directory and run `git init`.
2. For every `directories[]` entry with `create: true`, create `path`.
3. Copy `root_hub.source` to `root_hub.target`, substituting
   `{{GRIMOIRE_DIRECTORY}}` in the target path.
4. For every `files[]` entry with `create: true`, copy `source` to `target`,
   substituting scaffold placeholders in target paths.
5. Replace placeholders in copied file contents during Step 4.

The root hub file is named after the grimoire directory (folder-name convention). `grimoire.json` is the grimoire's self-declared identity (name, skill prefix, description). `sources/` is the immutable sources layer; `inbox/` is the transient drop zone for mixed content awaiting classification; `.obsidian/app.json` and `.obsidian/graph.json` are managed scaffold files that preserve safe full-path wikilink behavior and Arcana's graph-view color groups; `log.md` is the append-only activity log.

---

## Step 4: Customize Manifest, Hub, README, Log

Replace placeholders. Confirm `skill_prefix` with the user before writing — it's load-bearing and must be unique across grimoires installed side-by-side.

**Description-duplication policy.** Three description shapes, each with one canonical home:

| Field | Length | Where it lives | Example |
|---|---|---|---|
| `{{GRIMOIRE_NAME}}` | brand only (one word usually) | H1 of root hub, `name` field of manifest | `Cooking`, `HR`, `Project Alpha` |
| `{{GRIMOIRE_PURPOSE}}` | short tagline (2-5 words) | manifest `description`, italic subtitle in root hub | `personal cooking knowledge`, `HR runbooks and policies`, `Project Alpha knowledge` |
| `{{GRIMOIRE_PURPOSE_DETAILED}}` | long-form paragraph | **only** `README.md` | full multi-sentence description |

Do not re-paste the long form into the manifest, the root hub, the log, or any skill file. If another page needs the description, link to README — don't copy it.

**`grimoire.json`**:
- `{{GRIMOIRE_DIRECTORY}}`
- `{{SKILL_PREFIX}}` (must match `^[a-z][a-z0-9]*$`)
- `{{GRIMOIRE_PURPOSE}}` (used as the manifest's `description` — short tagline, a few words; e.g. "personal cooking knowledge")

**`{{grimoire_directory}}.md`** (root hub):
- `{{GRIMOIRE_NAME}}`, `{{GRIMOIRE_NAME_LOWER}}`, `{{GRIMOIRE_DIRECTORY}}`, `{{GRIMOIRE_PURPOSE}}` (italic subtitle), `{{GRIMOIRE_DOMAIN}}`, `{{SKILL_PREFIX}}`
- The hub uses `{{GRIMOIRE_PURPOSE}}` as a short subtitle below the title and points readers at `README.md` for the long-form description. Do not add a multi-sentence Purpose section here.
- `{{CHAPTER_ROUTES}}` — one entry per selected chapter, using full-path wikilinks:
  ```markdown
 - <chapter description>: [[chapters/<chapter_name>/<chapter_name>|<chapter label>]]
  ```

**`README.md`** (the canonical home for the long-form description):
- `{{GRIMOIRE_NAME}}`, `{{GRIMOIRE_PURPOSE_DETAILED}}`, `{{GRIMOIRE_DIRECTORY}}`, `{{SKILL_PREFIX}}`
- `{{GRIMOIRE_REPO_URL}}` — the git URL captured in Step 1; used in the README's `## Installation` section so downstream consumers who discover this grimoire on a git host know to summon Arcana first rather than clone the grimoire directly. Leave the literal placeholder `<set this when you push to a git host>` if unknown.
- `{{EXAMPLE_CHAPTER}}` — pick one chapter from the user's selection
- `{{CHAPTER_LIST}}` — bulleted `**name** - description` per chapter
- `{{CHAPTER_TREE}}` — ASCII tree of `chapters/<name>/<name>.md`

**`log.md`**:
- `{{GRIMOIRE_NAME}}`, `{{CREATION_DATE}}`, `{{GRIMOIRE_DIRECTORY}}`

Verify no `{{` placeholders remain:

```bash
grep -r "{{" {{grimoire_directory}}/{{grimoire_directory}}.md {{grimoire_directory}}/README.md {{grimoire_directory}}/grimoire.json {{grimoire_directory}}/log.md
```

Remove any leftover `.gitkeep` files in chapter folders that get populated:

```bash
rm -f {{grimoire_directory}}/chapters/.gitkeep
```

---

## Step 5: Create Initial Chapters

For each selected chapter, follow `ARCANA_HOME/invocations/grimoire/add.md` with these inputs auto-filled:

- **name**: from selection
- **purpose**: from selection
- **starting pointers**: ask user, or use `"Define during usage"`
- **sub_topics**: suggest 2-3 inferred from the chapter (e.g. `onboarding` -> `first_day`, `first_week`, `manager_guide`)

Create chapter hub `chapters/<chapter>/<chapter>.md` with canonical frontmatter and routing to planned sub_topics. Do not generate full leaf docs in this pass — placeholders or TODOs in the chapter hub are acceptable.

If a chapter creation fails, report it and continue with the rest. The user can retry with `/grm-add <name>`.

---

## Step 6: Register in Library

Read `~/grimoires/library.json`. If absent, create it with the structure below. If present, add one entry under `grimoires`:

```json
"{{grimoire_directory}}": {
  "local_path": "$HOME/path/to/{{grimoire_directory}}",
  "online_path": null
}
```

Use the actual absolute path from Step 3. The library records location only — the skill prefix lives in `grimoire.json`.

Bootstrap form (if creating from scratch):

```json
{
  "grimoires": {
    "{{grimoire_directory}}": {
      "local_path": "$HOME/path/to/{{grimoire_directory}}",
      "online_path": null
    }
  }
}
```

If an automatic or manual agent instruction target from
`ARCANA_HOME/docs/agent_targets.md` lacks a `## Grimoire Knowledge Base`
section, instruct the user to paste the canonical block from
`ARCANA_HOME/rites/templates/grimoire_block.md`. That block is static across
new grimoires — only the library changes.

---

## Step 7: Register Skills

If the new grimoire declares a `skill_prefix` in `grimoire.json`, register its
skills so its `/<prefix>-*` commands become available:

```bash
python3 ARCANA_HOME/rites/sync_skills.py --grimoire .
```

Then tell the user to reopen their agent session - Claude Code and Codex cache
the skill listing at startup, so the new `/<prefix>-*` commands appear only after
a restart.

---

## Step 8: Validate

```bash
python3 ARCANA_HOME/rites/validate_grimoire_structure.py --grimoire .
python3 ARCANA_HOME/rites/validate_frontmatter.py --grimoire .
python3 ARCANA_HOME/rites/validate_links.py --grimoire .
```

Or invoke `/grm-validate` for the full mechanical pass.

If the relevant agent instruction file already includes the Grimoire block, also test routing by asking the agent: `"What chapters exist in {{grimoire_name}}?"`

---

## Related

- **Chapter creation**: [[invocations/grimoire/add|add]]
- **Template formula**: `ARCANA_HOME/formulae/grimoire/`
- **Page schema**: `ARCANA_HOME/docs/page_schema.md`
- **Skill registration**: `/arc-sync-skills` (reads each grimoire's `grimoire.json`)
- **Structure validator**: `/grm-validate structure`
- **Agent block**: `ARCANA_HOME/rites/templates/grimoire_block.md`
