# `publish/` - The Publishing Layer

This directory is the optional home for **turning the grimoire into a website**: the static-site generator's config, the build scripts that stage and render content, and the generated build output. It is the one place where publishing tooling lives, so the rest of the grimoire stays a clean authoring workspace.

Publishing is **optional**. A grimoire is fully usable as a local, AI-routed knowledge base with no site at all. This folder ships with every grimoire as the designated home for publishing tooling; until you publish, it simply holds this README and stays out of your way (see *If you never publish* below).

## Contract

- **Outside the knowledge graph.** `publish/` is not knowledge. Wiki pages must never set a `sources:` entry pointing at `publish/`, and nothing in `chapters/` should link into it.
- **Excluded from validation.** The grimoire validators skip `publish/` for links, orphans, encoding, format, portability, and doc-tree checks. Generator config, vendored dependencies, and build artifacts under here will not trip `/grm-validate` or `/grm-health-check`.
- **Build artifacts are disposable.** Anything the build emits (rendered HTML, search indexes, vendored modules) is regenerable. It can be `.gitignore`d or deleted; only your generator config and scripts are worth keeping under version control.
- **Tooling-shaped, not page-shaped.** No grimoire frontmatter, no naming convention, no hub - this folder follows the conventions of whatever site generator you choose.

## Choosing a method

Pick one static-site generator. **Quartz** is the documented default because it is built for linked Markdown notes and renders wikilinks, backlinks, a graph view, and full-text search with little configuration:

| Method | Best when |
|---|---|
| **Quartz** (default) | You want a digital-garden site that understands wikilinks, backlinks, and a graph view out of the box. |
| **MkDocs Material** | The grimoire reads like documentation and you want strong search and navigation. |
| **Hugo** | The grimoire is large or you want maximum build speed and theme control. |
| **Docusaurus** | You want a polished, product-style docs site with versioning. |
| **Obsidian Publish** | You author in Obsidian and want hosted, one-click publishing with no build pipeline to maintain. |

You only need one. The rest of this README describes the default Quartz-style flow; the same shape applies to any generator.

## The stage-then-build pattern

Do not point the generator at the grimoire root. The authoring layout (`chapters/`, `inbox/`, `skills/`, `publish/`, editor dotfiles) is not the layout readers should see. Instead, a build script **stages** a copy of just the publishable content into a generator content folder, then **builds** the site from that copy:

```text
stage  ->  copy the root hub + chapter folders into publish/<generator>/content/
build  ->  run the generator against the staged copy
output ->  static site lands in publish/<generator>/public/ (or the generator's output dir)
```

Staging keeps authoring and publishing decoupled: you edit the grimoire normally, then regenerate the site. Typical staging rules: copy the root hub to the site index, flatten `chapters/` so readers see chapter folders at the site root, and carry chapter-local `sources/` along with the chapters they belong to. Authoring-only folders (`inbox/`, `skills/`, `publish/`, templates, editor dotfiles) are not staged.

## Private content caveat

A grimoire can hold private material - drafts, internal notes, source PDFs, receipts, credentials, identity documents. **Publishing makes whatever you stage reachable.** Before you expose a site:

- Treat the staging step as a publish boundary. Audit the staged copy, not just your intent.
- Put access control in front of any site that carries private or operational content (for example an authenticating proxy with an email allowlist), and keep it enabled while the site is live.
- Keep severe secrets - passwords, API keys, payment or identity documents - out of the publish boundary entirely. A build-time audit that fails on such material is a good safety net.

## If you never publish

Nothing breaks. `publish/` stays idle - it holds only this README and is excluded from validation and the knowledge graph, so it never affects authoring, routing, or `/grm-validate`. When you are ready, drop your generator of choice in here and follow the stage-then-build pattern above. Anything the build later emits is disposable and regenerable; only your generator config and scripts are worth keeping under version control.
