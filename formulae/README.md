# Formulae

Templates the LLM copies when scaffolding new content. Each `*.formula.md` carries placeholder frontmatter and body text — substitute the placeholders, drop the result into place, and run the relevant validator.

## What's here

| File | Use it for | Expanded by |
|---|---|---|
| [`page.formula.md`](page.formula.md) | A new authored knowledge page (concept, entity, source, playbook, reference) inside `chapters/`. Carries the canonical frontmatter shape. | `/grm-domain-create-chapter`, `/grm-domain-file-answer`, `/grm-domain-ingest` |
| [`chapter_hub.formula.md`](chapter_hub.formula.md) | A new chapter or sub-chapter hub (`<folder>/<folder>.md`). Hub-level frontmatter and routing-list scaffolding. | `/grm-domain-create-chapter` |
| [`source.formula.md`](source.formula.md) | A `type: source` page that wraps an immutable artifact under `sources/` with summary frontmatter. | `/grm-domain-ingest` |
| [`log_entry.formula.md`](log_entry.formula.md) | The shape of a single entry appended to a grimoire's `log.md`. | `rites/append_log.py`, called by every mutating skill |
| [`invocation.formula.md`](invocation.formula.md) | A new Arcana invocation (workflow doc referenced by a skill). Maintainer-only. | manual authoring |
| [`grimoire/`](grimoire/) | Full grimoire scaffold — root hub, manifest, README, `sources/`, `inbox/`, `chapters/`, `log.md`, `.obsidian/`. Used to bootstrap a brand-new grimoire from scratch. | `/grm-domain-create-grimoire` |

## Conventions

- All templates carry placeholder YAML frontmatter; substitute values before saving.
- Placeholder tokens use `{{TOKEN}}` syntax. Canonical placeholders and their meanings live in [`docs/reference.md`](../docs/reference.md#placeholders-in-formulae).
- Templates are intentionally exempted from strict frontmatter validation (placeholders like `YYYY-MM-DD` would fail otherwise) — see [`docs/page_schema.md`](../docs/page_schema.md) for the spec applied after expansion.

## Editing a formula

Treat each template as a contract: every page produced from it must satisfy the canonical schema. Changes here propagate to every future scaffolded page, so update them deliberately and run `python3 rites/validate.py` after edits.
