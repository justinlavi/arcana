# Invocation: Create Grimoire Chapter

## Purpose

Scaffold a new knowledge chapter inside the active domain grimoire — copy `chapter_index.formula.md`, customize placeholders, optionally seed leaf docs from `page.formula.md`, and register the chapter in the grimoire's root `INDEX.md`.

## Invocation

```
/grm-domain-create-chapter
```

Or with a topic:

```
/grm-domain-create-chapter for <topic>
```

## Non-Negotiable Rules

1. Chapter names are `snake_case`, lowercase, specific (`pto_policies`, not `hr_stuff`).
2. Practical folder names only inside chapters (`templates/`, `scripts/`, `snippets/`). Never `invocations/`, `formulae/`, or `rites/` — those live only in Arcana.
3. Link to source systems; don't duplicate their content.
4. Update the grimoire's root `INDEX.md` so the chapter is routable.

---

## Step 0: Precondition

Verify the working directory is a registered domain grimoire by checking `~/grimoires/library.json`. Arcana is not a grimoire. If the check fails, list available grimoires from the library and tell the user to `cd` into one. **Stop.**

---

## Step 1: Gather Inputs

Have a short conversation. Ask one question at a time:

- **Chapter name** (`snake_case`, specific, scope-appropriate)
- **One-line purpose** — what knowledge does this chapter hold?
- **When to route here** — what kinds of questions land here?
- **Knowledge sources** — wikis, drives, repos, tribal knowledge to point at
- **Sub-topics** — 2–5 leaf docs the chapter will eventually contain

Capture: `chapter_name`, `chapter_title` (Title Case), `purpose`, `when_to_use`, `sources[]`, `sub_topics[]`.

---

## Step 2: Scaffold from Formula

```bash
mkdir -p chapters/{{chapter_name}}
cp ~/grimoires/arcana/formulae/chapter_index.formula.md chapters/{{chapter_name}}/INDEX.md
```

---

## Step 3: Customize Chapter INDEX.md

Edit `chapters/{{chapter_name}}/INDEX.md` and replace placeholders:

- `[Chapter Name]` → `{{chapter_title}}`
- `[purpose]` → `{{purpose}}`
- `[when to use]` → `{{when_to_use}}`
- Routes block — one line per sub-topic:
  ```markdown
  - <sub-topic description> → <sub_topic>.md
  ```

Verify no placeholder syntax remains:

```bash
grep -nE '\[(Chapter Name|purpose|when to use)\]|\{\{' chapters/{{chapter_name}}/INDEX.md
```

---

## Step 4: Seed Leaf Docs (Optional)

For each sub-topic the user wants stubbed now:

```bash
cp ~/grimoires/arcana/formulae/page.formula.md chapters/{{chapter_name}}/{{sub_topic}}.md
```

Edit each leaf to fill: `Purpose`, `When to use`, `Primary Sources` (if external), content sections, `Gotchas`, `Related docs`.

Content rules:

- **Do** point at sources of truth for drift-sensitive values; include "as of <date> — VERIFY BEFORE USE" when snapshotting.
- **Do** use Grimoire as the canonical home for grimoire-native knowledge.
- **Don't** duplicate content from another chapter — link to it.
- **Don't** store implementation values without query instructions.

Stubs with TODOs are acceptable — leaf authoring can happen later.

---

## Step 5: Register in Root INDEX.md

Edit the grimoire root `INDEX.md`. Under the `## Route By Chapter` section, add:

```markdown
- <chapter description>:
  - `chapters/{{chapter_name}}/INDEX.md`
```

Keep entries alphabetized or grouped by domain — match the existing convention in the file.

---

## Step 6: Validate

```bash
ls chapters/{{chapter_name}}/
grep -n "{{chapter_name}}" INDEX.md   # must find the new route
```

Then run:

```
/grm-domain-validate-structure
```

to confirm the chapter conforms to grimoire structure rules.

---

## Related

- **Chapter formula**: `~/grimoires/arcana/formulae/chapter_index.formula.md`
- **Page formula**: `~/grimoires/arcana/formulae/page.formula.md`
- **Grimoire creation**: [`create_grimoire.md`](create_grimoire.md)
- **Structure validator**: `/grm-domain-validate-structure`
