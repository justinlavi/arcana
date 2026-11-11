---
type: playbook
title: "Setup"
aliases: ["setup", "grm-setup", "onboarding", "join-grimoire"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-11-11
---

# Invocation: Setup (first grimoire, or join one)

## Purpose

Hold the onboarding conversation. A person who has just
installed Arcana, or who has been told "we keep that in the Kutta grimoire",
should be able to say "set me up" and end with a grimoire on disk, registered,
and usable, without learning git or Arcana. Engineers get the same flow with
fewer questions.

The rite behind the join path is `rites/install_grimoire.py`; the state check
is `rites/summon.py --check`. Everything else here is conversation.

## Invocation

```
/grm-setup
/grm-setup <git url>
```

## Preconditions

None. This command works from any directory and is the one `/grm-*` command
that does not need an active grimoire. Never ask for a token, password, or
personal access token: git already holds the user's credentials for their host,
and when it does not, git's own credential helper prompts once (a browser
window on Windows and macOS, a terminal prompt on Linux). Say that this prompt
may appear and move on.

## Workflow

### 1. Look before asking

```bash
python3 ARCANA_HOME/rites/summon.py --check --format json
```

Read the envelope. It tells you whether the library exists, which grimoires are
registered, whether skills and the routing block are current, and whether
anything drifted. Do not ask the user for facts this envelope already holds.

### 2. Branch on what you found

- **A URL was passed as `$url`.** Skip to step 3 with it.
- **No grimoires registered.** Ask one question, offering three answers:
  1. *Join a grimoire your team already has* - "paste the repository link
     your teammate or your wiki gave you".
  2. *Start a new grimoire from scratch* - hand off to `/grm-create`.
  3. *Turn a folder of notes you already have into a grimoire* - hand off to
     `/grm-adopt`.
- **Grimoires already registered and nothing drifted.** Say so in one line,
  list them with their descriptions, and offer the same three answers plus
  "nothing, I'm set". If the check reported drift (stale skills or routing
  block, a grimoire behind its remote), offer `/grm-update` first.

### 3. Join: run the rite

```bash
python3 ARCANA_HOME/rites/install_grimoire.py "<url>" --format json
```

Accepts `https://...`, `git@host:path.git`, and local paths. The rite derives
the directory name from the repository name (`--name` overrides it), clones or
fast-forwards into `~/grimoires/<name>`, checks for `grimoire.json`, records
the library entry, and registers skills.

Read the envelope and report from it, never from assumption:

- `status: ok` - say where it landed and what it is (from the grimoire's
  `grimoire.json` description). Continue to step 4.
- `status: blocked` with `manifest: missing` - the repository is on disk but is
  not a grimoire yet. Offer `/grm-adopt <name>` and explain that it only writes
  a small identity file.
- `status: error` on clone - the three causes, in order of likelihood: the URL
  is wrong (compare it with what the teammate sent), the host needs VPN, or git
  has no credential for the host yet (re-run and watch for git's prompt). Do
  not retry in a loop; ask the user which it is.

### 4. Close the loop

1. Tell the user to open a fresh agent session so it sees the grimoire's
   skills (agents cache skill listings).
2. Name the five verbs they will use day to day, in plain words: ask (just
   talk; the agent routes through the grimoire), `/grm-add` to write something
   down, `/grm-import` to file a document, `/grm-save` to share what they
   changed, `/grm-update` to pick up everyone else's changes.
3. If the user is an engineer who mentioned a group or org URL, point out the
   terminal path for discovering many grimoires at once:
   `bash ARCANA_HOME/rites/summon.sh --scope <org url>`.

## Rules

- One question at a time, plain words, no git vocabulary unless the user used
  it first.
- Never ask for credentials. Never store a token in a file.
- Never clone into any directory other than `~/grimoires/<name>`; the rite
  owns the layout.
- Quote the rite's envelope for every claim about what happened.

## Related

- Join rite: `ARCANA_HOME/rites/install_grimoire.py`
- Start from scratch: [[invocations/grm/create_grimoire|create grimoire]]
- Adopt a folder: [[invocations/grm/adopt|adopt]]
- Bring everything current: [[invocations/grm/update|update]]
- Share changes: [[invocations/grm/save|save]]
