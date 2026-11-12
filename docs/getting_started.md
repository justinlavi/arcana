---
type: reference
title: "Getting Started"
aliases: ["getting-started", "start-here", "grimoire-for-everyone"]
tags: [type/reference, arcana/docs, scope/onboarding]
authority: grimoire
last_verified: 2026-11-12
---

# Getting Started with Grimoire

A grimoire is a knowledge base your AI assistant reads and maintains with
you: the things your team knows, written down once, routed so the assistant
finds the right page instead of guessing. This page is for someone joining a
team that already has one, or starting their own, without being an engineer.
Arcana is the engine underneath; you never touch it.

## What you need

- **An AI coding assistant, signed in**: Claude Code (terminal, desktop app,
  or the VS Code extension) or Codex.
- **git** and **Python 3** on your computer. On Windows, install Python from
  python.org and tick "Add to PATH". Most work laptops already have both.
- **Access to your team's repository host** (GitHub, or your company's
  GitLab), with whatever sign-in you normally use for it.

## Install

**Claude Code** (two commands, inside a Claude Code session):

```text
/plugin marketplace add justinlavi/arcana
/plugin install grm@arcana
```

Then start a new session. The first session installs the engine for you and
tells you so. At a company that mirrors Arcana on its own GitLab, use that
address instead: `/plugin marketplace add https://gitlab.example.com/tools/arcana.git`.
If your IT team has preinstalled it, skip this step entirely.

**Codex, or any other assistant**: in a terminal, run the one-line installer
from [installation](installation.md#summoning-rite-codex-and-any-agent-without-plugins),
then open a new session.

## Set up

In a new session, type:

```text
/grm-setup
```

It asks what you want: join a grimoire your team already has (paste the
repository link a teammate gave you), start a new one, or turn a folder of
notes you already have into one. If your host needs a sign-in the first time,
git prompts you once, the way it does for any repository. When it finishes,
open one more new session so the assistant sees the grimoire's commands.

With the Claude Code plugin the commands are spelled `/grm:setup`,
`/grm:add`, and so on. Everywhere else they are `/grm-setup`, `/grm-add`.

## Day to day

Most of the time you do not run commands at all. You ask questions and the
assistant routes through the grimoire for the answer, citing the page it
read. When there is something to change, there are a handful of verbs:

| You want to | Say | Command |
|---|---|---|
| Write something down, or keep a good answer the assistant just gave | "add this to the grimoire" | `/grm-add` |
| File a document, a PDF, a folder of notes | "file this in the grimoire" | `/grm-add <path>` |
| Share your changes with the team | "save" | `/grm-save` |
| Pick up everyone else's changes | "update" | `/grm-update` |
| Find out whether the grimoire is in good shape | "check the grimoire" | `/grm-check` |
| Turn it into a website | "publish" | `/grm-publish` |
| Rename, move, or delete a page | "move X under Y", "remove X" | `/grm-move`, `/grm-remove` |
| See the commands | "help" | `/grm-help` |

Plain words work. The assistant picks the verb; you confirm before anything
is written or shared.

## Saving and updating

A grimoire lives in a git repository, which is how the whole team sees the
same thing. You do not need to know git:

- `/grm-save` checks the grimoire, records your changes with a one-line
  description you approve, brings in what teammates saved meanwhile, and
  sends yours. If you and a teammate changed the same lines, it stops, keeps
  your work safe, names the file, and walks you through choosing.
- `/grm-update` brings in everyone else's changes and keeps the engine and
  your commands current. With the Claude Code plugin this mostly happens on
  its own at the start of a session; the assistant tells you when something
  needs it.

## Publishing

`/grm-publish init gitlab-pages` (or `github-pages`, or `cloudflare`) sets a
grimoire up to build a website on every push, with an audit that refuses to
publish passwords, card numbers, or identity documents. Put access control in
front of the site before sharing the link; the assistant explains the option
for your host.

## When something looks wrong

- **A command is missing from the picker**: open a new session; assistants
  cache the command list. Still missing: `/grm-update skills`.
- **The assistant cannot find your grimoire**: `/grm-update library`, the
  fix after a folder was moved or renamed.
- **The assistant guesses instead of reading pages**: `/grm-update agentfile`
  refreshes its routing instructions.
- **"Python not found"** at the start of a session: install Python 3 and open
  a new session.

Everything above is deterministic where it can be and conversational where
it must be: the engine does the bookkeeping, the assistant does the asking,
and you decide.
