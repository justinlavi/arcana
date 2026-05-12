# Invocation: Create New Grimoire

## Purpose

AI-guided conversational setup that scaffolds a complete grimoire from the formula template, registers it in the local library, and validates the result. Output is a working grimoire directory with customized `INDEX.md`, `README.md`, `grimoire.json`, and initial chapter skeletons.

## Invocation

```
/grm-domain-create-grimoire
```

## Non-Negotiable Rules

1. One grimoire per domain.
2. Reference universal invocations/formulae via Arcana — don't copy them.
3. Practical folder names only (`templates/`, `scripts/`, `snippets/`). Never `invocations/`, `formulae/`, or `rites/` inside a domain grimoire.
4. No credentials, PII, or secrets.
5. Link to source systems; don't duplicate their content.
6. Designate an owner.

---

## Step 1: Discovery

Have a conversation, not a form. Ask one question at a time and probe for specifics:

- What subject area is this grimoire for? (Personal hobby? Team / project knowledge base? Something else?)
- What questions should the grimoire answer?
- What documents, processes, or knowledge does it cover?
- Who are the primary users — just you, a team, public?
- What 2–4 letter slug should prefix this grimoire's skills? Must match `^[a-z][a-z0-9]*$` (e.g. `cook` for a cooking grimoire yields `/cook-recipe-add`; `hr` for an HR grimoire yields `/hr-onboarding-checklist`).

Capture: `name`, `directory` (snake_case, conventionally `<topic>-grimoire`), `token` (all-caps), `skill_namespace`, `purpose` (one sentence), `purpose_detailed`, `owner` (whoever maintains it — a person, team, or "personal"), `creation_date` (today).

---

## Step 2: Suggest Chapters

Propose 5–10 chapters grounded in what the user described. Recommend they start with 3–5.

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

## Step 3: Scaffold from Template

```bash
mkdir {{grimoire_directory}} && cd {{grimoire_directory}}
git init
cp ~/grimoires/arcana/formulae/grimoire/INDEX.md .
cp ~/grimoires/arcana/formulae/grimoire/README.md .
cp ~/grimoires/arcana/formulae/grimoire/grimoire.json .
mkdir chapters skills
```

`grimoire.json` is the grimoire's self-declared identity (name, namespace, description) and the canonical source `/grm-skills-register` reads. `skills/` is created empty; populate as the grimoire grows.

---

## Step 4: Customize Manifest and Templates

Replace placeholders in the three copied files. Confirm `skill_namespace` with the user before writing — it's load-bearing and must be unique across grimoires installed side-by-side.

**`grimoire.json`**:
- `{{GRIMOIRE_DIRECTORY}}`
- `{{SKILL_NAMESPACE}}` (must match `^[a-z][a-z0-9]*$`)
- `{{GRIMOIRE_PURPOSE}}`

**`INDEX.md`**:
- `{{GRIMOIRE_NAME}}`, `{{GRIMOIRE_TOKEN}}`, `{{GRIMOIRE_PURPOSE}}`, `{{GRIMOIRE_DOMAIN}}`
- `{{CHAPTER_ROUTES}}` — one entry per selected chapter:
  ```markdown
  - <chapter description>:
    - `chapters/<chapter_name>/INDEX.md`
  ```

**`README.md`**:
- `{{GRIMOIRE_NAME}}`, `{{CREATION_DATE}}`, `{{OWNER_DOMAIN}}`, `{{GRIMOIRE_DOMAIN}}`
- `{{GRIMOIRE_PURPOSE}}`, `{{GRIMOIRE_PURPOSE_DETAILED}}`
- `{{GRIMOIRE_DIRECTORY}}`, `{{SKILL_NAMESPACE}}`
- `{{EXAMPLE_CHAPTER}}` — pick one chapter from the user's selection
- `{{CHAPTER_LIST}}` — bulleted `**name** - description` per chapter
- `{{CHAPTER_TREE}}` — ASCII tree of `chapters/<name>/`

Verify no `{{` placeholders remain:

```bash
grep -r "{{" {{grimoire_directory}}/INDEX.md {{grimoire_directory}}/README.md {{grimoire_directory}}/grimoire.json
```

Remove the template `.gitkeep`:

```bash
rm -f {{grimoire_directory}}/chapters/.gitkeep
```

---

## Step 5: Create Initial Chapters

For each selected chapter, follow `GRIMOIRE_ARCANA/invocations/grimoire/create_chapter.md` with these inputs auto-filled:

- **name**: from selection
- **purpose**: from selection
- **starting pointers**: ask user, or use `"Define during usage"`
- **sub_topics**: suggest 2–3 inferred from the chapter (e.g. `onboarding` → `first_day`, `first_week`, `manager_guide`)

Create chapter `INDEX.md` with routing to planned sub_topics. Do not generate full leaf docs in this pass — placeholders or TODOs in the chapter `INDEX.md` are acceptable.

If a chapter creation fails, report it and continue with the rest. The user can retry with `/grm-domain-create-chapter <name>`.

---

## Step 6: Register in Library

Read `~/grimoires/library.json`. If absent, create it with the structure below. If present, add one entry under `grimoires`:

```json
"{{grimoire_directory}}": {
  "local_path": "$HOME/path/to/{{grimoire_directory}}",
  "online_path": null
}
```

Use the actual absolute path from Step 3. The library records location only — the namespace lives in `grimoire.json`.

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

If `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md` lacks a `## Grimoire Knowledge Base` section, instruct the user to paste the canonical block from `GRIMOIRE_ARCANA/rites/templates/grimoire_block.md`. That block is static across new grimoires — only the library changes.

---

## Step 7: Validate

```bash
ls -la {{grimoire_directory}}/ {{grimoire_directory}}/chapters/
grep -r "{{" {{grimoire_directory}}/   # must return nothing
```

Then run:

```
/grm-domain-validate-structure
```

to confirm structural compliance. If the relevant agent instruction file already includes the Grimoire block, also test routing by asking the agent: `"What chapters exist in {{grimoire_name}}?"`

---

## Related

- **Chapter creation**: [`create_chapter.md`](create_chapter.md)
- **Template formula**: `GRIMOIRE_ARCANA/formulae/grimoire/`
- **Skill registration**: `/grm-skills-register` (reads each grimoire's `grimoire.json`)
- **Structure validator**: `/grm-domain-validate-structure`
- **Agent block**: `GRIMOIRE_ARCANA/rites/templates/grimoire_block.md`
