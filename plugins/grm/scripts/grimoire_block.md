<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->
## Grimoire Knowledge Base

**Library**: `~/grimoires/library.json` - read this file to resolve named grimoire keys and their on-disk paths.

**Arcana key**: `ARCANA_HOME` - resolved from the library or defaults to `~/grimoires/arcana/`.

**Skills**: Arcana ships `/grm-*` grimoire verbs (`setup`, `create`, `add`, `save`, `update`, `check`, `move`, `remove`, `help`) and `/arc-*` maintainer verbs (`update`, `validate`, `improve`, `clean`, `help`). Each grimoire ships its own `/<skill prefix>-*` skills declared in its `grimoire.json`.

### Hub convention

For any folder F that acts as a router, the hub file is `F/<basename(F)>.md`. The grimoire root hub is `<grimoire>/<grimoire>.md`. A hub may route to sub-hubs, to leaf pages, or both - depth is open-ended. Routing follows hubs depth-first until a leaf answers the question; chains can be 2 hops (root -> leaf) or more (root -> chapter -> sub-chapter -> ... -> leaf), as deep as the topic warrants.

### Storage layers

- **`chapters/**/sources/`** - Immutable source artifacts and source wrappers (articles, transcripts, papers, screenshots) colocated with the chapter material they support. File during import, then read. Citation-stable: pages with `authority: external` cite paths under here.
- **`inbox/`** - Optional transient drop zone for mixed content awaiting classification. Cleared by `/grm-add`. Pages must NOT cite `inbox/` paths (contents disappear once processed).
- **`chapters/`** - LLM-authored knowledge pages. Every page carries YAML frontmatter (`type`, `title`, `tags`, `authority`, `sources`, `last_verified`); see `ARCANA_HOME/docs/page_schema.md`.
- **`publish/`** - Build/publishing-output layer (rendered site, exported bundle, generated artifacts); present in every grimoire, idle until you publish. Excluded from grimoire validation and from the knowledge graph; pages must NOT cite `publish/` paths. Build output under it is disposable and regenerable.

### Routing rules

1. Resolve the active grimoire from the working directory (its key in the library) or project context.
2. Open `<grimoire>/<grimoire>.md` for routing.
3. Use full-path Obsidian wikilinks (`[[chapters/path/to/page|label]]`) for every in-grimoire Markdown-page pointer; aliases are metadata only and never link targets. Keep display labels to the target filename, normalized for reading.
4. Cross-grimoire references use path placeholders (`ARCANA_HOME/...`, `<grimoire>/...`).
5. For Grimoire meta-knowledge: read `ARCANA_HOME/arcana.md`.
6. Do not modify Grimoire files unless a `/arc-*` skill, a grimoire skill, or explicit instruction asks for it.
7. Name new files and folders in the grimoire's recorded convention (`naming` in `grimoire.json`, default `snake_case`). Any casing is valid, consistency is the goal, links must match on-disk spelling exactly, and imported material is never renamed without asking.

### Text file standard

Arcana and grimoires use UTF-8 without BOM and LF line endings. Unicode is allowed when useful; mojibake and repair artifacts are not. Preserve this standard when editing files. In Arcana, run `/arc-validate encoding`; in a grimoire, run `/grm-check encoding`.

### Provenance

Pages with `authority: external` or `hybrid` cite their `sources:` (paths under `chapters/**/sources/` or external URLs). The `validate_provenance` rite enforces this. Do not author external pages without filing the source first via `/grm-add`.

### Operations vocabulary

| You want to | Skill |
|---|---|
| Join a grimoire your team has, turn a folder into one, or start your first one | `/grm-setup` |
| Put knowledge in: write up a topic, save a chat answer, or file a document, folder, or `inbox/` as cited sources | `/grm-add` |
| Share what you changed with your team (validate, commit, pull, push) | `/grm-save` |
| Pick up everyone else's changes and bring everything current | `/grm-update` |
| Check the grimoire: full health pass, or `quick`, a validator, `naming`, `boundaries`, `fix` | `/grm-check` |
| Rename, move, or delete a page or chapter and fix every link | `/grm-move`, `/grm-remove` |
| See the grimoire commands you can run | `/grm-help` |
<!-- END GRIMOIRE KNOWLEDGE BASE -->
