---
type: playbook
title: "Publish"
aliases: ["publish", "grm-publish", "site", "static-site"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-11-12
---

# Invocation: Publish (turn the grimoire into a site)

## Purpose

Give a grimoire a website that its readers can open in a browser, built the
same way locally and in CI, with a publish boundary that is audited before
anything is exposed. The pipeline is stage, audit, generate, audit:
`rites/stage_publish.py` copies the publishable content into
`publish/content/` with links rewritten for the flattened tree,
`rites/audit_publish.py` refuses blockers (credentials, card numbers,
identity documents, authoring roots), Quartz renders the site into
`publish/quartz/public/`, and the audit runs once more over the generated
HTML. `publish/build.sh` runs those four steps everywhere.

## Invocation

```
/grm-publish init <target>     # target: gitlab-pages | github-pages | cloudflare
/grm-publish build             # stage, audit, generate, audit the output, locally
/grm-publish check             # stage and audit only; no generator, no Node needed
```

## Preconditions

!`cat ARCANA_HOME/invocations/meta/grimoire_directory_guard.md`

`build` needs Node.js 22+ and npm on the machine; `check` needs only Python
and git. Never bypass a blocker finding. Warnings mean "fine behind access
control": confirm the site will sit behind one (GitLab Pages access control,
Cloudflare Access, a private GitHub Pages site) before telling the user it is
safe.

## Scope: `init <target>`

Set the grimoire up to publish, once. Ask only for what the formulae cannot
guess: the site title (default: the grimoire's name) and, for Cloudflare, the
hostname; GitLab and GitHub Pages derive their URL from the project.

1. Copy the publishing formulae into `publish/`:

   ```bash
   cp ARCANA_HOME/formulae/publish/publish.json GRIMOIRE_ROOT/publish/publish.json
   cp ARCANA_HOME/formulae/publish/build.sh GRIMOIRE_ROOT/publish/build.sh
   cp ARCANA_HOME/formulae/publish/quartz.config.yaml GRIMOIRE_ROOT/publish/quartz.config.yaml
   ```

   Then fill `{{SITE_TITLE}}` and `{{BASE_URL}}` in `quartz.config.yaml`
   (`baseUrl` is the hostname without a scheme, for example
   `team.pages.example.com`; for GitLab Pages under a group path include the
   path, `group.pages.example.com/grimoire`).

2. Copy the CI template for the target and tell the user where it goes:
   - `gitlab-pages`: `ARCANA_HOME/formulae/publish/ci/gitlab-pages.yml` ->
     `GRIMOIRE_ROOT/.gitlab-ci.yml`. Mention "Pages access control: project
     members" in the project's Pages settings.
   - `github-pages`: `ARCANA_HOME/formulae/publish/ci/github-pages.yml` ->
     `GRIMOIRE_ROOT/.github/workflows/pages.yml`; the repository's Pages
     source must be "GitHub Actions". Say plainly that a free-plan site is
     public.
   - `cloudflare`: show `ARCANA_HOME/formulae/publish/ci/cloudflare_pages.md`
     and write `GRIMOIRE_ROOT/publish/wrangler.jsonc` from its sample with the
     user's Worker name and hostname.

   If the grimoire lives on a private host, set `ARCANA_URL` in the CI file
   to the engine mirror the runner can reach.

3. Make sure `.gitignore` ignores `publish/content/`, `publish/quartz/`, and
   `publish/.engine/` (the seeded scaffold ignore file already does). Only
   `publish.json`, `build.sh`, `quartz.config.yaml`, the CI file, and any
   `wrangler.jsonc` are committed.

4. Record exclusions the grimoire needs in `publish/publish.json` (`exclude`:
   paths under `chapters/` that must never publish, such as a trip template
   package) and any domain-specific `audit.warning_patterns` or
   `audit.known_identifier_patterns`.

5. Run the `check` scope and report its findings before the first push.

## Scope: `build`

```bash
bash GRIMOIRE_ROOT/publish/build.sh
```

Report the audit's blocker and warning counts, where the site landed
(`publish/quartz/public/`), and remind the user that the committed files are
the configuration, never the output.

## Scope: `check`

```bash
ARCANA_HOME/bin/arcana stage_publish --grimoire GRIMOIRE_ROOT --apply
ARCANA_HOME/bin/arcana audit_publish --grimoire GRIMOIRE_ROOT --mode content --format json
```

Read the diagnostics: every `PUBLISH_BLOCKER` is a stop with its file and
action; `PUBLISH_WARNING`s are listed by risk with counts. Offer the fixes:
move the material outside the publish boundary, add an exclusion, or turn an
unlinked source path into a Markdown link.

## Related

- Staging rite: `ARCANA_HOME/rites/stage_publish.py`
- Audit rite: `ARCANA_HOME/rites/audit_publish.py`
- Formulae: `ARCANA_HOME/formulae/publish/`
- The layer's contract: `publish/README.md` in the grimoire
- Share the configuration with the team: [[invocations/grm/save|save]]
