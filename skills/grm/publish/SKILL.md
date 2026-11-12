---
name: {{SKILL_PREFIX}}-publish
description: Turn the active grimoire into a website - set up publishing once (GitLab Pages, GitHub Pages, or Cloudflare), build the site locally, or check what would be published and what the audit says
when_to_use: User wants a web version of the grimoire, asks to publish it, set up GitLab Pages or GitHub Pages or Cloudflare, build the site, or check whether anything private would leak. "publish the grimoire", "make a website", "set up pages", "build the site", "is it safe to publish". Operates on the resolved active grimoire.
argument-hint: "[init <gitlab-pages|github-pages|cloudflare> | build | check]"
arguments: scope
user-invocable: true
allowed-tools: Bash Read Write Edit
---

# Publish

You are turning the active grimoire into a website, or checking what would be published. The scope is: **$scope**. Follow the invocation below exactly; never bypass a blocker finding.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Staging rite**: `{{ARCANA_PATH}}/rites/stage_publish.py`
- **Audit rite**: `{{ARCANA_PATH}}/rites/audit_publish.py`
- **Formulae**: `{{ARCANA_PATH}}/formulae/publish/`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/grm/publish.md`
