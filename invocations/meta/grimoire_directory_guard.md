---
type: reference
title: "Grimoire Directory Guard"
aliases: ["domain-guard", "grimoire-cwd-guard", "active-grimoire-guard"]
tags: [arcana/invocations, type/reference, scope/meta]
authority: grimoire
last_verified: 2026-05-25
---

# Grimoire Directory Guard

Shared precondition for every Arcana skill that mutates or analyzes an active grimoire. Skills include this fragment via `!cat` so the guard contract stays single-sourced.

**Before doing anything else**, resolve one active grimoire root:

1. Read `~/grimoires/library.json`
2. Resolve each grimoire's `local_path` (expand `$HOME`)
3. Check whether the current working directory is equal to, or inside, any registered grimoire path
4. If yes, set `GRIMOIRE_ROOT` to that registered root and continue
5. If the current working directory is Arcana, refuse unless the user explicitly names a grimoire
6. If the current working directory is not inside a registered grimoire:
  - If there is exactly one registered grimoire, set `GRIMOIRE_ROOT` to it, tell the user which grimoire was selected, and continue
  - If there are multiple registered grimoires, list them and ask which one to use; continue only after the user chooses
  - If there are no registered grimoires, stop and tell the user to create or register one first

Do not require the terminal to `cd` into the grimoire after `GRIMOIRE_ROOT` is resolved. Prefer explicit paths:

- For mechanical rites, pass `--grimoire GRIMOIRE_ROOT`.
- For file reads and writes, use paths under `GRIMOIRE_ROOT`.
- For commands that truly require process cwd, set the command working directory to `GRIMOIRE_ROOT`.

If the active grimoire cannot be resolved without guessing, stop before reading or modifying grimoire content.
