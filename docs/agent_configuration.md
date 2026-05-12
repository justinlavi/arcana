# Grimoire Agent Configuration

Configure AI agents to use Grimoire via a minimal CLAUDE.md entry and a local catalog file. The summoning rite handles all of this automatically.

---

## Summoning Rite (Recommended)

One command sets up everything — installs Arcana, summons grimoires, creates the local catalog, registers skills, and configures CLAUDE.md:

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash
```

For forks or private mirrors, pass the Arcana repository URL explicitly:

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | GRIMOIRE_ARCANA_URL=https://github.com/your-org/arcana.git bash
```

The script installs from the public Arcana GitHub repository by default. When run from a cloned Arcana checkout, it still detects the checkout's git origin automatically.

When run from the public curl command, the summoning rite is release-first:
1. Detects the current OS and architecture.
2. Downloads the matching `grimoire-summon-*` asset from the latest GitHub Release.
3. Verifies the `.sha256` checksum.
4. Runs the binary.
5. Falls back to the Python source bootstrap if the release asset is unavailable.

The summoning rite:
1. Checks runtime dependencies (`git`; Python 3 and Dear PyGui only if source fallback is needed)
2. Installs Arcana to `~/grimoire/arcana/` (clone or pull)
3. Discovers grimoires via git host API (GitLab/GitHub), falls back to static catalog
4. Presents an interactive menu — pick which grimoires to install
5. Clones or updates selected grimoires in `~/grimoire/`
6. Creates/updates the local catalog at `~/grimoire/catalog.json`
7. Injects the Grimoire routing block into `~/.claude/CLAUDE.md`
8. Registers Grimoire skills to `~/.claude/skills/`

After summoning, open a new Claude Code session and try `/grm-help`.

Dear PyGui is bundled into release binaries. In source fallback mode, it is installed into a Grimoire-managed Python dependency cache, not into the Arcana repository. On Arch-based systems, the source fallback may install `python-pip` with `pacman` first if the system Python does not include pip.

### Dynamic Grimoire Discovery

The summoning rite can discover grimoires by querying the git host API. This removes the need to maintain a static `catalog.json` — grimoires are found dynamically based on naming convention (`*-grimoire`).

Arcana and grimoires don't need to live in the same place. Arcana might be cloned from a public GitHub repo, while your grimoires are in a private company GitLab or a different GitHub org. The script asks where to look.

Discovery supports two URL shapes:
- Direct repository URLs, such as `https://github.com/you/japan`, are trusted explicitly and do not need a `-grimoire` slug.
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

If no scope is provided, the script prompts interactively:

```
  Where are your grimoires hosted?
  Enter the URL of the group or org containing your grimoires.
  Press Enter to skip and use the static catalog only.

  Examples:
    https://github.com/my-org
    https://gitlab.company.com/my-team
    https://gitlab.com/company/grimoires

  Grimoire location: _
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

**Fallback**: If the user skips the prompt or the API is unreachable, the script falls back to the static `catalog.json`.

---

## Grimoire Catalogs

Grimoire uses two catalog files:

### Global Catalog (Company-Wide)

`catalog.json` — committed to the Arcana repo root. Lists grimoires available for installation. Each deployment populates this with its own grimoires and URLs.

```json
{
  "grimoires": {
    "olympus-grimoire": {
      "name": "Olympus",
      "description": "Olympus domain grimoire",
      "online_path": "https://git.example.com/grimoire/olympus-grimoire.git"
    }
  }
}
```

**Adding a new grimoire**: add one entry to the `grimoires` object and commit to the Arcana repo.

**Fields**:
- `name` — display name for the summoning menu.
- `description` — short description shown during selection.
- `online_path` — git clone URL (any git-compatible host).

### Local Catalog (Per-User)

`~/grimoire/catalog.json` — lives on each user's system. Lists grimoires the user has cloned, with local filesystem paths. The summoning rite creates this automatically.

```json
{
  "grimoires": {
    "olympus-grimoire": {
      "local_path": "$HOME/grimoire/olympus-grimoire",
      "online_path": "https://git.example.com/grimoire/olympus-grimoire.git"
    }
  }
}
```

**Adding a grimoire manually**: add one entry to the `grimoires` object. No other files change.

```json
{
  "grimoires": {
    "olympus-grimoire": {
      "local_path": "$HOME/grimoire/olympus-grimoire",
      "online_path": "https://git.example.com/grimoire/olympus-grimoire.git"
    },
    "bd-grimoire": {
      "local_path": "$HOME/grimoire/bd-grimoire",
      "online_path": "https://git.example.com/grimoire/bd-grimoire.git"
    }
  }
}
```

**Fields**:
- `local_path` — absolute filesystem path to the domain grimoire root (supports `$HOME`).
- `online_path` — git clone URL; set to `null` if not applicable.

---

## CLAUDE.md Configuration

The summoning rite adds this block to `~/.claude/CLAUDE.md` automatically. If setting up manually, add it once — it never changes as new grimoires are added (that happens in the local catalog).

```markdown
## Grimoire Knowledge Base

**Catalog**: `~/grimoire/catalog.json` — read this file to resolve named grimoire keys and their paths.

**Arcana key**: `GRIMOIRE_ARCANA` — resolved from catalog or defaults to `~/grimoire/arcana/`

**Skills**: Grimoire operations are available as `/grm-*` skills (e.g., `/grm-help`, `/grm-improve`).

**Routing**:
1. Determine the active grimoire from working directory or project context; look up its `local_path` in the catalog.
2. Read `{active grimoire}/INDEX.md` first; route deterministically: `INDEX.md` > chapter `INDEX.md` > 1-2 page docs.
3. For Grimoire meta-knowledge: read `GRIMOIRE_ARCANA/INDEX.md`.
4. Do not modify Grimoire files unless a `/grm-*` skill or explicit instruction asks for it.
```

---

## Other AI Agents

### ChatGPT Custom Instructions

Paste the CLAUDE.md block above into the Custom Instructions field. Point `online_path` values at cloud-hosted grimoire URLs when available.

### GitHub Copilot

Add to `.github/copilot_instructions.md`:

```markdown
## Grimoire Knowledge Base

Catalog: `~/grimoire/catalog.json`
Arcana: `~/grimoire/arcana/`
Routing: read `{active grimoire}/INDEX.md` first, route deterministically.
Skills: `/grm-*` skills are available globally (e.g., `/grm-help`, `/grm-improve`).
```

---

## Skills System

Grimoire operations are delivered as Claude Code skills — globally available via `~/.claude/skills/`.

### How Skills Work

Skills are SKILL.md files registered to `~/.claude/skills/`. A skill is a **thin pointer** — it delegates to an invocation (markdown guide) or a rite (Python script) that contains the actual logic. Skills must never embed implementation logic directly.

This separation keeps skills portable across AI agent platforms (Claude Code, ChatGPT, Copilot). The skill file describes *what to do and where to find the instructions*; the invocation or rite contains the actual procedure.

**Two delegation patterns:**
- **Invocation-backed**: skill loads a markdown guide via `!`cat {{ARCANA_PATH}}/invocations/...`` — the AI follows the instructions
- **Rite-backed**: skill tells the AI to run a Python script via `python3 {{ARCANA_PATH}}/rites/...` — the script does the work

Skills are namespaced by source:
- Arcana skills: `grm-*` (e.g., `/grm-improve`, `/grm-help`)
- Domain grimoire skills: `{domain}-*` (e.g., `/olympus-show-chapters`)

The summoning rite registers skills automatically. To re-register after updates, use `/grm-register-skills` or run:

```bash
python3 ~/grimoire/arcana/rites/register_skills.py
```

### Available Skills

| Skill | Description |
|---|---|
| `/grm-create-grimoire` | Create a new domain grimoire |
| `/grm-create-chapter` | Create a new knowledge chapter |
| `/grm-improve` | Comprehensive grimoire improvement |
| `/grm-arcana-validate` | Validate structure compliance |
| `/grm-analyze-semantics` | Semantic naming analysis |
| `/grm-arcana-validate-boundaries` | Magical boundary validation |
| `/grm-arcana-improve` | Improve Arcana (maintainer) |
| `/grm-help` | Show skill catalog and usage guide |
| `/grm-arcana-clean` | Remove temporary rite artifacts |
| `/grm-register-skills` | Re-register all skills from Arcana and grimoires |

### Domain Grimoire Skills

Domain grimoires contribute skills via their own `skills/` directory. The registration rite auto-discovers them and applies the namespace prefix derived from the catalog key (`olympus-grimoire` → `olympus-*`).

Place skills in `<grimoire>/skills/<skill-name>/SKILL.md`. Each SKILL.md should be a thin pointer that delegates to an invocation or rite — never embed logic in the skill file itself. Use `{{ARCANA_PATH}}` and `{{GRIMOIRE_PATH}}` as path placeholders — the registration rite resolves them to absolute paths.

To register new or updated skills, run `/grm-register-skills`.

---

## Troubleshooting

**Agent can't find a grimoire**
- Check that the grimoire key exists in `~/grimoire/catalog.json`
- Verify `local_path` resolves correctly on the filesystem

**Agent doesn't find new invocations**
- Run `/grm-help` to refresh the dynamically-generated catalog

**Summoning fails to clone**
- Ensure network access to your git host (VPN if required)
- Ensure git credentials are configured for the host
- Try `git ls-remote <url>` to test access

**Skills not appearing after update**
- Run `/grm-register-skills` to re-register all skills

---
