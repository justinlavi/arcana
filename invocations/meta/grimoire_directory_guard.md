---
type: reference
title: "Grimoire Directory Guard"
aliases: ["domain-guard", "grimoire-cwd-guard"]
tags: [arcana/invocations, type/reference, scope/meta]
authority: grimoire
last_verified: 2026-05-15
---

# Grimoire Directory Guard

Shared precondition for every Arcana skill that mutates or analyzes an active grimoire (`/grm-*` operations that act on `cwd`). Skills include this fragment via `!cat` so the guard contract stays single-sourced.

**Before doing anything else**, verify the current working directory is a registered grimoire:

1. Read `~/grimoires/library.json`
2. Resolve each grimoire's `local_path` (expand `$HOME`)
3. Check if the current working directory matches any registered grimoire path

**If the directory is NOT a registered grimoire** (including Arcana - Arcana is not a grimoire):

- Display a clear error: "This skill operates on grimoires. Your current directory is not a registered grimoire."
- List available grimoires from the library with their paths
- Tell the user to `cd` to a grimoire directory and re-run
- **Stop.** Do not proceed.
