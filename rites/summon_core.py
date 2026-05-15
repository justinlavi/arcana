#!/usr/bin/env python3
"""Core install logic for the Arcana Summoning Rite.

Sister module to `summon.py` (the dispatcher) and `summon_gui.py` (the
DearPyGui front end). This module is the install engine: constants, the
Logger, git/HTTP helpers, GitHub/GitLab discovery, the install pipeline,
and the interactive CLI flow.

It depends only on the Python standard library so it stays usable in
headless environments where DearPyGui isn't installable.
"""

import json
import os
import re
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

SETTINGS_PATH = Path.home() / ".config" / "grimoire" / "summon.json"
SETTINGS_DEFAULTS = {
    "version": 1,
    "last_scope_url": "",
    "agent_targets": ["claude", "codex"],   # which agent files to inject
    "skip_skill_registration": False,
    "custom_arcana_url": "",
    "custom_arcana_ref": "",
}


def _load_grimoire_block():
    """Load the canonical Grimoire instruction block."""
    template_path = RITE_DIR / "templates" / "grimoire_block.md"
    if template_path.is_file():
        return "\n" + template_path.read_text(encoding="utf-8")

    # Inline fallback — kept in sync with rites/templates/grimoire_block.md.
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

    Both this terminal logger and the GUI's GuiLogger expose the same surface —
    info/ok/warn/err for tagged messages, plus `line()` for raw subprocess
    output that should appear in the user-visible log without a tag prefix.
    """
    def info(self, msg):  print(f"  [INFO]  {msg}")
    def ok(self, msg):    print(f"  [OK]    {msg}")
    def warn(self, msg):  print(f"  [WARN]  {msg}")
    def err(self, msg):   print(f"  [ERROR] {msg}")
    def line(self, text): print(text)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _subprocess_env():
    """Return a clean env dict for spawning subprocesses from a frozen binary.

    PyInstaller sets LD_LIBRARY_PATH to its extracted temp dir so its bundled
    C extensions can find their dependencies. When the binary spawns system
    tools like git, those tools' helpers (git-remote-https, etc.) also search
    LD_LIBRARY_PATH and pick up the bundled libssl / libcurl instead of the
    system versions, causing symbol-version mismatches on distros with newer
    OpenSSL (e.g. Arch / CachyOS). Stripping the key fixes this without
    affecting the binary's own Python extension loading.
    """
    if not getattr(sys, "frozen", False):
        return None
    env = dict(os.environ)
    env.pop("LD_LIBRARY_PATH", None)
    return env


def git(*args, cwd=None, log=None):
    """Run a git command. Returns (success: bool, stdout: str)."""
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
    """Parse a scope URL into (host, scope)."""
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
    return [part for part in scope.split("/") if part]


def _library_key_from_repo_path(path):
    parts = _scope_parts(path)
    return parts[-1] if parts else ""


def _is_github_host(host):
    return host == "github.com" or "github" in host


def _is_gitlab_host(host):
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
    topics = topics or []
    normalized = {str(t).lower() for t in topics}
    name_l = (name or "").lower()
    desc_l = (description or "").lower()
    return (
        name_l.endswith("-grimoire")
        or "grimoire" in normalized
        or "grimoire" in desc_l
    )


def _github_entry(repo):
    name = repo.get("name") or _library_key_from_repo_path(repo.get("full_name", ""))
    return {
        "name": name,
        "description": repo.get("description") or "Domain grimoire",
        "online_path": repo.get("clone_url", ""),
    }


def _gitlab_entry(project):
    path = project.get("path") or _library_key_from_repo_path(project.get("path_with_namespace", ""))
    return {
        "name": project.get("name", path),
        "description": project.get("description") or "Domain grimoire",
        "online_path": project.get("http_url_to_repo", ""),
    }


def _gitlab_filter_grimoires(data, log):
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
    api_base = "https://api.github.com" if host == "github.com" else f"https://{host}/api/v3"
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
    data, err = _api_get(url, token_header=auth_h, token_value=auth_v)
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
            name, repo.get("description", ""), repo.get("topics") or [],
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
            log.err("Failed to clone Arcana — check network and git credentials")
            return False
    else:
        if ARCANA_DIR.is_dir():
            log.ok(f"Arcana exists: {ARCANA_DIR}")
        else:
            log.err("Cannot detect Arcana origin URL")
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
            log.err(f"Failed to clone {name} — check VPN and git credentials")
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
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if not target_path.is_file():
        target_path.write_text(f"# {title}\n", encoding="utf-8")
        log.info(f"Created {target_path}")

    content = target_path.read_text(encoding="utf-8")

    if "## Grimoire Knowledge Base" in content:
        log.ok(f"Grimoire block already present in {target_path.name} (skipping)")
        return

    if content.startswith(f"# {title}"):
        first_line_end = content.index("\n") if "\n" in content else len(content)
        content = content[:first_line_end + 1] + GRIMOIRE_BLOCK + content[first_line_end + 1:]
    else:
        content += GRIMOIRE_BLOCK

    target_path.write_text(content, encoding="utf-8")
    log.ok(f"Grimoire block injected into {target_path}")


def inject_agent_configs(log):
    """Inject Grimoire routing blocks into supported agent instruction files."""
    inject_agent_file(log, CLAUDE_MD, "CLAUDE.md")
    inject_agent_file(log, CODEX_AGENTS_MD, "AGENTS.md")


def register_skills(log):
    """Run the skill registration script."""
    log.info("Registering Grimoire skills...")
    register_script = ARCANA_DIR / "rites" / "register_skills.py"
    if not register_script.is_file():
        register_script = RITE_DIR / "register_skills.py"

    if not register_script.is_file():
        log.err(f"register_skills.py not found at {ARCANA_DIR / 'rites'} or {RITE_DIR}")
        log.err("Skills NOT registered. Re-run manually after Arcana lands:")
        log.err(f"  python3 {ARCANA_DIR / 'rites' / 'register_skills.py'}")
        return False

    result = subprocess.run(
        [sys.executable, str(register_script), "--agent", "all"],
        capture_output=True, text=True,
    )
    if result.stdout:
        for line in result.stdout.rstrip().splitlines():
            log.line(line)
    if result.stderr:
        for line in result.stderr.rstrip().splitlines():
            log.line(line)

    if result.returncode != 0:
        log.err(f"Skill registration FAILED (exit {result.returncode}). See output above.")
        log.err("Re-run manually with:")
        log.err(f"  python3 {register_script}")
        return False

    claude_skills_dir = Path.home() / ".claude" / "skills"
    codex_skills_dir = Path.home() / ".codex" / "skills"
    claude_count = len(list(claude_skills_dir.glob("grm-*"))) if claude_skills_dir.is_dir() else 0
    codex_count = len(list(codex_skills_dir.glob("grm-*"))) if codex_skills_dir.is_dir() else 0
    log.ok(f"Skills registered: {claude_count} to {claude_skills_dir}, {codex_count} to {codex_skills_dir}")
    if claude_count == 0 and codex_count == 0:
        log.warn(
            "No /grm-* skills landed in either agent directory — "
            "this usually means neither Claude Code nor Codex is set up on this machine."
        )
        log.warn(f"Run `mkdir -p ~/.claude/skills ~/.codex/skills && python3 {register_script}` after installing your agent of choice.")
    return True


# ---------------------------------------------------------------------------
# Shared install pipeline
# ---------------------------------------------------------------------------


def finalize_install(installed_keys, library, log):
    """Run the post-Arcana install steps shared by both CLI and GUI modes."""
    if installed_keys:
        update_local_library(installed_keys, library, log)
    inject_agent_configs(log)
    return register_skills(log)


# ---------------------------------------------------------------------------
# CLI mode
# ---------------------------------------------------------------------------


def _prompt_cli_mode(scope_preselected):
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
            log.warn("No grimoires available to clone. Continuing with Arcana-only install.")
        else:
            log.ok(f"Library loaded ({len(library['grimoires'])} grimoire(s) available)")
            selected_keys = _cli_select_grimoires(library, log)
            if not selected_keys:
                log.warn("No grimoires selected. Continuing with Arcana-only install.")
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
                    log.warn("No grimoires were cloned successfully — continuing with Arcana-only install.")

    print()
    skills_ok = finalize_install(installed_keys, library, log)
    _print_cli_summary(mode, installed_keys, skills_ok)

