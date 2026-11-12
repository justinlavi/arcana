---
type: reference
title: "Cloudflare Build Settings"
aliases: ["cloudflare-pages", "cloudflare-publish"]
tags: [type/reference, arcana/formula, scope/publish]
authority: grimoire
last_verified: 2026-11-12
---

# Cloudflare: build settings

Cloudflare Workers Builds (or Pages) builds the site from the repository on
every push and serves `publish/quartz/public`. Put access control in front of
it with Cloudflare Access before sharing the URL.

| Setting | Value |
|---|---|
| Framework preset | None |
| Production branch | your default branch |
| Build command | `bash publish/build.sh` |
| Deploy command | `cd publish && npx wrangler deploy` |
| Build output directory | `publish/quartz/public` |
| Root directory | repository root |
| Environment variables | `ARCANA_URL` (your Arcana mirror, if any); `QUARTZ_REPO` / `QUARTZ_REF` to pin Quartz |

`publish/wrangler.jsonc` names the Worker, the static asset directory, and
any custom domains:

```jsonc
{
  "name": "<grimoire-name>",
  "compatibility_date": "2026-01-01",
  "assets": { "directory": "./quartz/public" },
  "routes": [
    { "pattern": "<your-domain>", "custom_domain": true }
  ]
}
```

Access control: in Cloudflare Zero Trust create a self-hosted application for
the site's hostname, choose an identity provider (the email one-time PIN
needs nothing but an inbox), add an Allow policy for the approved addresses,
and test with an unapproved address. Do not disable Access while the site is
deployed; the audit's warnings assume it is on.
