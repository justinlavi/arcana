---
type: reference
title: "Installation"
aliases: ["install", "summon", "setup"]
tags: [type/reference, arcana/docs]
authority: grimoire
last_verified: 2026-05-13
---

# Arcana Installation

One command installs Arcana — the framework that powers all your grimoires — configures your AI agents, and registers the `/grm-*` skill set. Cloning existing grimoires is optional and handled interactively.

For per-agent configuration after install, see [agent_configuration.md](agent_configuration.md). For library and manifest schemas, see [reference.md](reference.md).

---

## Summoning Rite

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash
```

For forks or private mirrors, pass the Arcana repository URL explicitly:

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | GRIMOIRE_ARCANA_URL=https://github.com/your-org/arcana.git bash
```

The script installs from the public Arcana GitHub repository by default. When run from a cloned Arcana checkout, it detects the checkout's git origin automatically.

When run from the public curl command, the summoning rite is release-first:
1. Detects the current OS and architecture.
2. Downloads the matching `grimoire-summon-*` asset from the latest GitHub Release.
3. Verifies the `.sha256` checksum.
4. Runs the binary.
5. Falls back to the Python source bootstrap if the release asset is unavailable.

**What the summoning rite always does:**
1. Checks runtime dependencies (`git`; Python 3 and Dear PyGui only if source fallback is needed)
2. Installs Arcana to `~/grimoires/arcana/` (clone or pull)
3. Injects the Grimoire routing block into `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`
4. Registers Arcana's `/grm-*` skills to `~/.claude/skills/` and `~/.codex/skills/`

**Optional — if you have existing grimoires to clone:**
5. Discovers grimoires via git host API (GitLab/GitHub), falls back to the static library
6. Presents an interactive menu — pick which grimoires to clone
7. Clones or updates selected grimoires in `~/grimoires/`
8. Creates/updates the local library at `~/grimoires/library.json`

After summoning, open a new Claude Code or Codex/ChatGPT session and try `/grm-meta-help`. To create your first grimoire from scratch, run `/grm-domain-create-grimoire`.

Dear PyGui is bundled into release binaries. In source fallback mode, it is installed into a Grimoire-managed Python dependency cache, not into the Arcana repository. On Arch-based systems, the source fallback may install `python-pip` with `pacman` first if the system Python does not include pip.

---

## Cloning Existing Grimoires

When you choose "Install Arcana and clone grimoires" in the GUI (or option 2 in the CLI), the rite can discover and clone grimoires by querying the git host API. This removes the need to maintain a static `library.json` — grimoires are found dynamically based on naming convention (`*-grimoire`).

Arcana and grimoires don't need to live in the same place. Arcana might be installed from the public GitHub repo while your grimoires live in a private company GitLab or a different GitHub org. The rite asks where to look.

If you don't have existing grimoires to clone yet, skip this step entirely and use `/grm-domain-create-grimoire` to build your first grimoire from scratch after Arcana is installed.

Discovery supports two URL shapes:
- Direct repository URLs, such as `https://github.com/you/cooking-grimoire`, are trusted explicitly. The `-grimoire` slug is conventional but not required when the URL points to a single repository.
- Namespace URLs, such as `https://github.com/you` or `https://gitlab.company.com/team`, scan available repositories/projects and select likely grimoires by `-grimoire` naming, `grimoire` topic/tag, or description metadata.

**Providing a scope** — tell the script where your grimoires live:

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

If no scope is provided, the rite prompts interactively:

```
  Where are your grimoires hosted?
  Enter the URL of the group or org containing your grimoires.
  Press Enter to skip and use the static library only.

  Examples:
    https://github.com/my-org
    https://gitlab.company.com/my-team
    https://gitlab.com/company/grimoires

  Grimoire repository: _
```

**Supported hosts**:
- **GitLab** (self-hosted or gitlab.com): uses the Projects API to search within a group or instance-wide
- **GitHub** (github.com or GitHub Enterprise): uses the Repos API to search within an org

**Authentication** — required for private instances:

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

**Fallback**: If the user skips the prompt or the API is unreachable, the script falls back to the static `library.json`.

---

## Manual Setup

If you can't run the summoning rite (no network, restricted environment, etc.):

1. Clone Arcana to `~/grimoires/arcana/`.
2. Clone each domain grimoire to `~/grimoires/<grimoire-name>/`.
3. Create `~/grimoires/library.json` with one entry per grimoire (see [reference.md](reference.md#local-library)).
4. Add the Grimoire instruction block to `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` — the canonical block lives at [`rites/templates/grimoire_block.md`](../rites/templates/grimoire_block.md).
5. Run `python3 ~/grimoires/arcana/rites/register_skills.py` to install skills into agent skill directories.

---

## Troubleshooting

**Agent can't find a grimoire**
- Check that the grimoire key exists in `~/grimoires/library.json`
- Verify `local_path` resolves correctly on the filesystem
- Run `/grm-library-sync` to detect and reconcile drift

**Summoning fails to clone**
- Ensure network access to your git host (VPN if required)
- Ensure git credentials are configured for the host
- Try `git ls-remote <url>` to test access

**Skills not appearing after install**
- Run `/grm-skills-register` to re-register all skills
- Open a new agent session (Claude Code / Codex caches skill listings)
