# `publish/` - The Publishing Layer

This directory is the home for **turning the grimoire into a website**: the site generator's configuration, the build script, and the generated output. It is the one place where publishing tooling lives, so the rest of the grimoire stays a clean authoring workspace.

Publishing is **optional**. A grimoire is fully usable as a local, AI-routed knowledge base with no site at all. This folder ships with every grimoire; until you publish, it holds this README and stays out of your way.

## Contract

- **Outside the knowledge graph.** `publish/` is not knowledge. Wiki pages never set a `sources:` entry pointing at `publish/`, and nothing in `chapters/` links into it.
- **Excluded from validation.** The grimoire validators skip `publish/` for links, orphans, encoding, format, portability, and doc-tree checks.
- **Generated output is disposable.** `publish/content/` (the staged copy), `publish/quartz/` (the generator), and `publish/.engine/` (the engine a CI runner clones) are ignored by git and regenerable. The committed files are the configuration: `publish.json`, `build.sh`, `quartz.config.yaml`, the CI file, and any `wrangler.jsonc`.
- **Tooling-shaped, not page-shaped.** No grimoire frontmatter, no naming convention, no hub.

## The pipeline

`/grm-publish init <target>` sets a grimoire up once; `/grm-publish build` and `bash publish/build.sh` run the same four steps everywhere, locally and in CI:

```text
stage    arcana stage_publish    root hub -> content/index.md; chapters/* -> content/* (flattened, chapter-local sources carried, asset folders and publish.json exclusions left out, links rewritten)
audit    arcana audit_publish    blockers stop the build: credentials, card numbers, identity documents, authoring roots, unresolved sources
build    npx quartz build        Quartz 5, cloned into publish/quartz/ when absent, reads publish/content and writes publish/quartz/public
audit    arcana audit_publish    the generated HTML, for broken asset links and anything the first pass could not see
```

`publish/publish.json` holds the grimoire's choices: `exclude` (paths under `chapters/` that must never publish), `include_asset_folders`, and `audit.warning_patterns` / `audit.known_identifier_patterns` for domain-specific checks.

## Targets

| Target | What `init` writes | Access control |
|---|---|---|
| GitLab Pages | `.gitlab-ci.yml` | Pages access control set to project members |
| GitHub Pages | `.github/workflows/pages.yml` | Private Pages on a paid plan; public otherwise |
| Cloudflare | `publish/wrangler.jsonc` and the build settings | Cloudflare Access in front of the hostname |

Quartz is the default generator because it renders wikilinks, backlinks, and full-text search from Markdown with little configuration. Another generator fits the same shape: stage with `arcana stage_publish`, audit, run the generator against `publish/content/`, audit the output.

## Private content

A grimoire can hold private material. **Publishing makes whatever is staged reachable.** The audit refuses severe secrets outright and reports private operational detail (published documents and images, booking references, access codes) as warnings that are acceptable only behind access control. Treat the staged copy, not your intent, as the publish boundary, and keep access control enabled while the site is live.
