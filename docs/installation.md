---
type: reference
title: "Installation"
aliases: ["install", "summon", "setup"]
tags: [type/reference, arcana/docs]
authority: grimoire
last_verified: 2026-05-25
---

# Arcana Installation

One command installs Arcana - the framework that powers all your grimoires -
configures your AI agents, and registers the `/arc-*` and `/grm-*` skill sets.
Cloning existing grimoires is optional and handled interactively.

For the supported agent target matrix, see
[agent targets](agent_targets.md). For per-agent configuration after
install, see [agent configuration](agent_configuration.md). For library and
manifest schemas, see [reference](reference.md). For the installer mode
contract, see [summoning contract](summoning_contract.md).

---

## Summoning Rite

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash
```

For forks or private mirrors, pass the Arcana repository URL explicitly:

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | ARCANA_URL=https://github.com/your-org/arcana.git bash
```

The script installs from the public Arcana GitHub repository by default. When run from a cloned Arcana checkout, it detects the checkout's git origin automatically.

When run from the public curl command, the summoning rite is release-first on
every platform (Linux, macOS, Windows): it downloads the matching
`grimoire-summon-*` asset from the latest GitHub Release, verifies its `.sha256`
checksum, and runs the binary, falling back to the Python source bootstrap if any
release step fails. The full release/source selection rules and the
`GRIMOIRE_SUMMON_*` controls are canonical in
[summoning contract](summoning_contract.md#release-and-source-selection).

**What the summoning rite always does:**
1. Checks runtime dependencies (`git`; Python 3 and Dear PyGui only if source fallback is needed)
2. Installs Arcana to `~/grimoires/arcana/` (clone or pull)
3. Injects the Grimoire routing block into automatic agent instruction targets from [agent targets](agent_targets.md)
4. Registers Arcana's `/arc-*` skills to agent skill targets from [agent targets](agent_targets.md)

**Optional - if you have existing grimoires to clone:**
5. Discovers grimoires via git host API (GitLab/GitHub)
6. Presents an interactive menu - pick which grimoires to clone
7. Clones or updates selected grimoires in `~/grimoires/`
8. Creates/updates the local library at `~/grimoires/library.json`

After summoning, open a new Claude Code or Codex/ChatGPT session and try `/arc-help`. To create your first grimoire from scratch, run `/grm-create`.

Dear PyGui is bundled into release binaries. In source mode, Dear PyGui is imported from the system Python or from a Grimoire-managed Python dependency cache, not from the Arcana repository. If pip or Dear PyGui is missing, the bootstrap asks before installing anything; only an explicit `y` proceeds. On Arch-based systems, accepting the pip prompt may install `python-pip` with `pacman` first if the system Python does not include pip.

GUI startup is probed before the source launcher opens a full Dear PyGui window. If OpenGL/GLX is unavailable or GUI dependencies are missing and not installed, the rite falls back to the CLI. When the one-line installer is run through `curl | bash`, prompts read from the controlling terminal instead of the curl pipe.

---

## Cloning Existing Grimoires

When you choose "Install Arcana and clone grimoires" in the GUI (or option 2 in the CLI), the rite can discover and clone grimoires by querying the git host API. Arcana does not ship a grimoire catalog; grimoires are discovered dynamically from the scope you provide.

Arcana and grimoires don't need to live in the same place. Arcana might be installed from the public GitHub repo while your grimoires live in a private company GitLab or a different GitHub org. The rite asks where to look.

If you don't have existing grimoires to clone yet, skip this step entirely and use `/grm-create` to build your first grimoire from scratch after Arcana is installed.

Discovery supports two URL shapes:
- Direct repository URLs, such as `https://github.com/you/cooking-grimoire`, are trusted explicitly. The `-grimoire` slug is conventional but not required when the URL points to a single repository.
- Skill prefix URLs, such as `https://github.com/you` or `https://gitlab.company.com/team`, scan available repositories/projects and select likely grimoires by `-grimoire` naming, `grimoire` topic/tag, or description metadata.

**Providing a scope** - tell the script where your grimoires live:

```bash
# Via --scope flag
./rites/summon.sh --scope https://github.com/my-org

# Via environment variable
export GRIMOIRE_SCOPE="https://gitlab.company.com/my-team"
./rites/summon.sh

# Via the one-liner
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash -s -- --scope https://github.com/my-org
```

To pin a specific release asset instead of using GitHub's latest published release:

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | GRIMOIRE_SUMMON_RELEASE_TAG=v1.0.0 bash
```

Release asset downloads print progress and explicit retry attempts. If a
network stalls, the bootstrap retries and then fails over to source mode after
the configured attempt/stall window. The download and mode controls
(`GRIMOIRE_SUMMON_*`) and the durable mode rules are canonical in
[summoning contract](summoning_contract.md#bootstrap-environment-controls).

If no scope is provided, the rite prompts interactively:

```
  Where are your grimoires hosted?
  Enter the URL of the group or org containing your grimoires.
  Press Enter to skip grimoire cloning and install Arcana only.

  Examples:
    https://github.com/my-org
    https://gitlab.company.com/my-team
    https://gitlab.com/company/grimoires

  Grimoire location: _
```

**Supported hosts**:
- **GitLab** (self-hosted or gitlab.com): uses the Projects API to search within a group or instance-wide
- **GitHub** (github.com or GitHub Enterprise): uses the Repos API to search within an org

**Authentication** - required for private instances:

| Host | Environment Variable | Header |
|---|---|---|
| GitLab | `GITLAB_TOKEN` | `PRIVATE-TOKEN` |
| GitHub | `GITHUB_TOKEN` | `Authorization: Bearer` |

Example with a GitLab token:
```bash
read -rs -p "GitLab token: " GITLAB_TOKEN
export GITLAB_TOKEN
./rites/summon.sh --scope https://gitlab.company.com/my-team
```

If the user skips the prompt, the rite installs Arcana only. If discovery fails, it reports the failure and continues without cloning grimoires. Existing local grimoires remain tracked only in `~/grimoires/library.json`.

### When a grimoire is discovered first

Most users find Arcana first, then use the summoning rite's interactive discovery to clone grimoires. Some users arrive from a *grimoire repo* instead, such as a private GitLab repository or a public GitHub repository, before they know Arcana exists.

The summoning rite is still the recommended entry point: one command pulls Arcana, registers it, and clones the grimoire into the right place. Manual installation is fine too, as long as the path layout stays stable: Arcana at `~/grimoires/arcana/` and each grimoire at `~/grimoires/<grimoire-directory>/`. The other rites resolve each other through those locations.

Every grimoire scaffolded from `formulae/grimoire/README.md` therefore carries its own `## Installation` section that:

1. Frames the grimoire as part of the Arcana-powered ecosystem (content + engine), not standalone software
2. Recommends a single command — the summoning rite with the grimoire's own URL as `--scope`:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash -s -- --scope <grimoire-url>
   ```

   This works whether or not Arcana is already installed: the rite pulls / installs Arcana, then runs discovery against the supplied URL, clones the grimoire into `~/grimoires/<grimoire-directory>`, and registers everything end-to-end.

3. Documents a manual install path for readers who prefer step-by-step (`git clone` Arcana + the grimoire into `~/grimoires/`, then `sync_library.py --apply` + `sync_skills.py`), with the path layout called out as the one thing the other rites depend on.

The `{{GRIMOIRE_REPO_URL}}` placeholder in the formula is the hook that `/grm-create` fills in during Step 1 (Discovery), so every new grimoire ships with this section pre-filled with its own canonical clone URL.

---

## Manual Setup

If you can't run the summoning rite (no network, restricted environment, etc.):

1. Clone Arcana to `~/grimoires/arcana/`.
2. Clone each grimoire to `~/grimoires/<grimoire-name>/`.
3. Create `~/grimoires/library.json` with one entry per grimoire (see [reference](reference.md#local-library)).
4. Add the Grimoire instruction block to the instruction targets listed in [agent targets](agent_targets.md) — the canonical block lives at [grimoire block](../rites/templates/grimoire_block.md). To refresh automatic targets after Arcana changes, use `/arc-sync-agentfile`.
5. Run `python3 ~/grimoires/arcana/rites/sync_skills.py` to install skills into registered agent skill directories.

If an existing installation is far behind and its registered slash commands no
longer match current Arcana, pull Arcana first, then follow
[Arcana Update](../UPDATE.md). The update does not depend on any installed
skill being correct.

---

## Verify Your Install (5-minute smoke test)

A short end-to-end check that everything wired up correctly.

### 1. Confirm files and skills landed

```bash
ls ~/grimoires/                  # arcana/ + at least one *-grimoire/ if you cloned any
cat ~/grimoires/library.json     # lists each grimoire and its local_path
ls ~/.claude/skills/ | grep ^arc-     # Claude Code, current full-skill target
ls ~/.codex/skills/  | grep ^arc-     # Codex / ChatGPT CLI, current pointer target
```

If any of these are missing, jump to the [Troubleshooting](#troubleshooting) section below.

### 2. Smoke-test the agent

Open a new Claude Code (or Codex) session and run:

```
/arc-help
```

The skill should enumerate every installed `arc-*` and grimoire-prefixed skill. If you see a populated list, the agent has loaded the library and skill directory correctly.

### 3. Smoke-test a grimoire

Pick any grimoire from your library and ask the agent:

> "Read the {grimoire-name} root hub and tell me what chapters it routes to."

The agent should resolve `local_path` from `~/grimoires/library.json`, read `<grimoire>/<grimoire>.md`, and report the chapter list — exactly what's in the file, no invention. If it makes things up or can't find the file, your agent's instruction block is missing the routing rules.

### 4. (Optional) Walk a full route

For a deeper test, ask:

> "What's the canonical document for {topic} in {grimoire-name}?"

The agent should follow hubs depth-first (root hub -> chapter hub -> ... -> leaf, however deep the topic needs) and cite the exact file path it read.

---

## Troubleshooting

**Agent can't find a grimoire**
- Check that the grimoire key exists in `~/grimoires/library.json`
- Verify `local_path` resolves correctly on the filesystem
- Run `/arc-library-sync` to detect and reconcile drift

**Summoning fails to clone**
- Ensure network access to your git host (VPN if required)
- Ensure git credentials are configured for the host
- Try `git ls-remote <url>` to test access

**GUI fails on Linux**
- Run the installer with `--cli` to force terminal mode:
  `curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash -s -- --cli`
- On Wayland systems, ensure XWayland is installed and running.
- On Arch-based systems, install Mesa and XWayland if needed: `sudo pacman -S --needed mesa xorg-xwayland`

**Skills not appearing after install**
- Run `/arc-sync-skills` to re-register all skills
- Open a new agent session (Claude Code / Codex caches skill listings)

**Skill names appear as `{{SKILL_PREFIX}}-...`**
- The grimoire is missing its `grimoire.json` manifest. Add one per [reference](reference.md#grimoire-manifest), then re-register.

**Agent guesses instead of reading files**
- The Grimoire instruction block is missing from the relevant target in [agent targets](agent_targets.md), or it is stale. See [agent configuration](agent_configuration.md#agent-instruction-files), then run `/arc-sync-agentfile`.
