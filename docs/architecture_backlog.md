---
type: reference
title: "S-tier Architecture Backlog"
aliases: ["architecture-backlog", "s-tier-backlog", "deferred-architecture-items"]
tags: [type/reference, arcana/docs, scope/quality]
authority: grimoire
last_verified: 2026-11-10
---

# S-tier Architecture Backlog

## Purpose

Durable queue for deferred architecture opportunities found during
`/arc-improve` and `invocations/arc/quality/review_architecture.md`, and the
working design queue for the next release.

The architecture review report should mention deferred items in chat, but
large items also belong here when they need maintainer review, sequencing, or
explicit approval before implementation. This file is not a release note and
is not a substitute for `CHANGELOG.md`; it is the working design backlog for
moving Arcana from "correct and maintainable" to "self-explaining,
contract-driven, low-drift, and deeply testable."

## How To Use This Backlog

- Add items only when the change is too broad for the current `/arc-improve`
  pass, affects public command behavior, touches release/install behavior, or
  needs a new contract before implementation.
- Keep each item stable enough that a maintainer can name its ID
  and an agent can begin with the listed owner, first slice, and validation
  profile.
- When an item is implemented, either remove it in the same change or mark it
  as resolved with the release or commit where the work landed.
- If a future architecture review discovers the same concern again, merge it
  into the existing item instead of adding a duplicate.

Priority labels:

| Priority | Meaning |
|---|---|
| P0 | Blocking correctness or data-safety issue; implement before release. |
| P1 | High-leverage S-tier work; architecture remains correct but future drift or maintenance cost is likely. |
| P2 | Important scalability or clarity improvement; can wait behind P1 items. |
| P3 | Useful polish, generated convenience, or follow-up after larger contracts exist. |

## 1.8 Program: Grimoire for Everyone

Intake date 2026-11-10. Source: maintainer brief for the 1.8 cycle, distilled
into the items below. The brief's intent, in one sentence:

> Grimoire works superbly for one team of engineers who were taught it by hand.
> It cannot spread beyond them because installing, updating, publishing, and
> contributing all still assume an engineer. 1.8 removes those assumptions
> without weakening the engineer path.

Target population for every item: a business-development lead, an HR
representative, a systems engineer, or an IT administrator at a company with a
self-hosted GitLab behind a VPN, using Claude Code or Codex, who will never read
`docs/`. The engineer path must keep working unchanged or get strictly simpler.

Verified state the program starts from (see [CHANGELOG](../CHANGELOG.md)
`[1.8.0] - Unreleased` for what already landed):

- Installer: 5,083 lines across `summon.sh`, `summon.py`, `summon_core.py`,
  `summon_gui.py` (2,480 lines, Dear PyGui), `summon_state.py`,
  `summon_contract.py`, `build_summon_binary.py`; four PyInstaller release
  binaries built by `summon-release.yml`; private-host discovery through
  `GITLAB_TOKEN` / `GITHUB_TOKEN` environment variables.
- Casing: `validate_naming` runs for Arcana only (see
  `rites/data/validators.json`). Grimoires are held to snake_case only by
  invocations, docs, the routing block, and `/grm-audit-semantics`. Wikilink
  resolution uses `Path.resolve()` + `is_file()`, so a wrong-case link passes on
  Windows and macOS and breaks on Linux and in site builds (probed 2026-11-10:
  `[[chapters/RECIPES/recipes]]` validated clean on Windows). CI runs on
  Ubuntu only, so Windows-only failures never surface before release.
- `log.md`: every mutating invocation appends through `append_log.py`; no
  invocation, rite, or skill reads it. It is also an append-only file at the
  grimoire root, which guarantees merge conflicts for any two people editing a
  shared grimoire at once.
- Agent ecosystem drift since 1.7.0: Codex deprecated `~/.codex/skills` in
  favour of `~/.agents/skills` (still loaded, but legacy); both Claude Code and
  Codex now ship plugin systems with marketplaces, and Codex reads a Claude Code
  `.claude-plugin/marketplace.json`, so one git repository can serve both;
  Claude Code `SessionStart` hooks inject plain stdout as session context;
  Claude Code admins can force-install plugins and marketplaces through managed
  settings; the `!cat` dynamic-context syntax Arcana skills depend on can be
  disabled by an admin setting (`disableSkillShellExecution`).
- Publishing: the only working pipeline (stage, audit, Quartz build, Cloudflare)
  lives inside `japan-grimoire/publish/` with a 291-file vendored Quartz
  checkout. Arcana ships only `formulae/grimoire/publish/README.md`.

### Decisions needed before implementation

These are maintainer sign-off items under
[governance](governance.md#human-sign-off). Each is referenced by the items
that depend on it.

| ID | Decision | Recommendation |
|---|---|---|
| D1 | Package Arcana and grimoires as agent plugins (Claude Code and Codex), or keep the flat `sync_skills` registration as the only mechanism? Plugin skills are namespaced (`/grm:add` instead of `/grm-add`), which is a public command change. | Adopt plugins as the primary distribution for Claude Code in 1.8, with the `arc` and `grm` command families becoming two plugins, so names become `/grm:add` and `/arc:validate`. Keep flat skill registration as a permanent first-class path, not a deprecated fallback: the Codex IDE extension does not support plugins at all (verified 2026-11-10 against the Codex plugin docs), and Cursor and Copilot have no plugin path either. Codex therefore gets skills in `~/.agents/skills` plus the file-injected routing block. Approved 2026-11-10. |
| D2 | Retire `log.md` as a required scaffold file? | Yes. Make it optional, stop appending, derive "recent activity" from git on demand. Existing files stay valid, so this is MINOR. |
| D3 | Casing policy: how to keep grimoires consistent without forcing a rename of imported material? | Any casing is valid; consistency within a grimoire is the goal; snake_case is the default. Each grimoire records its convention once (`naming` in `grimoire.json`, set by `/grm-create` or on the first import or add that raises the question). The AI applies the recorded convention to new material, asks before renaming anything imported, and may accept a case-by-case exception the user states. Validators enforce only what breaks machines: exact-case links and no case-insensitive collisions; the convention itself is advisory and reported by `/grm-audit-semantics`. |
| D4 | Delete the GUI and release binaries outright in 1.8, or deprecate for one minor? | Delete in 1.8. The maintainer asked for removal; nothing in a grimoire depends on the GUI; the CLI path and the plugin path both replace it. |
| D5 | Does the 1.8 scope include a the proposed `grm-save` skill (commit and push) verb for non-engineers? | Yes. Without it a layperson can read and edit but never share, which is the proliferation blocker the brief describes. |

### Decision Queue

| ID | Priority | Item | Primary owner | Why deferred |
|---|---|---|---|---|
| AB-17 | P0 | Resolved on `release/1.8` (2026-11-10): skills fail to load outside the grimoires directory; invocations are now rendered into generated skills at registration | `rites/sync_skills.py`, every `skills/**/SKILL.md`, `docs/skill_schema.md`, `docs/agent_configuration.md` | Verified 2026-11-10; changes the generated skill contract and the plugin build. Absorbs AB-14. |
| AB-01 | P0 | Resolved on `release/1.8` (2026-11-10): case-exact wikilinks and case-collision portability checks | `rites/validate_links.py`, `rites/validate_portability.py`, `rites/_lib.py` | Needs D3; changes validator contracts. |
| AB-02 | P0 | Resolved on `release/1.8` (2026-11-10): Windows in the CI matrix | `.github/workflows/ci.yml` | Release-process change. |
| AB-03 | P1 | Resolved on `release/1.8` (2026-11-10): casing freedom across invocations, docs, routing block, and rites | `invocations/grm/*`, `docs/operating_model.md`, `rites/templates/grimoire_block.md`, `rites/new_page.py`, `rites/restructure_grimoire.py` | Needs D3; touches many public surfaces. |
| AB-04 | P1 | Resolved on `release/1.8` (2026-11-11): retire `log.md`; derive activity from git | `formulae/grimoire/scaffold_contract.json`, `rites/validate_grimoire_structure.py`, `rites/append_log.py`, every `invocations/grm/*` that appends | Needs D2; scaffold contract and command surface change. |
| AB-05 | P1 | Resolved on `release/1.8` (2026-11-11): remove the GUI, the release binaries, and the binary release workflow | `rites/summon_gui.py`, `rites/build_summon_binary.py`, `.github/workflows/summon-release.yml`, `rites/data/summon_contract.json`, `pyproject.toml` | Needs D4; deletion and install-behavior change. |
| AB-06 | P1 | Resolved on `release/1.8` (2026-11-10): Codex skill target moves to `~/.agents/skills` | `rites/data/agent_targets.json`, `rites/sync_skills.py`, `docs/agent_targets.md` | Public install-behavior change; needs migration cleanup of the deprecated directory. |
| AB-07 | P1 | Arcana as a plugin; `~/grimoires` as a local marketplace | new `.claude-plugin/`, `formulae/grimoire/scaffold_contract.json`, `rites/sync_skills.py`, `rites/data/agent_targets.json` | Needs D1; new contract. |
| AB-08 | P1 | Session-start context hook: routing block, installed grimoires, drift nudge | new `hooks/hooks.json`, `rites/summon_state.py`, `rites/inject_agent_file.py` | Depends on AB-07 for Claude; Codex keeps file injection. |
| AB-09 | P1 | Resolved on `release/1.8` (2026-11-11): `/grm-setup` conversational onboarding replaces the installer menu | new `invocations/grm/setup.md`, `rites/summon_core.py` (clone, discover, library) | Public command addition; replaces GUI flows. |
| AB-10 | P1 | Resolved on `release/1.8` (2026-11-11): `/grm-save` commits, pulls, and pushes the active grimoire for non-engineers | new `invocations/grm/save.md`, new rite `rites/save_grimoire.py` | Needs D5; first write-capable rite that touches git. |
| AB-11 | P1 | Generic publishing: stage and audit as rites, generator templates, CI templates for GitLab Pages, GitHub Pages, Cloudflare | new `rites/stage_publish.py`, `rites/audit_publish.py`, new `formulae/publish/`, new `invocations/grm/publish.md` | New contract; japan-grimoire migration proves it. |
| AB-12 | P2 | One Python launcher for every platform | new `bin/arcana` (sh) and `bin/arcana.cmd`, every `SKILL.md` and invocation that says `python3` | Touches every skill; sequence after AB-07 so plugin `bin/` can carry it. |
| AB-13 | P2 | Resolved on `release/1.8` (2026-11-10): scaffold `.gitignore` as a seeded file | `formulae/grimoire/scaffold_contract.json`, new `formulae/grimoire/gitignore` | Scaffold contract change with heal. |
| AB-15 | P2 | Layperson documentation and product naming | `README.md`, `docs/installation.md`, new `docs/getting_started.md`, `formulae/grimoire/README.md` | Write after AB-05, AB-07, AB-09 settle the real flow. |
| AB-16 | P3 | Grimoire skills auto-load by path | grimoire `skills/**/SKILL.md` via `paths:` frontmatter | Claude-only convenience; after AB-07. |

### Item details

#### AB-17 Skills fail to load outside the grimoires directory (P0)

Why: every Arcana skill inlines its invocation at runtime with
`` !`cat <ARCANA_PATH>/invocations/...` ``. Claude Code only lets that
directive read files inside the session's allowed working directories. Spike
evidence from 2026-11-10 on Claude Code 2.1.322, headless sessions on this
machine:

- Working directory `~/grimoires` (Arcana inside it): `/grm-help` loads.
- Working directory `~/grimoires/japan-grimoire`: the skill fails to load and
  the model improvises a catalog from whatever it can see. A forward-slash
  probe gives the explicit reason: `cat ... was blocked. For security, Claude
  Code may only concatenate files from the allowed working directories`.
- Same directory with `--add-dir ~/grimoires/arcana`: loads.
- A plugin skill reading from its own plugin root is blocked the same way,
  because the plugin cache is outside the working directories too.

Every engineer who opens a project repository rather than the grimoires
folder has therefore been running `/grm-*` commands without their playbooks.
This is the likeliest mechanical cause of the "ups and downs" the 1.8 brief
describes, and it would carry straight into plugin packaging.

Resolved on `release/1.8`, 2026-11-10: `sync_skills.py` inlines the directive
target at registration (nested includes and `ARCANA_HOME/` resolved, duplicate
includes collapsed, missing files warned and left visible), with tests that
render the whole shipped catalog and assert no directive survives and no skill
exceeds 500 lines. Verified headless from a grimoire working directory. The
plugin build (AB-07) reuses the same renderer. Remaining from this item:
`metadata:` provenance and `compatibility:` fields on generated skills, folded
into AB-07.

Original fix description: stop runtime inlining. `sync_skills.py` (and the plugin build) render
the invocation text into the generated `SKILL.md` body at registration, so a
registered skill is self-contained: no shell runs when it loads, no working
directory matters, and an admin `disableSkillShellExecution` setting changes
nothing. Source skills keep a single `{{INVOCATION: invocations/grm/add.md}}`
marker that the rite expands; the invocation files stay the single source.
Generated skills stay under the 500-line guidance of the Agent Skills
standard (the longest invocation today is well under that). Rite commands
inside the rendered text use the absolute engine path as now. Also move the
provenance comment into `metadata:` and add `compatibility:` where a skill
needs git or Python, so the generated files conform to the standard.

Validation profile: `tests/test_sync_skills.py` renders a fixture skill and
asserts no `!` directive survives; `validate_skill_refs` learns the marker.
Compatibility: MINOR (generated artifacts change; sources and grimoires do
not).

#### AB-01 Case-exact wikilinks and case-collision portability checks (P0)

Why: a grimoire that validates on the author's Windows or macOS machine can
fail on a Linux CI runner, in GitLab Pages, and in Obsidian on Linux. The
validators are supposed to be the cross-platform guarantee and today they are
not.

First slice:

- `_lib.resolve_wikilink_path` returns the resolved path; add
  `wikilink_case_matches(body, resolved, root)` that compares the link text
  with the on-disk spelling segment by segment (`os.listdir` per segment, or
  `Path.resolve()` on Windows which returns true casing) and have
  `validate_links` emit `LINK_CASE_MISMATCH` as an error with the exact on-disk
  path as the hint.
- `validate_portability` gains `PORTABILITY_CASE_COLLISION` for two entries in
  one directory that are equal under `casefold()`.
- `repair_links.py` and `restructure_grimoire.py` preserve on-disk casing when
  they rewrite links (they already do; add tests).
- Tests: fixture with a wrong-case link, fixture with `Foo.md` and `foo.md`.

Validation profile: `arc-validate` full, pytest fast gate on Ubuntu and Windows
(AB-02). Compatibility: existing valid grimoires stay valid unless they already
carry a latent cross-platform break, which is the point. PATCH or MINOR.

#### AB-02 Windows in the CI matrix (P0)

Add `windows-latest` to `ci.yml` for the fast gate. The 1.8 cycle already found
two Windows-only failures that Ubuntu CI could not see. Keep the eval tier on
Ubuntu only.

#### AB-03 Casing freedom (P1)

Why: people adopting Grimoire for existing material (HR policy folders, program
documentation, exported wikis) must not be forced to rename everything.
Different teams have legitimate casing conventions.

Policy to write once, in `docs/operating_model.md`, and reference everywhere
else:

- Any casing is valid in page and folder names. Consistency within one
  grimoire is the goal; snake_case is the default because it is greppable as
  whole tokens and matches every existing grimoire.
- Each grimoire records its convention in `grimoire.json` as an optional
  `naming` field (`snake_case` default, or `preserve` for material that keeps
  its own casing, or another named style). `/grm-create` asks for it with
  snake_case preselected. When the field is absent and the question first
  matters (an import or add whose material arrives in another casing), the
  invocation asks once, records the answer, and moves on.
- Invocations apply the recorded convention to new pages and folders they
  create, recommend it for imported material, and never rename imported files
  or folders without asking. A user may state a case-by-case exception (keep
  `ICD_Documents/` as is) and the invocation respects it without arguing.
- `/grm-audit-semantics` reports deviations from the recorded convention as
  advisory findings, never as errors, and reads the dominant pattern when no
  convention is recorded.
- Links must match on-disk spelling exactly (AB-01).
- A hub is `F/<basename(F)>.md` with the folder's exact spelling. The
  structure validator already compares exact strings; keep it.
- Asset-folder and source-folder recognition (`sources/`, `templates/`,
  `assets/`, and the rest) becomes case-insensitive in `_lib` and the
  structure validator, so `Sources/` and `Templates/` are recognised.
- Tags derived from folder names (`chapter/<folder>`) keep the folder's
  spelling verbatim.
- Skill directory names and `skill_prefix` stay lowercase kebab and
  `^[a-z][a-z0-9]*$`; those are command identifiers, not content.

Surfaces to change: `invocations/grm/add.md` (three mentions),
`create_grimoire.md`, `import.md`, `audit_semantics.md` (stop flagging mixed
case as a defect; flag inconsistency within a grimoire instead),
`docs/operating_model.md`, `CONTRIBUTING.md` (Arcana's own tree stays
snake_case through `validate_naming`), `rites/templates/grimoire_block.md`,
`formulae/grimoire/README.md`.

Validation profile: `arc-validate` full plus `grm-validate` on a fixture that
uses PascalCase chapters. Compatibility: MINOR, no migration.

#### AB-04 Retire `log.md` (P1)

Why: the file is write-only. It costs one rite call per operation, produces
merge conflicts in shared grimoires, and duplicates `git log`. The one argument
for it, squashed or imported history, is better served by a rite that renders
git history on demand and by the frontmatter `last_verified` dates that pages
already carry.

First slice:

- Scaffold contract: `log.md` becomes optional (not required, not managed).
  `validate_grimoire_structure` stops requiring it; `validate_orphans`,
  `validate_provenance`, `validate_frontmatter` keep their exemptions so an
  existing file stays harmless.
- New read-only rite `rites/recent_changes.py --grimoire <root> [--since 30d]`
  that renders `git log --name-status` for `chapters/` as a compact table, with
  a `--format json` envelope. `/grm-health-check` uses it for its activity and
  staleness phases.
- Remove the "Append to log.md" step from `add`, `import`, `move`, `remove`,
  `repair_links`, `health_check`, and `meta/base_invocation.md`.
  `append_log.py` stays for one minor, marked deprecated in
  `rites/data/rite_profiles.json`, then is removed.
- `formulae/log_entry.formula.md` and the `log-entry` page type are removed
  with it (the page type is documented as tooling-only and nothing emits it).
- Grimoires that are not git repositories: `recent_changes.py` reports
  "no history" and health check says so. That is the honest state.

Validation profile: full Arcana suite, command-surface coherence audit, update
on the fixture grimoire. Compatibility: MINOR (existing grimoires stay valid;
nothing is deleted from them).

#### AB-05 Remove the GUI and the release binaries (P1)

Why: the GUI is the largest single source of installer code and support
burden, requires Dear PyGui, OpenGL probing, Wayland handling, PyInstaller
builds on four platforms, and a release workflow, and it exists only to present
a menu the agent can present better in conversation.

First slice:

- Delete `rites/summon_gui.py`, `rites/build_summon_binary.py`,
  `.github/workflows/summon-release.yml`, the `[gui]` and `[build]` extras in
  `pyproject.toml`, and every GUI and release-binary mode from
  `rites/data/summon_contract.json` and `docs/summoning_contract.md`.
- `summon.sh` becomes a thin bootstrap: find Python, clone or pull Arcana to
  `~/grimoires/arcana`, run `summon.py --cli` which performs the required
  pipeline without prompts when `--scope`/`--non-interactive` are given, then
  prints the one instruction that matters: open the agent and run
  the proposed `grm-setup` skill. Grimoire discovery and cloning move behind the proposed `grm-setup` skill
  (AB-09) where the agent can ask questions in plain language.
- `docs/installation.md` loses the GUI and binary sections; the release guide
  loses the asset list.

Validation profile: full suite, `summon.py --check` on a fresh home directory
fixture (`tests/test_summon_*`). Compatibility: MINOR for grimoires (nothing in
a grimoire references the GUI); public install behavior change, so it is a
sign-off item (D4).

#### AB-06 Codex skill target `~/.agents/skills` (P1)

Why: Codex's documented personal skill root is now `~/.agents/skills`;
`~/.codex/skills` is loaded only for backward compatibility. `.agents/skills`
is also the emerging cross-agent convention, so registering there once may
serve more than one agent.

First slice: change the `codex` target's `skill_target` in
`rites/data/agent_targets.json`; have `sync_skills --reset-managed` remove
managed-prefix directories from the deprecated `~/.codex/skills` as well so a
user never has two copies; update `docs/agent_targets.md`,
`docs/agent_configuration.md`, and `docs/installation.md`. Also add the Codex
`agents/openai.yaml` `policy.allow_implicit_invocation: false` for the two
audits and `/arc-clean`, mirroring `disable-model-invocation`.

Validation profile: `tests/test_sync_skills.py`, `summon.py --check`.
Compatibility: MINOR.

#### AB-07 Arcana as a plugin; `~/grimoires` as a local marketplace (P1)

Why: this is the item that turns "clone the engine, inject a block, register
skills, remind people to update" into "install once, updates arrive". Both
agents now have plugin systems that handle fetch, versioning, auto-update, and
enterprise rollout, and Codex reads the Claude Code marketplace file, so one
repository serves both.

Shape:

- Arcana's repository gains `.claude-plugin/marketplace.json` listing two
  plugins sourced from inside the same repository: `grm` (universal grimoire
  skills) and `arc` (maintainer skills). Each plugin's `plugin.json` omits
  `version` so users track commits, or carries `VERSION` so releases are
  explicit (recommend the latter; `/grm-update` already pulls).
- Skill sources keep `{{SKILL_PREFIX}}` and `{{ARCANA_PATH}}` as the
  rendering seam; the plugin build renders them with `${CLAUDE_PLUGIN_ROOT}`
  and the flat registration renders them with absolute paths, from one source.
  `sync_skills.py` stays permanently for Codex (whose IDE extension has no
  plugin support), Cursor, and Copilot (D1). Both renderings must be generated
  by the same rite so they cannot drift.
- Engine location: `~/grimoires/arcana` remains the single engine checkout for
  every agent. The Claude plugin is a thin carrier (skills, hook, launcher)
  whose session-start hook clones the engine if absent and fast-forwards it
  when clean, pinned to the plugin's version tag. The engine never lives in an
  agent's plugin cache, so Claude and Codex always run the same rites.
- Grimoire skills are not packaged as plugins. Spike result 2026-11-10: a
  directory marketplace over `~/grimoires` with japan-grimoire as a
  relative-path plugin copied the entire grimoire (24 MB, 435 files, every
  chapter) into the plugin cache under a directory named by its commit SHA,
  so every commit would re-copy the content and each grimoire would exist
  twice. Grimoire skills stay on flat registration; the Arcana plugin's
  session-start hook runs `sync_skills.py` for the library so they are never
  stale, and the same path serves Codex.
- `ARCANA_HOME` resolution order becomes: `CLAUDE_PLUGIN_ROOT` of the `grm`
  plugin, then the library, then `~/grimoires/arcana`.
- Rollout at a company: an administrator sets `extraKnownMarketplaces` and
  `enabledPlugins` in managed settings once; every Claude Code user then has
  Grimoire with auto-update and zero manual steps. Codex users add the
  marketplace with one command. Both need only existing git credentials to the
  GitLab host, which Git Credential Manager prompts for in a browser on first
  use, so no token export.

Spike results 2026-11-10 (Claude Code 2.1.322, bundled extension binary,
throwaway config directory): a private git-URL marketplace clones with the
stored git credential and no token export; install lands in a versioned
cache; `SessionStart` command hook output reaches the model as context,
including a generated list of installed grimoires with descriptions and the
plugin root; `!cat` inside a plugin skill is blocked (see AB-17), so plugin
skills must be rendered self-contained. Remaining open questions: whether `!cat` dynamic context expands
inside the Claude Code VS Code extension (plugins, hooks, and settings are
documented as shared with the CLI; the extension bundles its own `claude`
binary, so no separate CLI install is needed), which built-in commands the
extension hides ("subset" per the docs), how `disableSkillShellExecution`
affects `!cat` (AB-14 covers the fallback), and whether the Codex CLI plugin
path is worth supporting at all given the IDE extension gap (recommendation:
no; Codex uses skills only).

Validation profile: `claude plugin validate .` and `codex plugin` checks in CI,
`summon.py --check` recognising plugin-mode installs, full suite. Compatibility:
MINOR for grimoires (the new managed file is auto-healed); public command
namespace change is the D1 sign-off.

#### AB-08 Session-start context hook (P1)

Why: the routing block is pasted into `CLAUDE.md` and goes stale (it was stale
on the maintainer's own machine on 2026-11-10). A `SessionStart` command hook
in the `grm` plugin prints the canonical block, so it is always the installed
version's text, and can add what a static block cannot: the list of installed
grimoires with one-line descriptions, and a one-line drift or behind-upstream
nudge from `summon.py --check` so the agent offers `/grm-update` at the right
moment instead of the maintainer reminding people.

First slice: `hooks/hooks.json` with one `SessionStart` command that runs
`python rites/session_context.py` (read-only; must finish fast, so the git
`fetch` for the behind-upstream check is time-boxed and skipped offline).
Claude Code stops needing `inject_agent_file.py`; Codex keeps it until Codex
plugin hooks are available outside the desktop app. The block shrinks to
routing essentials; the schema details move to a `grm:schema` skill the agent
loads on demand.

Validation profile: hook output under the 10,000-character cap, `summon.py --check`
parity. Compatibility: MINOR.

#### AB-09 the proposed `grm-setup` skill onboarding (P1)

Why: the installer's menu (install only, clone existing, create new) is the
single place a layperson meets the system, and today it is a GUI or a numbered
CLI prompt. The agent should hold that conversation.

First slice: `invocations/grm/setup.md` that inspects state through
`summon.py --check --format json` and then asks, one question at a time: do you
have a grimoire to join (paste the repository URL from your team), or are you
starting one (`/grm-create`), or do you have a folder of notes (`/grm-adopt`).
For "join": `rites/summon_core.py` `install_grimoire` and
`update_local_library` are reused as a rite entry point
(`rites/install_grimoire.py <url>`) that clones to `~/grimoires/<name>`,
registers the library, and syncs. Discovery by group URL stays as an option
for engineers. Credentials: never ask for a token; let git's credential helper
prompt, and explain what to expect on the user's platform.

Validation profile: `tests/test_summon_core.py` reuse, eval spec for the
conversation. Compatibility: MINOR; public command addition.

#### AB-10 the proposed `grm-save` skill (P1)

Why: nothing in the command surface commits or pushes grimoire content. For
engineers that is fine; for everyone else it means their edits never leave
their machine and teammates never see them. "Update the grimoire" in plain
language means both pull and share.

First slice: `rites/save_grimoire.py --grimoire <root> [--message] [--apply]`
with `plan_apply` profile: refuse if validators fail, stage everything under
the grimoire except ignored paths, commit with a generated message from the
diff summary, `pull --rebase` and stop with a plain explanation on conflict,
push. The invocation handles the conversation (what changed, confirm, what a
conflict means). `/grm-update` keeps the pull side.

Validation profile: new tests on a temporary bare remote, `rite_profiles` entry
with write detection. Compatibility: MINOR; command addition (D5).

#### AB-11 Generic publishing (P1)

Why: the proven pipeline is japan-specific and Cloudflare-specific, and
vendors Quartz. A company with a self-hosted GitLab wants GitLab Pages behind
project membership, built by CI on every push, with no vendored generator.

First slice:

- Port `stage-grimoire-for-quartz.sh` and `audit-grimoire-publish.sh` to pure
  stdlib rites: `rites/stage_publish.py` (flatten `chapters/`, rewrite full-path
  wikilinks and `sources:` paths, carry chapter-local sources, respect casing)
  and `rites/audit_publish.py` (secret audit with BLOCKER/WARNING, allowlist
  file). Both deterministic, both cross-platform, both with JSON envelopes.
- `formulae/publish/quartz/` with `quartz.config.ts` and layout templates that
  read the staged content directory, and `formulae/publish/ci/` with
  `gitlab-pages.yml`, `github-pages.yml`, and `cloudflare-pages.md` that run
  stage, audit, `npx quartz build` with a pinned version, and publish `public/`.
  No vendored Quartz: the generator is installed in CI or in a gitignored
  `publish/quartz/` directory.
- `invocations/grm/publish.md`: `grm-publish init <target>` scaffolds
  `publish/` from the formulae; `grm-publish build` runs stage, audit, build
  locally; `grm-publish check` audits only.
- Migrate `japan-grimoire/publish/` to the generic shape as the proof, keeping
  its Cloudflare deployment working.

Validation profile: rite tests on the fixture grimoire, a CI job that stages
and audits the fixture. Compatibility: MINOR; `publish/` stays excluded from
validation.

#### AB-12 One Python launcher (P2)

Why: docs and skills say `python3`; Windows ships `python`; the maintainer's
own machine needed a shim. Every skill repeating "on Windows use python" is a
smell.

First slice: `bin/arcana` (POSIX sh) and `bin/arcana.cmd` that locate a Python
3.10+ interpreter (`python3`, `python`, `py -3`) and run
`rites/<name>.py` with the remaining arguments; skills and invocations say
`arcana validate --summary`. With AB-07 the plugin's `bin/` is on the agent's
PATH automatically.

#### AB-13 Scaffold `.gitignore` (P2)

Add a managed `.gitignore` to the scaffold (Obsidian per-user state, OS files,
`publish/` build output) so new grimoires do not track `workspace.json` the way
japan-grimoire did until 2026-11-10. Heal copies it in when absent and leaves a
customised one alone (managed-if-absent, a new flag in the scaffold contract).

#### AB-15 Layperson documentation and product naming (P2)

Why: every public document speaks to engineers and explains Arcana first.
A reader who is not an engineer should meet "Grimoire" as the product, see one
install sentence per agent, and learn five verbs: setup, ask, add, save,
update. Arcana is mentioned once as "the engine, you never touch it".

First slice: `docs/getting_started.md` written for the non-engineer personas
named in the brief; `README.md` restructured with that page first and the
engineering material after; `formulae/grimoire/README.md` installation section
reduced to the plugin add command and the proposed `grm-setup` skill. Write it after AB-05,
AB-07, and AB-09 so it documents the real flow.

#### AB-16 Grimoire skills auto-load by path (P3)

Grimoire skills can declare `paths:` so Claude loads them when the user works
under the grimoire directory. Convenience only; Claude-specific.

## Suggested Implementation Sequence

Slice 1, foundations (MINOR, no decisions blocked except D2 and D3):
AB-17, AB-02, AB-01, AB-03, AB-13, AB-06, AB-04.

Slice 2, install and update (needs D1, D4, D5): AB-05, AB-09, AB-10, AB-07,
AB-08, AB-12.

Slice 3, publishing: AB-11, including the japan-grimoire migration.

Slice 4, polish and docs: AB-15, AB-16.

Whether all four slices ship as 1.8.0 or slices 3 and 4 become 1.9.0 is a
maintainer call; nothing in slice 3 or 4 blocks slice 1 or 2.

## Update Triggers

Update this backlog when:

- `/arc-improve` defers an item with P1 or P2 impact.
- A deferred item is implemented, rejected, or split.
- A new release changes one of the primary owner surfaces.
- A future architecture review finds the same drift risk again.

Do not update this file for small local cleanup that can be applied inside the
current pass. Those belong in the change itself and, if user-visible, in
`CHANGELOG.md`.
