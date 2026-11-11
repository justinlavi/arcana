---
type: playbook
title: "Save"
aliases: ["save", "grm-save", "share-changes", "commit-and-push"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-11-11
---

# Invocation: Save (share what you changed)

## Purpose

Let someone who never types git commands share their grimoire edits with their
team. "Save" means: check the grimoire is valid, record the changes with a
short description, bring in whatever teammates saved meanwhile, and send the
result to the shared repository. The rite `rites/save_grimoire.py` does the
mechanical part and refuses anything unsafe; this playbook does the
conversation.

## Invocation

```
/grm-save
/grm-save "<what you changed>"
```

## Preconditions

!`cat ARCANA_HOME/invocations/meta/grimoire_directory_guard.md`

The grimoire must be a git repository. If it is not, say that there is no
shared copy to save to yet and offer to set one up with the user's git host.

## Workflow

### 1. Plan

```bash
python3 ARCANA_HOME/rites/save_grimoire.py --grimoire GRIMOIRE_ROOT --format json
```

The plan lists every change (added, changed, removed, new), the branch, and
how far it is ahead of or behind the shared copy. It also runs the grimoire
validators and stops with `status: blocked` if they fail.

- **Nothing to save** (`noop`, no changes, not ahead): say so and stop.
- **Validation failed**: show the failing validator(s) in plain words and
  offer to fix them (`/grm-validate`, or the specific repair). Do not save
  around a failure.
- **Changes present**: summarise them for the user in one or two sentences
  ("you added two pages under travel and changed the food hub").

### 2. Compose the message

Write a one-line description from the plan, in the past tense, naming what
changed rather than how ("Add Kyoto day plan and route it from the travel
hub"). If the user passed `$message`, use it. Show the line and ask for a yes
before saving. Keep it under 72 characters when you can.

### 3. Apply

```bash
python3 ARCANA_HOME/rites/save_grimoire.py --grimoire GRIMOIRE_ROOT --apply --message "<line>" --format json
```

Report from the envelope:

- `mutations` holds `commit` (with the short hash) and `push`. Say both in
  plain words: recorded, shared.
- `status: blocked` with a conflict message: teammates changed the same lines.
  The rite already aborted the rebase; the user's commit is safe locally.
  Name the files, explain that both versions need a human decision, and
  offer to walk through each file: show both versions, ask which to keep or
  how to merge, then re-run the save.
- `status: blocked` for identity: git does not know the user's name and
  email yet. Give the two `git config --global` lines from the message, run
  them with the user's values once they confirm, and re-run.
- `push failed`: usually VPN or credentials. The commit is kept; the user can
  re-run `/grm-save` later and only the push will happen.

### 4. Close

One line: what was shared, and that teammates receive it on their next
`/grm-update`.

## Rules

- Never force-push, never rewrite history, never discard the user's work. The
  rite enforces this; do not work around it with raw git.
- Never commit a grimoire that fails validation.
- Plain words. "Record" and "share", not "stage" and "push", unless the user
  speaks git.

## Related

- Save rite: `ARCANA_HOME/rites/save_grimoire.py`
- Pick up teammates' changes and bring everything current: [[invocations/grm/update|update]]
- Validate before saving: [[invocations/grm/validators/validate|validate]]
- First-time setup: [[invocations/grm/setup|setup]]
