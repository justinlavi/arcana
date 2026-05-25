---
type: reference
title: "VS Code Setup"
aliases: ["vscode", "vscode-setup", "editor-setup"]
tags: [type/reference, arcana/docs]
authority: grimoire
last_verified: 2026-05-19
---

# VS Code Setup

How to configure VS Code so wikilink Ctrl-click works against the workspace root instead of creating recursive directory trees relative to the current note.

This is a hard requirement for anyone editing grimoires in VS Code. Skip it and Ctrl-clicking any full-path wikilink will silently create a nested copy of the chapter tree (e.g. `chapters/build_system/ci/chapters/build_system/ci/gitlab_shell_ci.md`).

---

## The problem

VS Code's built-in markdown extension does not natively handle `[[wikilinks]]`. The **Markdown Preview Enhanced** (MPE) extension ships a `DocumentLinkProvider` for `[[...]]` that resolves wikilink targets relative to the current file. When the target doesn't exist at that relative path, Ctrl-click creates a new file there — silently, without prompting. From `chapters/build_system/ci/ci.md`, Ctrl-clicking `[[chapters/build_system/ci/gitlab_shell_ci|label]]` spawns `chapters/build_system/ci/chapters/build_system/ci/gitlab_shell_ci.md`.

This is the same root cause as the Obsidian recursive-directory bug, but VS Code ignores `.obsidian/app.json` entirely — the fix must happen on the VS Code side.

---

## Recommended setup

The simplest reliable setup is:

1. **Uninstall Markdown Preview Enhanced.** VS Code's built-in markdown preview is sufficient for everyday rendering and does not have the recursive-directory wikilink bug. Removing MPE eliminates the conflicting `DocumentLinkProvider` entirely.
2. **Install Foam** for wikilink Ctrl-click navigation against the workspace root.

If you need MPE's specific features (advanced math, custom mermaid themes, PlantUML, code-chunk execution), see *Keeping MPE installed* below for the disable-only workaround.

### 1. Uninstall MPE

```
code --uninstall-extension shd101wyy.markdown-preview-enhanced
```

After uninstalling, VS Code falls back to its built-in markdown preview (`Ctrl/Cmd+Shift+V`). The built-in preview renders standard CommonMark, GFM tables, and embedded images correctly — enough for reading grimoire pages.

### 2. Install Foam

```
code --install-extension foam.foam-vscode
```

Foam indexes the workspace by full path and resolves wikilinks against the workspace root. Full-path wikilinks like `[[chapters/build_system/ci/gitlab_shell_ci|label]]` then Ctrl-click to the actual file rather than a recursive ghost.

Foam's defaults work out of the box for Arcana's conventions; no extra Foam settings are required.

---

## Keeping MPE installed

If you have a reason to keep MPE (advanced rendering features), disable only its wikilink handler in your VS Code **user** settings (`~/.config/Code/User/settings.json` on Linux, `~/Library/Application Support/Code/User/settings.json` on macOS):

```json
"markdown-preview-enhanced.enableWikiLinkSyntax": false
```

MPE's preview rendering, math, mermaid, PlantUML, and other features keep working — only its wikilink Ctrl-click handler is disabled. Foam then handles wikilink navigation.

This works in principle, but uninstalling MPE is the cleaner fix: there's no risk of a future MPE update re-enabling the setting or shipping a new wikilink behavior. Disable-only is a fallback, not the recommendation.

### Without Foam

If you don't want Foam *and* you want to keep MPE, the disable setting still prevents the recursive-directory bug — but Ctrl-click on wikilinks becomes a no-op. You lose in-editor navigation entirely. Use Obsidian for that.

---

## Verifying the fix

1. Open any grimoire as a VS Code workspace.
2. Open a chapter that contains a full-path wikilink, e.g. `chapters/build_system/ci/ci.md`.
3. Ctrl-click the `[[chapters/build_system/ci/gitlab_shell_ci|gitlab_shell_ci]]` link.
4. The actual file `chapters/build_system/ci/gitlab_shell_ci.md` should open.
5. Confirm no `chapters/build_system/ci/chapters/...` directory was created.

If a recursive directory does appear, MPE (or another wikilink-providing extension) is still active — confirm MPE is uninstalled (`code --list-extensions | grep markdown-preview-enhanced` returns nothing) and Foam is installed, then restart VS Code.

---

## Cleaning up existing damage

If you find stray nested folders like `chapters/<chapter>/chapters/<chapter>/...` from previous bad Ctrl-clicks:

```bash
find chapters -type d -path '*/chapters/*chapters*'
# review the matches, then:
rm -rf <each-bad-path>
```

These are pure artifacts — they contain only stub files like `# cmake` from VS Code's auto-create flow. Deleting them removes nothing real.

---

## Why not workspace settings?

Workspace `.vscode/settings.json` per grimoire would scope the MPE-disable to each vault — but it only takes effect when you open the grimoire as its own workspace. Most contributors open `~/grimoires/` (or a single grimoire) as their workspace, so user-level settings are the more reliable place for this if you choose the disable-only path. The MPE-disable is harmless outside grimoire contexts: MPE's wikilink feature is rarely used in normal projects.

Either way — uninstall or user-level disable — workspace settings are not the right layer for this fix.

---

## Related

- Obsidian-side config (parallel concern): `ARCANA_HOME/docs/obsidian.md` — "Required app.json settings"
- Wikilink convention enforced by validators: same doc, "Full-path wikilinks" section
- Bulk wikilink repair rite: `ARCANA_HOME/rites/repair_links.py`
