<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->
## Grimoire Knowledge Base

**Library**: `~/grimoires/library.json` - read this file to resolve named grimoire keys and their on-disk paths.

**Arcana key**: `ARCANA_HOME` - resolved from the library or defaults to `~/grimoires/arcana/`.

**Skills**: Arcana ships `/arc-*` platform skills (e.g. `/arc-help`, `/arc-agent-register-skills`) and `/grm-*` universal grimoire skills (e.g. `/grm-ingest`, `/grm-lint`, `/grm-improve`). Each grimoire ships its own `/<skill prefix>-*` skills declared in its `grimoire.json`.

### Hub convention

For any folder F that acts as a router, the hub file is `F/<basename(F)>.md`. The grimoire root hub is `<grimoire>/<grimoire>.md`. A hub may route to sub-hubs, to leaf pages, or both - depth is open-ended. Routing follows hubs depth-first until a leaf answers the question; chains can be 2 hops (root -> leaf) or more (root -> chapter -> sub-chapter -> ... -> leaf), as deep as the topic warrants.

### Storage layers

- **`sources/`** - Immutable source artifacts and source wrappers (articles, transcripts, papers, screenshots). File during ingest, then read. Citation-stable: pages with `authority: external` cite paths under here.
- **`inbox/`** - Optional transient drop zone for mixed content awaiting classification. Cleared by `/grm-ingest`. Pages must NOT cite `inbox/` paths (contents disappear once processed).
- **`chapters/`** - LLM-authored knowledge pages. Every page carries YAML frontmatter (`type`, `title`, `tags`, `authority`, `sources`, `last_verified`); see `ARCANA_HOME/docs/page_schema.md`.
- **`log.md`** - Append-only activity log. Each entry begins `## [YYYY-MM-DD HH:MM] <op> | <title>`.

### Routing rules

1. Resolve the active grimoire from the working directory (its key in the library) or project context.
2. Open `<grimoire>/<grimoire>.md` for routing.
3. Use full-path Obsidian wikilinks (`[[chapters/path/to/page|label]]`) for every in-grimoire Markdown-page pointer; aliases are metadata only and never link targets. Keep display labels to the target filename, normalized for reading.
4. Cross-grimoire references use path placeholders (`ARCANA_HOME/...`, `<grimoire>/...`).
5. For Grimoire meta-knowledge: read `ARCANA_HOME/arcana.md`.
6. Do not modify Grimoire files unless a `/arc-*` skill, a grimoire skill, or explicit instruction asks for it.

### Text file standard

Arcana and grimoires use UTF-8 without BOM and LF line endings. Unicode is allowed when useful; mojibake and repair artifacts are not. Preserve this standard when editing files. In Arcana, run `/arc-validate-encoding`; in a grimoire, run `/grm-validate-encoding`.

### Provenance

Pages with `authority: external` or `hybrid` cite their `sources:` (paths under `sources/` or external URLs). The `validate_provenance` rite enforces this. Do not author external pages without filing the source first via `/grm-ingest`.

### Operations vocabulary

| You want to | Skill |
|---|---|
| Ingest a single source | `/grm-ingest <path>` |
| Sort a folder of mixed content (zip extract, drafts, etc.) | `/grm-ingest <folder>` (or drop into `inbox/` and run `/grm-ingest`) |
| Promote a chat answer into a wiki page | `/grm-file-answer` |
| Health-check the grimoire | `/grm-lint` |
| Add a new chapter | `/grm-create-chapter` |
| Audit naming and structure | `/grm-improve` |
| List every skill installed | `/arc-help` |
<!-- END GRIMOIRE KNOWLEDGE BASE -->
