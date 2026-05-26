# Formulae

Templates the LLM copies when scaffolding new content. Each `*.formula.md` carries placeholder frontmatter and body text - substitute the placeholders, drop the result into place, and run the relevant validator.

## What's here

| File | Use it for | Expanded by |
|---|---|---|
| [Page.Formula](page.formula.md) | A new authored knowledge page (concept, entity, source, playbook, reference) inside `chapters/`. Carries the canonical frontmatter shape. | `/grm-create-chapter`, `/grm-file-answer`, `/grm-ingest` |
| [Chapter Hub.Formula](chapter_hub.formula.md) | A new chapter or sub-chapter hub (`<folder>/<folder>.md`). Hub-level frontmatter and routing-list scaffolding. | `/grm-create-chapter` |
| [Source.Formula](source.formula.md) | A `type: source` wrapper under `sources/` with capture metadata, source body, or a pointer to a sibling raw artifact. | `/grm-ingest` |
| [Log Entry.Formula](log_entry.formula.md) | The shape of a single entry appended to a grimoire's `log.md`. | `rites/append_log.py`, called by every mutating skill |
| [Invocation.Formula](invocation.formula.md) | A new Arcana invocation (workflow doc referenced by a skill). Maintainer-only. | manual authoring |
| [README](grimoire/README.md) | Full grimoire scaffold - root hub, manifest, README, `sources/`, `inbox/`, `chapters/`, `log.md`, `.obsidian/`. Used to bootstrap a brand-new grimoire from scratch. | `/grm-create` |
| [`grimoire/scaffold_contract.json`](grimoire/scaffold_contract.json) | Machine-readable inventory for grimoire scaffold directories, copied files, managed files, and scaffold JSON requirements. | `/grm-create`, `/grm-improve`, `/grm-validate-structure`, tests |

## Conventions

- All templates carry placeholder YAML frontmatter; substitute values before saving.
- Machine-substituted placeholder tokens use `{{TOKEN}}` syntax. Bracketed prompts such as `[Title]` are human authoring cues inside generic page/source formulas, not scaffold variables. Canonical scaffold placeholders and their meanings live in [reference](../docs/reference.md#placeholders-in-formulae).
- The grimoire scaffold inventory lives in [`grimoire/scaffold_contract.json`](grimoire/scaffold_contract.json). Update that contract with every scaffold file or directory change.
- Templates are intentionally exempted from strict frontmatter validation (placeholders like `YYYY-MM-DD` would fail otherwise) - see [page schema](../docs/page_schema.md) for the spec applied after expansion.

## Editing a formula

Treat each template as a contract: every page produced from it must satisfy the canonical schema. Changes here propagate to every future scaffolded page, so update them deliberately and run `python3 rites/validate.py` after edits.
