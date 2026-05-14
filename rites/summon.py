#!/usr/bin/env python3
"""Arcana Summoning Rite — installs Arcana and optionally clones grimoires.

Usage:
    python3 summon.py [--arcana-url URL] [--scope URL] [--cli] [--gui]

One-liner entry point:
    curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash

Options:
    --arcana-url URL
                   URL of the Arcana git repository to install
    --scope URL    URL of the group/org containing your grimoires
    --cli          Force terminal mode (no GUI)
    --gui          Force GUI mode
    -h, --help     Show this help message

Environment variables:
    GRIMOIRE_ARCANA_URL
                     Same as --arcana-url (flag takes precedence)
    GRIMOIRE_SCOPE    Same as --scope (flag takes precedence)
    GITLAB_TOKEN      GitLab personal access token for private instances
    GITHUB_TOKEN      GitHub token for private orgs
"""

import argparse
import json
import os
import re
import signal
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GRIMOIRES_HOME = Path.home() / "grimoires"
ARCANA_DIR = GRIMOIRES_HOME / "arcana"
LOCAL_LIBRARY = GRIMOIRES_HOME / "library.json"
CLAUDE_MD = Path.home() / ".claude" / "CLAUDE.md"
CODEX_AGENTS_MD = Path.home() / ".codex" / "AGENTS.md"
RITE_DIR = Path(__file__).resolve().parent
REPO_ROOT = RITE_DIR.parent
DEFAULT_ARCANA_URL = "https://github.com/justinlavi/arcana.git"

def _load_grimoire_block():
    """Load the canonical Grimoire instruction block.

    Tries rites/templates/grimoire_block.md first (installed Arcana).
    Falls back to the inline default when running from a bootstrap temp
    directory where the templates/ subdirectory hasn't been downloaded yet.
    """
    template_path = RITE_DIR / "templates" / "grimoire_block.md"
    if template_path.is_file():
        return "\n" + template_path.read_text(encoding="utf-8")

    # Inline fallback — kept in sync with rites/templates/grimoire_block.md.
    # The summoning rite injects this into ~/.claude/CLAUDE.md and
    # ~/.codex/AGENTS.md; after Arcana is cloned the template file is
    # authoritative and this fallback is never reached in normal use.
    return """
## Grimoire Knowledge Base

**Library**: `~/grimoires/library.json` — read this file to resolve named grimoire keys and their on-disk paths.

**Arcana key**: `GRIMOIRE_ARCANA` — resolved from the library or defaults to `~/grimoires/arcana/`.

**Skills**: Arcana ships `/grm-*` skills (e.g. `/grm-meta-help`, `/grm-domain-ingest`, `/grm-domain-lint`, `/grm-domain-improve`). Each domain grimoire ships its own `/<namespace>-*` skills declared in its `grimoire.json`.

### Hub convention

For any folder F that acts as a router, the hub file is `F/<basename(F)>.md`. The grimoire root hub is `<grimoire>/<grimoire>.md`. A hub may route to sub-hubs, to leaf pages, or both — depth is open-ended. Routing follows hubs depth-first until a leaf answers the question; chains can be 2 hops (root -> leaf) or more (root -> chapter -> sub-chapter -> ... -> leaf), as deep as the topic warrants.

### Storage layers

- `sources/` — Immutable source artifacts. Read, never modify. Citation-stable.
- `inbox/` — Optional transient drop zone for mixed content awaiting classification. Cleared by `/grm-domain-ingest`. Pages must not cite `inbox/` paths.
- `chapters/` — LLM-authored knowledge pages with YAML frontmatter (`type`, `title`, `tags`, `authority`, `sources`, `last_verified`); see `GRIMOIRE_ARCANA/docs/page_schema.md`.
- `log.md` — Append-only activity log; entries prefixed `## [YYYY-MM-DD HH:MM] <op> | <title>`.

### Routing

1. Resolve the active grimoire from the working directory or project context.
2. Open `<grimoire>/<grimoire>.md` for routing.
3. Use Obsidian wikilinks (`[[page]]`) for in-grimoire pointers; cross-grimoire references use placeholders (`GRIMOIRE_ARCANA/...`).
4. For Grimoire meta-knowledge: read `GRIMOIRE_ARCANA/arcana.md`.
5. Do not modify Grimoire files unless a `/grm-*` skill, a domain skill, or explicit instruction asks for it.
"""


GRIMOIRE_BLOCK = _load_grimoire_block()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


class Logger:
    """Terminal logger with prefixed output.

    Both this terminal logger and the GUI's GUILogger expose the same
    interface — info/ok/warn/err for tagged messages, plus `line()` for raw
    subprocess output that should appear in the user-visible log without
    a redundant tag prefix.
    """

    def info(self, msg):
        print(f"  [INFO]  {msg}")

    def ok(self, msg):
        print(f"  [OK]    {msg}")

    def warn(self, msg):
        print(f"  [WARN]  {msg}")

    def err(self, msg):
        print(f"  [ERROR] {msg}")

    def line(self, text):
        """Append a raw line of output (no tag prefix). For subprocess output."""
        print(text)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _subprocess_env():
    """Return a clean env dict for spawning subprocesses from a frozen binary.

    PyInstaller sets LD_LIBRARY_PATH to its extracted temp dir so its bundled
    C extensions can find their dependencies.  When the binary spawns system
    tools like git, those tools' helpers (git-remote-https, etc.) also search
    LD_LIBRARY_PATH and pick up the bundled libssl / libcurl instead of the
    system versions, causing symbol-version mismatches on distros with newer
    OpenSSL (e.g. Arch / CachyOS).  Stripping the key fixes this without
    affecting the binary's own Python extension loading (those paths are
    already baked into the extension .so files via RPATH).
    """
    if not getattr(sys, "frozen", False):
        return None  # not frozen — let subprocess inherit env unchanged
    env = dict(os.environ)
    env.pop("LD_LIBRARY_PATH", None)
    return env


def git(*args, cwd=None, log=None):
    """Run a git command. Returns (success: bool, stdout: str).

    When `log` is provided and the command fails, git's stderr is fed line-by-line
    through `log.line()` so the user sees the actual git error (auth failure,
    network issue, repo not found, etc.) instead of just our generic message.
    """
    try:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=cwd,
            capture_output=True,
            text=True,
            env=_subprocess_env(),
        )
        if result.returncode != 0 and log is not None:
            stderr = (result.stderr or "").rstrip()
            if stderr:
                for line in stderr.splitlines():
                    log.line(line)
        return result.returncode == 0, result.stdout.strip()
    except FileNotFoundError:
        if log is not None:
            log.line("git executable not found on PATH")
        return False, ""


def detect_arcana_url():
    """Detect Arcana origin from the repo this script lives in."""
    ok, _ = git("-C", str(REPO_ROOT), "rev-parse", "--is-inside-work-tree")
    if not ok:
        return ""
    ok, url = git("-C", str(REPO_ROOT), "remote", "get-url", "origin")
    return url if ok else ""


def resolve_arcana_url(args):
    """Resolve the Arcana git URL from flag, env, local origin, or public default."""
    return (
        args.arcana_url
        or os.environ.get("GRIMOIRE_ARCANA_URL", "")
        or detect_arcana_url()
        or DEFAULT_ARCANA_URL
    )


def git_credential_token(host):
    """Query git credential helper for a stored token/password."""
    try:
        result = subprocess.run(
            ["git", "credential", "fill"],
            input=f"protocol=https\nhost={host}\n\n",
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return ""
        for line in result.stdout.splitlines():
            if line.startswith("password="):
                return line[len("password="):]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return ""


# ---------------------------------------------------------------------------
# URL parsing
# ---------------------------------------------------------------------------


def parse_scope_url(url):
    """Parse a scope URL into (host, scope).

    Examples:
        https://github.com/my-org       → ("github.com", "my-org")
        https://github.com/my-org/repo  → ("github.com", "my-org/repo")
        git@github.com:my-org/repo.git  → ("github.com", "my-org/repo")
        https://gitlab.co/team/grimoire → ("gitlab.co", "team/grimoire")
        https://server.com              → ("server.com", "")
    """
    raw = url.strip()
    ssh_match = re.match(r"^git@([^:]+):(.+)$", raw)
    if ssh_match:
        host = ssh_match.group(1)
        scope = ssh_match.group(2)
    else:
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw):
            raw = f"https://{raw}"
        parsed = urlparse(raw)
        host = parsed.netloc
        scope = parsed.path.lstrip("/")

    scope = re.sub(r"\.git$", "", scope.rstrip("/"))
    return host.lower(), scope


def _scope_parts(scope):
    """Split a repository scope path into clean path parts."""
    return [part for part in scope.split("/") if part]


def _library_key_from_repo_path(path):
    """Use the repo slug as the local library key."""
    parts = _scope_parts(path)
    return parts[-1] if parts else ""


def _is_github_host(host):
    """Best-effort detection for GitHub.com and GitHub Enterprise hosts."""
    return host == "github.com" or "github" in host


def _is_gitlab_host(host):
    """Best-effort detection for GitLab.com and self-hosted GitLab hosts."""
    return host == "gitlab.com" or "gitlab" in host


# ---------------------------------------------------------------------------
# API discovery
# ---------------------------------------------------------------------------


def _api_get(url, token_header=None, token_value=None):
    """GET a JSON API endpoint. Returns (data, error_string)."""
    from urllib.error import HTTPError

    req = Request(url)
    req.add_header("User-Agent", "grimoire-summon/1.0")
    if token_header and token_value:
        req.add_header(token_header, token_value)
    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode()), None
    except HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            pass
        detail = ""
        if body:
            try:
                msg = json.loads(body)
                detail = msg.get("message") or msg.get("error") or body
            except (json.JSONDecodeError, AttributeError):
                detail = body
        return None, f"HTTP {e.code}: {detail}" if detail else f"HTTP {e.code}"
    except URLError as e:
        return None, f"Connection failed: {e.reason}"
    except json.JSONDecodeError:
        return None, "Response was not valid JSON"
    except OSError as e:
        return None, str(e)


def _metadata_marks_grimoire(name, description="", topics=None):
    """Return True when repository metadata marks a repo as a grimoire."""
    topics = topics or []
    normalized_topics = {str(topic).lower() for topic in topics}
    name_l = (name or "").lower()
    desc_l = (description or "").lower()
    return (
        name_l.endswith("-grimoire")
        or "grimoire" in normalized_topics
        or "grimoire" in desc_l
    )


def _github_entry(repo):
    """Convert one GitHub repo API object to a library entry."""
    name = repo.get("name") or _library_key_from_repo_path(repo.get("full_name", ""))
    return {
        "name": name,
        "description": repo.get("description") or "Domain grimoire",
        "online_path": repo.get("clone_url", ""),
    }


def _gitlab_entry(project):
    """Convert one GitLab project API object to a library entry."""
    path = project.get("path") or _library_key_from_repo_path(project.get("path_with_namespace", ""))
    return {
        "name": project.get("name", path),
        "description": project.get("description") or "Domain grimoire",
        "online_path": project.get("http_url_to_repo", ""),
    }


def _gitlab_filter_grimoires(data, log):
    """Extract grimoire entries from a GitLab project list."""
    if not isinstance(data, list):
        log.warn(f"GitLab API returned unexpected response type: {type(data).__name__}")
        return {}
    entries = {}
    for project in data:
        path = project.get("path", "")
        topics = project.get("topics") or project.get("tag_list") or []
        if not _metadata_marks_grimoire(path, project.get("description", ""), topics):
            continue
        entries[path] = _gitlab_entry(project)
    return entries


def _resolve_token(host, env_var, explicit_token, log):
    """Resolve an API token: explicit > env var > git credential helper."""
    if explicit_token:
        return explicit_token
    from_env = os.environ.get(env_var, "")
    if from_env:
        log.info(f"Using token from ${env_var}")
        return from_env
    from_git = git_credential_token(host)
    if from_git:
        log.info(f"Using token from git credential store for {host}")
        return from_git
    return ""


def try_gitlab_discovery(host, scope, token, log):
    """Query GitLab API for grimoire repos. Returns dict of library entries."""
    auth_h = "PRIVATE-TOKEN" if token else None
    auth_v = token or None

    if len(_scope_parts(scope)) >= 2:
        encoded_project = quote(scope, safe="")
        project_url = f"https://{host}/api/v4/projects/{encoded_project}"
        log.info(f"Trying GitLab project API: {project_url}")
        data, err = _api_get(project_url, token_header=auth_h, token_value=auth_v)
        if isinstance(data, dict) and data.get("http_url_to_repo"):
            key = data.get("path") or _library_key_from_repo_path(scope)
            log.ok(f"Using explicit GitLab project: {key}")
            return {key: _gitlab_entry(data)}
        if err and "404" not in err:
            log.warn(f"GitLab project lookup failed: {err}")

    if not scope:
        url = f"https://{host}/api/v4/projects?search=grimoire&per_page=100"
        log.info(f"Trying GitLab API: {url}")
        data, err = _api_get(url, token_header=auth_h, token_value=auth_v)
        if err:
            log.warn(f"GitLab API failed: {err}")
            if not token:
                log.warn("No credentials found — set GITLAB_TOKEN or configure git credential helper")
            return {}
        return _gitlab_filter_grimoires(data, log)

    encoded = quote(scope, safe="")
    group_url = f"https://{host}/api/v4/groups/{encoded}/projects?search=grimoire&per_page=100"
    log.info(f"Trying GitLab groups API: {group_url}")
    data, err = _api_get(group_url, token_header=auth_h, token_value=auth_v)

    if data is not None:
        return _gitlab_filter_grimoires(data, log)

    if "404" in (err or ""):
        user = scope.split("/")[0]
        user_url = f"https://{host}/api/v4/users?username={user}"
        log.info(f"Group not found, trying as user namespace: {user}")
        user_data, _ = _api_get(user_url, token_header=auth_h, token_value=auth_v)

        if isinstance(user_data, list) and user_data:
            uid = user_data[0].get("id")
            proj_url = f"https://{host}/api/v4/users/{uid}/projects?search=grimoire&per_page=100"
            log.info(f"Trying GitLab user projects API: {proj_url}")
            data, err = _api_get(proj_url, token_header=auth_h, token_value=auth_v)
            if data is not None:
                return _gitlab_filter_grimoires(data, log)

    log.warn(f"GitLab API failed: {err}")
    if not token:
        log.warn("No credentials found — set GITLAB_TOKEN or configure git credential helper")
    return {}


def try_github_discovery(host, scope, token, log):
    """Query GitHub API for grimoire repos. Returns dict of library entries."""
    if host == "github.com":
        api_base = "https://api.github.com"
    else:
        api_base = f"https://{host}/api/v3"

    parts = _scope_parts(scope)
    auth_h = "Authorization" if token else None
    auth_v = f"Bearer {token}" if token else None

    if len(parts) >= 2:
        owner, repo_name = parts[0], parts[1]
        repo_url = f"{api_base}/repos/{owner}/{repo_name}"
        log.info(f"Trying GitHub repo API: {repo_url}")
        data, err = _api_get(repo_url, token_header=auth_h, token_value=auth_v)
        if isinstance(data, dict) and data.get("clone_url"):
            key = data.get("name") or repo_name
            log.ok(f"Using explicit GitHub repository: {key}")
            return {key: _github_entry(data)}
        log.warn(f"GitHub repo lookup failed: {err}")
        return {}

    if not parts:
        log.warn("GitHub discovery requires an owner/org or owner/repo URL")
        return {}

    owner = parts[0]
    url = f"{api_base}/orgs/{owner}/repos?per_page=100"

    log.info(f"Trying GitHub org repos API: {url}")
    data, err = _api_get(
        url,
        token_header=auth_h,
        token_value=auth_v,
    )
    if err:
        user_url = f"{api_base}/users/{owner}/repos?per_page=100"
        log.info(f"Org lookup failed, trying GitHub user repos API: {user_url}")
        data, err = _api_get(user_url, token_header=auth_h, token_value=auth_v)
        if err:
            log.warn(f"GitHub API failed: {err}")
            if not token:
                log.warn("No credentials found — set GITHUB_TOKEN or configure git credential helper")
            return {}
    if not isinstance(data, list):
        log.warn(f"GitHub API returned unexpected response type: {type(data).__name__}")
        return {}

    entries = {}
    for repo in data:
        name = repo.get("name", "")
        if not _metadata_marks_grimoire(
            name,
            repo.get("description", ""),
            repo.get("topics") or [],
        ):
            continue
        entries[name] = _github_entry(repo)
    return entries


def discover_grimoires(scope_url, log, explicit_token=""):
    """Discover grimoires from a scope URL. Returns dict of library entries."""
    host, scope = parse_scope_url(scope_url)
    if not host:
        log.warn("Could not parse host from URL")
        return {}

    if scope:
        log.info(f"Searching {host}/{scope} for grimoires...")
    else:
        log.info(f"Searching {host} for grimoires...")

    if _is_github_host(host):
        gh_token = _resolve_token(host, "GITHUB_TOKEN", explicit_token, log)
        entries = try_github_discovery(host, scope, gh_token, log)
        if entries:
            log.ok(f"Discovered {len(entries)} grimoire(s) via GitHub API")
            return entries
    elif _is_gitlab_host(host):
        gl_token = _resolve_token(host, "GITLAB_TOKEN", explicit_token, log)
        entries = try_gitlab_discovery(host, scope, gl_token, log)
        if entries:
            log.ok(f"Discovered {len(entries)} grimoire(s) via GitLab API")
            return entries
    else:
        gl_token = _resolve_token(host, "GITLAB_TOKEN", explicit_token, log)
        entries = try_gitlab_discovery(host, scope, gl_token, log)
        if entries:
            log.ok(f"Discovered {len(entries)} grimoire(s) via GitLab API")
            return entries

        gh_token = _resolve_token(host, "GITHUB_TOKEN", explicit_token, log)
        entries = try_github_discovery(host, scope, gh_token, log)
        if entries:
            log.ok(f"Discovered {len(entries)} grimoire(s) via GitHub API")
            return entries

    log.err(f"No grimoires found at {scope_url} — check the URL, network, and auth tokens")
    return {}


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------


def check_git(log):
    """Verify git is available."""
    ok, _ = git("--version")
    if not ok:
        log.err("git is required but not found on PATH")
        return False
    log.ok("git found")
    return True


def install_arcana(arcana_url, log):
    """Clone or update Arcana."""
    log.info("Installing Arcana...")

    if (ARCANA_DIR / ".git").is_dir():
        log.info("Arcana already installed — pulling latest...")
        ok, _ = git("-C", str(ARCANA_DIR), "pull", "--ff-only", log=log)
        if ok:
            log.ok(f"Arcana updated: {ARCANA_DIR}")
        else:
            log.warn("Arcana pull failed (local changes?) — skipping update")
            log.ok(f"Arcana exists: {ARCANA_DIR}")
    elif arcana_url:
        log.info(f"Cloning Arcana from {arcana_url}...")
        ok, _ = git("clone", arcana_url, str(ARCANA_DIR), log=log)
        if ok:
            log.ok(f"Arcana cloned to {ARCANA_DIR}")
        else:
            log.err("Failed to clone Arcana — check network and git credentials (see git output above)")
            return False
    else:
        if ARCANA_DIR.is_dir():
            log.ok(f"Arcana exists: {ARCANA_DIR}")
        else:
            log.err(
                "Cannot detect Arcana origin URL — ensure this script is run from a git-cloned Arcana repo"
            )
            return False
    return True


def load_static_library():
    """Load the global library.json from Arcana. Returns dict."""
    library_path = ARCANA_DIR / "library.json"
    if not library_path.is_file():
        library_path = REPO_ROOT / "library.json"
    if not library_path.is_file():
        return {"grimoires": {}}
    try:
        with open(library_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"grimoires": {}}


def install_grimoire(key, entry, log):
    """Clone or update a single grimoire. Returns True on success."""
    name = entry.get("name", key)
    url = entry.get("online_path", "")
    target = GRIMOIRES_HOME / key

    if (target / ".git").is_dir():
        log.info(f"{name} already installed — pulling latest...")
        ok, _ = git("-C", str(target), "pull", "--ff-only", log=log)
        if ok:
            log.ok(f"{name} updated: {target}")
        else:
            log.warn(f"{name} pull failed (local changes?) — skipping update")
            log.ok(f"{name} exists: {target}")
        return True
    elif target.is_dir():
        log.warn(f"{name} directory exists but is not a git repo — skipping")
        return True
    else:
        log.info(f"Cloning {name} from {url}...")
        ok, _ = git("clone", url, str(target), log=log)
        if ok:
            log.ok(f"Cloned {name} to {target}")
            return True
        else:
            log.err(f"Failed to clone {name} — check VPN and git credentials (see git output above)")
            return False


def update_local_library(installed_keys, library, log):
    """Update ~/grimoires/library.json with installed grimoires."""
    log.info("Updating local library...")

    if LOCAL_LIBRARY.is_file():
        try:
            with open(LOCAL_LIBRARY) as f:
                local = json.load(f)
        except (json.JSONDecodeError, OSError):
            local = {"grimoires": {}}
    else:
        local = {"grimoires": {}}

    for key in installed_keys:
        entry = library.get("grimoires", {}).get(key, {})
        local_entry = {
            "local_path": f"$HOME/grimoires/{key}",
            "online_path": entry.get("online_path", ""),
        }
        local["grimoires"][key] = local_entry

    with open(LOCAL_LIBRARY, "w") as f:
        json.dump(local, f, indent=2)
        f.write("\n")

    log.ok(f"Local library updated: {LOCAL_LIBRARY}")


def inject_agent_file(log, target_path, title):
    """Inject Grimoire routing block into an agent instruction file."""
    log.info(f"Configuring {target_path.name}...")

    target_dir = target_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    if not target_path.is_file():
        target_path.write_text(f"# {title}\n", encoding="utf-8")
        log.info(f"Created {target_path}")

    content = target_path.read_text(encoding="utf-8")

    if "## Grimoire Knowledge Base" in content:
        log.ok(f"Grimoire block already present in {target_path.name} (skipping)")
        return

    if content.startswith(f"# {title}"):
        first_line_end = content.index("\n") if "\n" in content else len(content)
        content = content[: first_line_end + 1] + GRIMOIRE_BLOCK + content[first_line_end + 1 :]
    else:
        content += GRIMOIRE_BLOCK

    target_path.write_text(content, encoding="utf-8")
    log.ok(f"Grimoire block injected into {target_path}")


def inject_agent_configs(log):
    """Inject Grimoire routing blocks into supported agent instruction files."""
    inject_agent_file(log, CLAUDE_MD, "CLAUDE.md")
    inject_agent_file(log, CODEX_AGENTS_MD, "AGENTS.md")


def register_skills(log):
    """Run the skill registration script.

    Always attempts to run. Surfaces both stdout and stderr so failures are
    never silent. Returns True on success, False on failure (caller may want
    to surface the failure in the final summary, but the rest of summoning
    should not be aborted by a registration failure).
    """
    log.info("Registering Grimoire skills...")

    # Prefer the installed Arcana copy. Fall back to the bootstrap copy in
    # the current rite dir during first-time install (when ARCANA_DIR is the
    # repo we're cloning into, the script lands there a moment before this
    # runs, but during a hot-bootstrap the script may only exist next to us).
    register_script = ARCANA_DIR / "rites" / "register_skills.py"
    if not register_script.is_file():
        register_script = RITE_DIR / "register_skills.py"

    if not register_script.is_file():
        log.err(
            f"register_skills.py not found at {ARCANA_DIR / 'rites'} or {RITE_DIR}"
        )
        log.err("Skills NOT registered. Re-run manually after Arcana lands:")
        log.err(f"  python3 {ARCANA_DIR / 'rites' / 'register_skills.py'}")
        return False

    result = subprocess.run(
        [sys.executable, str(register_script), "--agent", "all"],
        capture_output=True,
        text=True,
    )

    # Route subprocess output through the log object so both CLI (stdout) and
    # GUI (log window) audiences see the same lines verbatim.
    if result.stdout:
        for line in result.stdout.rstrip().splitlines():
            log.line(line)
    if result.stderr:
        for line in result.stderr.rstrip().splitlines():
            log.line(line)

    if result.returncode != 0:
        log.err(
            f"Skill registration FAILED (exit {result.returncode}). See output above."
        )
        log.err("Re-run manually with:")
        log.err(f"  python3 {register_script}")
        return False

    # Confirm by spot-checking the agent skill directories.
    claude_skills_dir = Path.home() / ".claude" / "skills"
    codex_skills_dir = Path.home() / ".codex" / "skills"
    claude_count = len(list(claude_skills_dir.glob("grm-*"))) if claude_skills_dir.is_dir() else 0
    codex_count = len(list(codex_skills_dir.glob("grm-*"))) if codex_skills_dir.is_dir() else 0
    log.ok(
        f"Skills registered: {claude_count} to {claude_skills_dir}, "
        f"{codex_count} to {codex_skills_dir}"
    )
    if claude_count == 0 and codex_count == 0:
        log.warn(
            "No /grm-* skills landed in either agent directory — "
            "this usually means neither Claude Code nor Codex is set up on this machine."
        )
        log.warn(
            "Run `mkdir -p ~/.claude/skills ~/.codex/skills && "
            f"python3 {register_script}` after installing your agent of choice."
        )
    return True


# ---------------------------------------------------------------------------
# Shared install pipeline
# ---------------------------------------------------------------------------


def finalize_install(installed_keys, library, log):
    """Run the post-Arcana install steps shared by both CLI and GUI modes.

    Updates the local library only when at least one domain grimoire landed,
    then always re-injects agent configs and re-registers /grm-* skills so
    Arcana itself is usable even when no domain grimoires were cloned.

    Returns True iff skill registration succeeded.
    """
    if installed_keys:
        update_local_library(installed_keys, library, log)
    inject_agent_configs(log)
    return register_skills(log)


# ---------------------------------------------------------------------------
# CLI mode
# ---------------------------------------------------------------------------


def _prompt_cli_mode(scope_preselected):
    """Ask whether to install Arcana only or Arcana + clone existing grimoires.

    When `scope_preselected` is True (the user passed --scope or set
    GRIMOIRE_SCOPE), we skip the prompt and assume clone mode — the explicit
    scope makes the intent unambiguous.

    Returns "arcana_only" or "clone".
    """
    if scope_preselected:
        return "clone"

    print()
    print("  What would you like to do?")
    print()
    print("    1) Install Arcana               (sets up the framework; build grimoires from scratch)")
    print("    2) Install Arcana + clone grimoires  (also pulls existing grimoires from a git host)")
    print()
    while True:
        choice = input("  Choice [1]: ").strip() or "1"
        if choice == "1":
            return "arcana_only"
        if choice == "2":
            return "clone"
        print(f"  Invalid choice: {choice!r}. Enter 1 or 2.")


def _cli_select_grimoires(library, log):
    """Show the grimoire selection menu and return the chosen keys.

    Returns an empty list when the user makes no valid selection so the caller
    can decide whether to abort or continue with Arcana only.
    """
    print()
    print("  Available Grimoires:")
    print("  --------------------")

    keys = sorted(library["grimoires"].keys())
    for i, key in enumerate(keys, 1):
        entry = library["grimoires"][key]
        name = entry.get("name", key)
        desc = entry.get("description", "")
        print(f"    {i}) {name:<20s} - {desc}")

    print()
    print("    a) Install ALL grimoires")
    print()

    selection = input("  Select grimoires to install (e.g. 1 3 or a for all): ").strip()

    if selection.lower() in ("a", "all"):
        return keys

    selected_keys = []
    for part in selection.split():
        try:
            idx = int(part) - 1
            if 0 <= idx < len(keys):
                selected_keys.append(keys[idx])
            else:
                log.warn(f"Invalid selection: {part} (skipping)")
        except ValueError:
            log.warn(f"Invalid selection: {part} (skipping)")
    return selected_keys


def _print_cli_summary(mode, installed_keys, skills_ok):
    """Print the closing summary block for either install mode."""
    print()
    print("============================================")
    if skills_ok:
        print("  Arcana Summoning Complete")
    else:
        print("  Arcana Summoning Complete (with warnings)")
    print("============================================")
    print()
    print("  Arcana:  ~/grimoires/arcana/")
    print()
    if mode == "arcana_only":
        print("  Grimoires: none cloned — Arcana only.")
        print("  To create your first grimoire, open an agent session and run: /grm-domain-create-grimoire")
    elif installed_keys:
        print("  Installed grimoires:")
        for key in installed_keys:
            print(f"    - ~/grimoires/{key}/")
    else:
        print("  Domain grimoires: none landed (clone failures — see log above).")
    print()
    print(f"  Local library: {LOCAL_LIBRARY}")
    print(f"  CLAUDE.md:     {CLAUDE_MD}")
    print(f"  AGENTS.md:     {CODEX_AGENTS_MD}")
    print("  Skills:        ~/.claude/skills/")
    print("                 ~/.codex/skills/")
    print()
    if not skills_ok:
        print("  *** Skill registration failed — see errors above. Re-run: ***")
        print(f"      python3 {ARCANA_DIR / 'rites' / 'register_skills.py'}")
        print()
    print("  Next steps:")
    print("    1. Open a new Claude Code or Codex/ChatGPT session")
    print("    2. Try: /grm-meta-help")
    print()


def run_cli(args):
    """Terminal-based interactive summoning flow."""
    log = Logger()

    print()
    print("============================================")
    print("  Arcana Summoning Rite")
    print("============================================")

    if not check_git(log):
        sys.exit(1)

    GRIMOIRES_HOME.mkdir(parents=True, exist_ok=True)
    log.ok(f"Install directory: {GRIMOIRES_HOME}")

    scope_url = args.scope or os.environ.get("GRIMOIRE_SCOPE", "")
    mode = _prompt_cli_mode(scope_preselected=bool(scope_url))

    print()
    arcana_url = resolve_arcana_url(args)
    if not install_arcana(arcana_url, log):
        sys.exit(1)

    installed_keys = []
    library = {"grimoires": {}}

    if mode == "clone":
        print()
        log.info("Discovering grimoires...")

        if not scope_url:
            print()
            print("  Where are your grimoires hosted?")
            print("  Enter the URL of the group or org containing your grimoires.")
            print("  Press Enter to skip and use the static library only.")
            print()
            print("  Examples:")
            print("    https://github.com/my-org")
            print("    https://gitlab.company.com/my-team")
            print("    https://gitlab.com/company/grimoires")
            print()
            scope_url = input("  Grimoire location: ").strip()

        library = load_static_library()
        if scope_url:
            discovered = discover_grimoires(scope_url, log)
            for key, entry in discovered.items():
                if key not in library["grimoires"]:
                    library["grimoires"][key] = entry
        else:
            log.info("Skipping discovery (no scope URL provided)")

        if not library["grimoires"]:
            log.warn(
                "No grimoires available to clone. Continuing with Arcana-only install."
            )
        else:
            log.ok(f"Library loaded ({len(library['grimoires'])} grimoire(s) available)")
            selected_keys = _cli_select_grimoires(library, log)
            if not selected_keys:
                log.warn(
                    "No grimoires selected. Continuing with Arcana-only install."
                )
            else:
                print()
                log.ok(f"Selected {len(selected_keys)} grimoire(s)")
                print()
                log.info("Installing grimoires...")
                print()
                for key in selected_keys:
                    entry = library["grimoires"][key]
                    if install_grimoire(key, entry, log):
                        installed_keys.append(key)
                if selected_keys and not installed_keys:
                    log.warn(
                        "No grimoires were cloned successfully — "
                        "continuing with Arcana-only install."
                    )

    print()
    skills_ok = finalize_install(installed_keys, library, log)
    _print_cli_summary(mode, installed_keys, skills_ok)


# ---------------------------------------------------------------------------
# GUI mode
# ---------------------------------------------------------------------------


def _ensure_dearpygui():
    """Import Dear PyGui, auto-installing via pip if missing."""
    dep_dir = Path(
        os.environ.get(
            "GRIMOIRE_SUMMON_PY_DEPS",
            Path.home() / ".cache" / "grimoire" / "summon-python",
        )
    )
    if dep_dir.is_dir() and str(dep_dir) not in sys.path:
        sys.path.insert(0, str(dep_dir))

    try:
        import dearpygui.dearpygui as dpg
        return dpg
    except ImportError:
        pass

    dep_dir.mkdir(parents=True, exist_ok=True)
    for pip_args in (
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--target",
            str(dep_dir),
            "dearpygui",
        ],
    ):
        result = subprocess.run(pip_args, capture_output=True, text=True)
        if result.returncode == 0:
            break
    else:
        raise ImportError(
            "Failed to install Dear PyGui. Install pip, or run in CLI mode with --cli."
        )

    if str(dep_dir) not in sys.path:
        sys.path.insert(0, str(dep_dir))
    import dearpygui.dearpygui as dpg
    return dpg


# ---------------------------------------------------------------------------
# GUI: DPI scaling + theme + font helpers
# ---------------------------------------------------------------------------

# Vaporwave-leaning palette, mirrors docs/obsidian.md.
GUI_COLORS = {
    "bg":            (20, 22, 38),       # window background — deep indigo
    "bg_alt":        (28, 30, 52),       # child windows
    "bg_input":      (24, 26, 46),       # input fields
    "bg_input_hov":  (34, 36, 60),
    "border":        (60, 50, 100),
    "text":          (235, 235, 245),    # body text — near-white
    "text_muted":    (155, 160, 195),    # secondary text
    "text_title":    (255, 113, 206),    # hot pink — matches hub/root
    "accent":        (1, 205, 254),      # cyan — matches hub/chapter
    "accent_hover":  (90, 220, 255),
    "btn_primary":   (185, 103, 255),    # purple — matches hub/sub
    "btn_primary_hov": (210, 140, 255),
    "btn_primary_act": (155, 80, 220),
    "btn_secondary": (60, 65, 100),
    "btn_secondary_hov": (80, 85, 130),
    "btn_secondary_act": (50, 55, 85),
    "separator":     (60, 50, 100),
    "checkmark":     (255, 113, 206),
}


def _compute_dpi_scale():
    """Best-effort DPI scale factor. 1.0 on standard 1080p, ~1.5–2.0 on 4K.

    Tries a few methods, all dependency-free, and falls back to 1.0 if every
    detection fails. Honors GRIMOIRE_GUI_SCALE env var for explicit override.
    """
    override = os.environ.get("GRIMOIRE_GUI_SCALE", "").strip()
    if override:
        try:
            v = float(override)
            return max(0.5, min(4.0, v))
        except ValueError:
            pass

    # Method 1: tkinter (ships with stdlib on most platforms)
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        # winfo_fpixels('1i') = pixels per inch on this display
        dpi = root.winfo_fpixels("1i")
        root.destroy()
        if dpi and dpi > 0:
            return max(1.0, min(3.0, dpi / 96.0))
    except Exception:
        pass

    # Method 2: rough heuristic from screen height
    try:
        if sys.platform.startswith("linux"):
            result = subprocess.run(
                ["xrandr", "--current"], capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                # Parse first "current 1920 x 1080" we find
                m = re.search(r"current\s+(\d+)\s*x\s*(\d+)", result.stdout)
                if m:
                    height = int(m.group(2))
                    if height >= 2160:
                        return 1.8
                    if height >= 1440:
                        return 1.35
    except Exception:
        pass

    return 1.0


def _find_system_font():
    """Return a path to a usable TTF/OTF font, or None to use Dear PyGui default.

    The default ProggyClean bitmap font scales poorly at high sizes; loading
    a vector font lets us draw crisp text at DPI-scaled sizes.
    """
    candidates = [
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/noto/NotoSans-Regular.ttf",
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNS.ttf",
        "/Library/Fonts/Arial.ttf",
        # Windows
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for p in candidates:
        if Path(p).is_file():
            return p
    return None


def _build_grimoire_theme(dpg):
    """Build and return the bound Grimoire theme tag."""
    c = GUI_COLORS
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, c["bg"])
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, c["bg_alt"])
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, c["bg_alt"])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, c["bg_input"])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, c["bg_input_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, c["bg_input_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_Border, c["border"])
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_Text, c["text"])
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, c["text_muted"])
            dpg.add_theme_color(dpg.mvThemeCol_Button, c["btn_primary"])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, c["btn_primary_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, c["btn_primary_act"])
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, c["checkmark"])
            dpg.add_theme_color(dpg.mvThemeCol_Separator, c["separator"])
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, c["accent"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, c["bg"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, c["btn_secondary"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, c["btn_secondary_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, c["btn_secondary_act"])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, c["bg"])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, c["bg_alt"])
            dpg.add_theme_color(dpg.mvThemeCol_Header, c["bg_input_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, c["bg_input_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, c["bg_input"])

            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 24, 20)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 8)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 12, 10)
            dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 8, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
    return theme


def _resolve_launcher_icon():
    """Find the Arcana icon shipped under resources/. Returns (small, large) paths.

    Falls back gracefully when running from a bootstrap temp dir that only
    holds summon.py — in that case we return (None, None) and the launcher
    keeps the default OS icon.

    Search order (first hit wins):
      1. PyInstaller bundle (sys._MEIPASS/resources)  — frozen binary install
      2. Installed Arcana repo (~/grimoires/arcana/resources)
      3. The repo this script lives in (REPO_ROOT/resources)
      4. RITE_DIR's parent (alt layout)
    """
    candidates_dirs = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates_dirs.append(Path(meipass) / "resources")
    candidates_dirs += [
        ARCANA_DIR / "resources",
        REPO_ROOT / "resources",
        RITE_DIR.parent / "resources",
    ]
    small_name = "arcana_icon_256.png"
    large_name = "arcana_icon_512.png"
    for d in candidates_dirs:
        small = d / small_name
        large = d / large_name
        if small.is_file() or large.is_file():
            # Use whichever exists for whichever slot, falling back to the
            # other if only one is present.
            small_path = str(small) if small.is_file() else str(large) if large.is_file() else None
            large_path = str(large) if large.is_file() else str(small) if small.is_file() else None
            return small_path, large_path
    return None, None


def _apply_launcher_icon(dpg):
    """Bind the Arcana icon to the viewport's small + large icon slots.

    Must be called AFTER `dpg.create_viewport()` and BEFORE `dpg.show_viewport()`.
    Silently no-ops if the resource files aren't accessible.
    """
    small, large = _resolve_launcher_icon()
    if small is None and large is None:
        return
    try:
        if small:
            dpg.set_viewport_small_icon(small)
        if large:
            dpg.set_viewport_large_icon(large)
    except Exception:
        # Some platforms / DPG versions don't accept PNG; never let icon
        # binding abort the launcher.
        pass


def _setup_fonts(dpg, scale):
    """Load a system font at a DPI-scaled size; bind it as the global font.

    Returns the font tag, or None if font loading failed (default font remains).
    """
    base_size = int(round(18 * scale))
    font_path = _find_system_font()
    if not font_path:
        # Fall back to Dear PyGui's built-in font; just bump the global scale.
        try:
            dpg.set_global_font_scale(max(1.0, scale * 1.3))
        except Exception:
            pass
        return None
    try:
        with dpg.font_registry():
            font = dpg.add_font(font_path, base_size)
        dpg.bind_font(font)
        return font
    except Exception:
        try:
            dpg.set_global_font_scale(max(1.0, scale * 1.3))
        except Exception:
            pass
        return None


def _probe_python():
    """Return the Python executable to use for GUI probing.

    When running inside a PyInstaller frozen binary, sys.executable is the
    binary itself.  Using it for the probe would re-invoke the binary with -c,
    re-extract the same bundled GLFW/Mesa, and fail with the same library
    conflicts as the main run — defeating the purpose of the probe.  Using
    system Python instead lets the probe talk to the system's Mesa/GLX stack
    directly, giving an accurate picture of whether the GUI can actually work.
    """
    if not getattr(sys, "frozen", False):
        return sys.executable
    for candidate in ("python3", "python"):
        try:
            r = subprocess.run(
                [candidate, "--version"],
                capture_output=True,
                timeout=3,
                env=_subprocess_env(),
            )
            if r.returncode == 0:
                return candidate
        except Exception:
            pass
    return sys.executable  # last resort: try the bundle anyway


def _extract_probe_hint(stderr_bytes):
    """Pull the most informative line from a failed probe's stderr.

    GLFW/Mesa errors (e.g. 'GLX: No GLXFBConfigs returned') appear early in
    stderr.  The last line is often a generic crash line or a Python code
    snippet from the traceback — not useful.  Prefer lines that mention
    known keywords; fall back to the first non-blank line.
    """
    text = (stderr_bytes or b"").decode("utf-8", errors="replace").strip()
    if not text:
        return ""
    keywords = ("glx", "glfw", "opengl", "egl", "error", "assert", "abort",
                 "failed", "cannot", "unable", "libgl", "mesa")
    for line in text.splitlines():
        if any(k in line.lower() for k in keywords):
            return line.strip()[:200]
    return text.splitlines()[0].strip()[:200]


def _probe_gui(extra_env=None):
    """Test whether DearPyGui can open an OpenGL window with the given env.

    Runs the minimum DearPyGui init sequence (create_context → create_viewport
    → destroy_context) inside an isolated subprocess using system Python (not
    the PyInstaller bundle).  `create_viewport()` is where GLFW creates the
    window and initialises GLX — the call that aborts (SIGABRT) on systems
    without a usable OpenGL context.  Running it in a child means the abort
    kills only the child; the launcher catches the non-zero exit and can try
    a different env or fall back to CLI.

    Returns (ok: bool, hint: str).  `hint` is empty on success; on failure it
    holds the most informative stderr line to help diagnose the root cause.
    """
    env = dict(os.environ)
    # Strip PyInstaller lib-path pollution so system Mesa / drivers are used.
    env.pop("LD_LIBRARY_PATH", None)
    if extra_env:
        env.update(extra_env)
    code = (
        "import sys, os\n"
        "d = os.environ.get('GRIMOIRE_SUMMON_PY_DEPS', '')\n"
        "if d: sys.path.insert(0, d)\n"
        "import dearpygui.dearpygui as dpg\n"
        "dpg.create_context()\n"
        "dpg.create_viewport(title='_probe', width=300, height=200)\n"
        "dpg.destroy_context()\n"
    )
    try:
        result = subprocess.run(
            [_probe_python(), "-c", code],
            capture_output=True,
            timeout=8,
            env=env,
        )
    except Exception as e:
        return False, f"could not run probe: {e}"
    if result.returncode == 0:
        return True, ""
    return False, _extract_probe_hint(result.stderr)


# Mesa software-rendering env: forces llvmpipe (CPU-side OpenGL), which
# provides its own GLX framebuffer configs and bypasses any hardware-driver
# brokenness.  Slower than hardware GL but functional on essentially any Linux
# system that has Mesa installed.  Harmless on macOS / Windows (those backends
# ignore the LIBGL_* / GALLIUM_* knobs entirely).
_GUI_SW_RENDER_ENV = {
    "LIBGL_ALWAYS_SOFTWARE": "1",
    "GALLIUM_DRIVER": "llvmpipe",
}


def _select_gui_env():
    """Pick the first env that makes the GUI work on this machine.

    Strategy: try hardware OpenGL first.  If it fails, force Mesa software
    rendering and try again.  Most systems where the hardware path fails
    (broken/missing GPU drivers, restrictive GLX configs on Arch-based distros,
    NVIDIA-on-Wayland issues, headless servers) recover with software rendering.

    Returns:
        (env_dict, label) when a working configuration is found.  `env_dict`
            holds env vars to apply to the launcher's process before running
            the GUI; empty dict means hardware GL works as-is.
        (None, reason) when no configuration works.  `reason` includes both
            probes' failure hints plus an actionable suggestion.
    """
    ok, hw_err = _probe_gui()
    if ok:
        return {}, "hardware OpenGL"

    print(f"  [INFO]  Hardware OpenGL probe failed ({hw_err}) — retrying with software rendering")
    ok, sw_err = _probe_gui(extra_env=_GUI_SW_RENDER_ENV)
    if ok:
        return dict(_GUI_SW_RENDER_ENV), "software OpenGL (Mesa llvmpipe)"

    return None, (
        f"no usable OpenGL/GLX context "
        f"(hardware: {hw_err}; software: {sw_err}). "
        f"If you're on Wayland, install XWayland — "
        f"`sudo pacman -S xorg-xwayland` on Arch, "
        f"`sudo apt install xwayland` on Debian/Ubuntu. "
        f"Otherwise ensure Mesa is installed."
    )


def run_gui(args):
    """Dear PyGui summoning flow."""
    dpg = _ensure_dearpygui()

    gui_env, label = _select_gui_env()
    if gui_env is None:
        raise RuntimeError(label)
    if gui_env:
        # Apply the env vars that made the probe succeed — the in-process
        # DearPyGui calls below read these at create_viewport() time, so it's
        # safe to set them here (after import, before context creation).
        os.environ.update(gui_env)
        print(f"  [INFO]  Using {label} for GUI rendering")

    # DPI scale is computed once and used by every dimension-bearing call.
    # Nested helpers (show_modal, populate_grimoires, etc.) close over it.
    scale = _compute_dpi_scale()

    class GUILogger:
        def __init__(self):
            self.lines = []

        def _append(self, tag, msg):
            line = f"  [{tag}]  {msg}"
            self.lines.append(line)
            if dpg.does_item_exist("log_text"):
                dpg.set_value("log_text", "\n".join(self.lines))

        def info(self, msg):
            self._append("INFO", msg)

        def ok(self, msg):
            self._append("OK", msg)

        def warn(self, msg):
            self._append("WARN", msg)

        def err(self, msg):
            self._append("ERROR", msg)

        def line(self, text):
            """Append raw output (no tag prefix). For subprocess capture."""
            self.lines.append(text)
            if dpg.does_item_exist("log_text"):
                dpg.set_value("log_text", "\n".join(self.lines))

    log = GUILogger()
    library = {"grimoires": {}}
    checkbox_tags = {}
    scope_default = args.scope or os.environ.get("GRIMOIRE_SCOPE", "")

    def show_modal(title, message, close_app=False):
        tag = "message_modal"
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

        def close_modal(*_):
            if dpg.does_item_exist(tag):
                dpg.delete_item(tag)
            if close_app:
                dpg.stop_dearpygui()

        with dpg.window(
            label=title,
            tag=tag,
            modal=True,
            no_resize=True,
            no_collapse=True,
            width=int(440 * scale),
            pos=(int(150 * scale), int(240 * scale)),
        ):
            dpg.add_text(message, wrap=int(400 * scale))
            dpg.add_spacer(height=int(10 * scale))
            dpg.add_button(label="OK", width=int(100 * scale), callback=close_modal)

    def set_busy(is_busy):
        for tag in ("discover_btn", "summon_btn"):
            if dpg.does_item_exist(tag):
                # Re-enable summon only when there's a valid selection,
                # not just because we stopped being busy.
                if tag == "summon_btn" and not is_busy:
                    update_summon_state()
                else:
                    dpg.configure_item(tag, enabled=not is_busy)

    def update_summon_state(mode=None):
        """Enable Summon based on the active mode.

        Accepts an explicit `mode` string to avoid re-reading the radio value
        during a callback (DPG may not have committed the new value yet).

        Arcana-only: always enabled.
        Clone: enabled iff at least one grimoire checkbox is checked.
        """
        if not dpg.does_item_exist("summon_btn"):
            return
        if mode is None:
            mode = dpg.get_value("mode_radio") if dpg.does_item_exist("mode_radio") else ""
        if mode == "Install Arcana":
            dpg.configure_item("summon_btn", enabled=True)
            return
        any_selected = any(
            dpg.does_item_exist(tag) and dpg.get_value(tag)
            for tag in checkbox_tags.values()
        )
        dpg.configure_item("summon_btn", enabled=any_selected)

    def on_mode_change(_sender=None, app_data=None, _user_data=None):
        """Show/hide the clone section and resize the viewport to fit the new mode.

        Strategy: immediate resize to the pre-computed estimate (eliminates the
        2-frame window where content and viewport are mismatched), then schedule
        _auto_fit_viewport to refine to the exact measured height after the layout
        has re-rendered.  The estimate is close enough that the refinement is a
        few pixels at most — not noticeable as a second flash.
        """
        mode = app_data if app_data is not None else (
            dpg.get_value("mode_radio") if dpg.does_item_exist("mode_radio") else ""
        )
        is_clone_mode = mode == "Install Arcana and clone grimoires"
        if dpg.does_item_exist("clone_section"):
            dpg.configure_item("clone_section", show=is_clone_mode)
        # Immediate resize to pre-computed estimate.
        estimated_h = _viewport_h_clone if is_clone_mode else _viewport_h_arcana
        try:
            dpg.set_viewport_height(estimated_h)
        except Exception:
            pass
        # Refine after the layout has re-rendered (widget positions update next frame).
        try:
            dpg.set_frame_callback(dpg.get_frame_count() + 2, _auto_fit_viewport)
        except Exception:
            pass
        update_summon_state(mode=mode)

    def populate_grimoires(entries):
        if dpg.does_item_exist("grimoire_list"):
            dpg.delete_item("grimoire_list", children_only=True)

        checkbox_tags.clear()
        library["grimoires"].update(entries)

        if not library["grimoires"]:
            dpg.add_text(
                "No grimoires found. Check your scope URL and authentication tokens.",
                parent="grimoire_list",
                wrap=int(620 * scale),
                color=GUI_COLORS["text_muted"],
            )
            return

        for key in sorted(library["grimoires"]):
            entry = library["grimoires"][key]
            name = entry.get("name", key)
            desc = entry.get("description", "")
            tag = f"grimoire::{key}"
            checkbox_tags[key] = tag
            label = name if not desc else f"{name} - {desc}"
            dpg.add_checkbox(
                label=label,
                default_value=True,
                tag=tag,
                parent="grimoire_list",
                callback=lambda *_: update_summon_state(),
            )

        # New checkboxes default to selected, so the button should light up.
        update_summon_state()

    def on_discover(*_):
        set_busy(True)
        try:
            scope = dpg.get_value("scope_input").strip()
            token = dpg.get_value("token_input").strip()
            static = load_static_library()
            library["grimoires"] = dict(static.get("grimoires", {}))

            if scope:
                discovered = discover_grimoires(scope, log, explicit_token=token)
                for k, v in discovered.items():
                    if k not in library["grimoires"]:
                        library["grimoires"][k] = v
            else:
                log.info("No scope URL — using static library only")

            populate_grimoires(library["grimoires"])
        finally:
            set_busy(False)

    def on_summon(*_):
        mode = (
            dpg.get_value("mode_radio")
            if dpg.does_item_exist("mode_radio")
            else "Install Arcana and clone grimoires"
        )
        arcana_only = mode == "Install Arcana"

        if arcana_only:
            selected = []
        else:
            selected = [key for key, tag in checkbox_tags.items() if dpg.get_value(tag)]
            if not selected:
                show_modal(
                    "No Selection",
                    "Please select at least one grimoire to clone, or switch to "
                    "'Install Arcana' to set up Arcana without cloning grimoires.",
                )
                return

        set_busy(True)
        try:
            if not check_git(log):
                show_modal("Error", "git is not installed.", close_app=True)
                return

            GRIMOIRES_HOME.mkdir(parents=True, exist_ok=True)

            arcana_url = resolve_arcana_url(args)
            if not install_arcana(arcana_url, log):
                show_modal("Error", "Failed to install Arcana.", close_app=True)
                return

            installed = []
            if not arcana_only:
                log.info("Installing grimoires...")
                for key in selected:
                    entry = library["grimoires"][key]
                    if install_grimoire(key, entry, log):
                        installed.append(key)

                if selected and not installed:
                    log.warn(
                        "No grimoires were cloned successfully — "
                        "continuing with Arcana-only install."
                    )

            skills_ok = finalize_install(installed, library, log)

            log.ok("Summoning complete!")
            if arcana_only:
                installed_msg = (
                    "Arcana is installed and ready.\n\n"
                    "To create your first grimoire from scratch, open a new agent "
                    "session and run /grm-domain-create-grimoire."
                )
            elif installed:
                installed_msg = (
                    f"Arcana installed with {len(installed)} grimoire(s) cloned."
                )
            else:
                installed_msg = (
                    "Arcana installed. No grimoires were cloned — check the log for clone errors."
                )
            warn_msg = (
                ""
                if skills_ok else
                "\n\nWARNING: skill registration failed. Re-run:\n"
                f"python3 {ARCANA_DIR / 'rites' / 'register_skills.py'}"
            )
            show_modal(
                "Summoning Complete" + ("" if skills_ok else " (with warnings)"),
                f"{installed_msg}{warn_msg}\n\n"
                "Next steps:\n"
                "1. Open a new Claude Code or Codex/ChatGPT session\n"
                "2. Try: /grm-meta-help",
                close_app=True,
            )
        finally:
            set_busy(False)

    dpg.create_context()
    try:
        _setup_fonts(dpg, scale)
        grimoire_theme = _build_grimoire_theme(dpg)
        dpg.bind_theme(grimoire_theme)

        c = GUI_COLORS

        # Pre-scale layout dimensions so widgets keep their visual proportions
        # regardless of DPI.
        list_h     = int(round(220 * scale))
        log_h      = int(round(150 * scale))
        btn_w      = int(round(160 * scale))
        discover_w = int(round(120 * scale))
        input_pad  = int(round(140 * scale))
        viewport_w = int(round(760 * scale))

        # Pre-computed viewport heights for each mode.
        #
        # DPG style constants set above:
        #   mvStyleVar_FramePadding  → 10, 8   (frame_pad_y = 8)
        #   mvStyleVar_ItemSpacing   → 12, 10  (item_spacing_y = 10)
        #   mvStyleVar_WindowPadding → 24, 20  (win_pad_y = 20 top + 20 bottom)
        # Font size = round(18 * scale).
        #
        # Per-widget heights (DPG measures from top of frame to top of next item):
        #   text item   → font(18) + item_spacing_y(10) = 28
        #   input/button → font(18) + 2*frame_pad_y(16) + item_spacing_y(10) = 44
        #   separator   → ~item_spacing_y * 2 = 20
        #   explicit spacer(h) → h (no extra spacing)
        #   multiline input(height=H) → H + 2*frame_pad_y(16) + item_spacing_y(10)
        #   child_window(height=H) → H + item_spacing_y(10)
        #   window padding         → win_pad_y top + win_pad_y bottom = 40
        #   OS chrome (title bar)  → ~60 on Linux, ~30 on macOS
        _t  = int(round(28 * scale))              # text item
        _i  = int(round(44 * scale))              # input / button item
        _s  = int(round(20 * scale))              # separator
        _s8 = int(round(8 * scale))               # explicit spacer(8)
        _log_inp_h = log_h + int(round(26 * scale))   # log input (150 + 2*8 + 10)
        _list_h    = list_h + int(round(10 * scale))  # child_window (220 + 10)
        _chrome    = int(round(100 * scale))       # win_pad(40) + OS title bar(~60)

        # Arcana-only visible items (top to bottom):
        #   "Grimoire" + "Summoning Rite" + separator + spacer(8)
        #   "What would you like?" + radio(2 items) + tip-text + separator + spacer(8)
        #   log-label-row + log-input + spacer(8) + summon-button
        #   + window padding + OS chrome
        _viewport_h_arcana = (
            _t + _t + _s + _s8
            + _t + 2*_t + _t + _s + _s8
            + _t + _log_inp_h + _s8 + _i
            + _chrome
        )
        # Clone section adds (between mode-selector and log section):
        #   "Grimoire Location" + (input + discover-btn) + hint-text
        #   + "Token" + token-input + spacer(8) + "Available Grimoires" + list + spacer(8)
        _viewport_h_clone = _viewport_h_arcana + (
            _t + _i + _t
            + _t + _i + _s8 + _t + _list_h + _s8
        )

        viewport_h = _viewport_h_clone if scope_default else _viewport_h_arcana

        # Default mode is Arcana-only unless a scope was preselected via flag/env,
        # in which case the user's intent to clone is implicit and we land on
        # the clone path so the discovery results have somewhere to render.
        default_mode = (
            "Install Arcana and clone grimoires"
            if scope_default
            else "Install Arcana"
        )

        with dpg.window(tag="main_window", label="Arcana", no_title_bar=True):
            dpg.add_text("Arcana", color=c["text_title"])
            dpg.add_text("Summoning Rite", color=c["text_muted"])
            dpg.add_separator()
            dpg.add_spacer(height=int(8 * scale))

            dpg.add_text("What would you like to do?")
            dpg.add_radio_button(
                items=[
                    "Install Arcana",
                    "Install Arcana and clone grimoires",
                ],
                tag="mode_radio",
                default_value=default_mode,
                callback=on_mode_change,
            )
            dpg.add_text(
                "Arcana is the framework — it's always installed. Choose the second option"
                " only if you have existing grimoires to clone from a git host.",
                color=c["text_muted"],
                wrap=int(680 * scale),
            )
            dpg.add_separator()
            dpg.add_spacer(height=int(8 * scale))

            with dpg.group(
                tag="clone_section",
                show=(default_mode == "Install Arcana and clone grimoires"),
            ):
                dpg.add_text("Grimoire Repository")
                with dpg.group(horizontal=True):
                    dpg.add_input_text(
                        tag="scope_input",
                        default_value=scope_default,
                        hint="https://github.com/my-org",
                        width=-(input_pad),
                        on_enter=True,
                        callback=on_discover,
                    )
                    dpg.add_button(tag="discover_btn", label="Discover", width=discover_w, callback=on_discover)
                dpg.add_text(
                    "e.g. https://github.com/my-org | https://gitlab.company.com/team",
                    color=c["text_muted"],
                )

                dpg.add_text("Token", color=c["text_muted"])
                dpg.add_input_text(
                    tag="token_input",
                    password=True,
                    hint="Optional - auto-detects from git credentials / env vars",
                    width=-1,
                    on_enter=True,
                    callback=on_discover,
                )

                dpg.add_spacer(height=int(8 * scale))
                dpg.add_text("Available Grimoires")
                with dpg.child_window(tag="grimoire_list", height=list_h, border=True):
                    dpg.add_text(
                        "Enter a GitHub/GitLab org or repository URL above, then press Discover.",
                        color=c["text_muted"],
                        wrap=int(620 * scale),
                    )

            with dpg.group(horizontal=True):
                dpg.add_text("Log")
                dpg.add_text(
                    "  (click in the box, Ctrl+A to select all, Ctrl+C to copy)",
                    color=c["text_muted"],
                )
            dpg.add_input_text(
                tag="log_text",
                multiline=True,
                readonly=True,
                height=log_h,
                width=-1,
                tab_input=False,
            )

            dpg.add_spacer(height=int(8 * scale))
            # In Arcana-only mode the button is immediately actionable. In
            # clone mode it gates on selection (lights up only after the user
            # checks at least one grimoire); until then the eye is drawn to
            # the active action (Discover).
            dpg.add_button(
                tag="summon_btn",
                label="Summon",
                width=btn_w,
                callback=on_summon,
                enabled=(default_mode == "Install Arcana"),
            )

        dpg.create_viewport(
            title="Arcana - Summoning Rite",
            width=viewport_w,
            height=viewport_h,
            min_width=int(560 * scale),
            min_height=_viewport_h_arcana - int(round(20 * scale)),
        )
        # Apply launcher icon (no-op if files aren't accessible).
        _apply_launcher_icon(dpg)

        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window", True)
        dpg.show_viewport()

        # One-time auto-fit after the first frame renders so font metrics and
        # OS chrome are actual rather than estimated.  Measures from the Summon
        # button's rendered position rather than from main_window height
        # (main_window height == viewport height under set_primary_window, making
        # a window-height measurement circular and causing unbounded growth).
        def _auto_fit_viewport():
            try:
                if not dpg.does_item_exist("summon_btn"):
                    return
                btn_pos  = dpg.get_item_pos("summon_btn")
                btn_size = dpg.get_item_rect_size("summon_btn")
                if not (btn_pos and btn_size and btn_size[1]):
                    return
                content_bottom = btn_pos[1] + btn_size[1]
                total_h  = dpg.get_viewport_height()
                client_h = dpg.get_viewport_client_height() or total_h
                chrome   = max(40, total_h - client_h)
                target   = content_bottom + int(28 * scale) + chrome
                dpg.set_viewport_height(target)
            except Exception:
                pass

        # Frame 2 = first frame fully rendered with measurable widget rects.
        # Only called once at startup; on_mode_change uses pre-computed heights
        # instead of this measurement to avoid re-entry and growth artifacts.
        try:
            dpg.set_frame_callback(2, _auto_fit_viewport)
        except Exception:
            pass

        if scope_default:
            on_discover()

        signal.signal(signal.SIGINT, lambda *_: dpg.stop_dearpygui())
        dpg.start_dearpygui()
    finally:
        dpg.destroy_context()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Arcana Summoning Rite — install Arcana and optionally clone grimoires"
    )
    parser.add_argument(
        "--arcana-url",
        help="URL of the Arcana git repository to install (defaults to public GitHub Arcana)",
    )
    parser.add_argument(
        "--scope",
        help="URL of the group/org containing your grimoires (e.g., https://github.com/my-org)",
    )
    parser.add_argument("--cli", action="store_true", help="Force terminal mode (no GUI)")
    parser.add_argument("--gui", action="store_true", help="Force GUI mode")
    args = parser.parse_args()

    use_gui = False
    gui_skip_reason = ""
    if args.gui:
        use_gui = True
    elif not args.cli:
        if sys.platform == "win32":
            use_gui = True
        else:
            session_type = os.environ.get("XDG_SESSION_TYPE", "")
            has_display = bool(
                os.environ.get("DISPLAY")
                or os.environ.get("WAYLAND_DISPLAY")
                or session_type in ("x11", "wayland")
            )
            if not has_display:
                gui_skip_reason = "no display server detected"
            else:
                # On Wayland without XWayland, DISPLAY is unset and DearPyGui
                # (which requires X11/GLX) will fail.  _probe_gui() catches this
                # before the main GUI loop starts and raises RuntimeError, which
                # the caller handles by falling back to CLI.  Setting DISPLAY=:0
                # blindly causes GLFW to connect to a nonexistent X server and
                # produce GLX failures — omit the assignment and let the probe
                # decide.
                use_gui = True

    if use_gui:
        try:
            run_gui(args)
        except Exception as e:
            print(f"  [WARN]  GUI failed ({e}), falling back to CLI")
            run_cli(args)
    else:
        if gui_skip_reason and not args.cli:
            print(f"  [INFO]  Using CLI mode: {gui_skip_reason}")
        run_cli(args)


if __name__ == "__main__":
    main()
