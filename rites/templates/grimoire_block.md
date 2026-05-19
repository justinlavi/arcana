<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->
## Grimoire Knowledge Base

**Library**: `~/grimoires/library.json` — read this file to resolve named grimoire keys and their on-disk paths.

**Arcana key**: `GRIMOIRE_ARCANA` — resolved from the library or defaults to `~/grimoires/arcana/`.

**Skills**: Arcana ships `/grm-*` skills (e.g. `/grm-meta-help`, `/grm-domain-ingest`, `/grm-domain-lint`, `/grm-domain-improve`). Each domain grimoire ships its own `/<namespace>-*` skills declared in its `grimoire.json`.

### Hub convention

For any folder F that acts as a router, the hub file is `F/<basename(F)>.md`. The grimoire root hub is `<grimoire>/<grimoire>.md`. A hub may route to sub-hubs, to leaf pages, or both — depth is open-ended. Routing follows hubs depth-first until a leaf answers the question; chains can be 2 hops (root → leaf) or more (root → chapter → sub-chapter → … → leaf), as deep as the topic warrants.

### Storage layers

- **`sources/`** — Immutable source artifacts (articles, transcripts, papers, screenshots). Read, never modify. Citation-stable: pages with `authority: external` cite paths under here.
- **`inbox/`** — Optional transient drop zone for mixed content awaiting classification. Cleared by `/grm-domain-ingest`. Pages must NOT cite `inbox/` paths (contents disappear once processed).
- **`chapters/`** — LLM-authored knowledge pages. Every page carries YAML frontmatter (`type`, `title`, `tags`, `authority`, `sources`, `last_verified`); see `GRIMOIRE_ARCANA/docs/page_schema.md`.
- **`log.md`** — Append-only activity log. Each entry begins `## [YYYY-MM-DD HH:MM] <op> | <title>`.

### Routing rules

1. Resolve the active grimoire from the working directory (its key in the library) or project context.
2. Open `<grimoire>/<grimoire>.md` for routing.
3. Use full-path Obsidian wikilinks (`[[chapters/path/to/page|label]]`) for in-grimoire pointers; aliases are metadata only and never link targets. Keep display labels to the target filename, normalized for reading.
4. Cross-grimoire references use path placeholders (`GRIMOIRE_ARCANA/...`, `<grimoire>/...`).
5. For Grimoire meta-knowledge: read `GRIMOIRE_ARCANA/arcana.md`.
6. Do not modify Grimoire files unless a `/grm-*` skill, a domain skill, or explicit instruction asks for it.

### Provenance

Pages with `authority: external` or `hybrid` cite their `sources:` (paths under `sources/` or external URLs). The `validate_provenance` rite enforces this. Do not author external pages without filing the source first via `/grm-domain-ingest`.

### Operations vocabulary

| You want to… | Skill |
|---|---|
| Ingest a single source | `/grm-domain-ingest <path>` |
| Sort a folder of mixed content (zip extract, drafts, etc.) | `/grm-domain-ingest <folder>` (or drop into `inbox/` and run `/grm-domain-ingest`) |
| Promote a chat answer into a wiki page | `/grm-domain-file-answer` |
| Health-check the grimoire | `/grm-domain-lint` |
| Add a new chapter | `/grm-domain-create-chapter` |
| Audit naming and structure | `/grm-domain-improve` |
| List every skill installed | `/grm-meta-help` |
<!-- END GRIMOIRE KNOWLEDGE BASE -->
