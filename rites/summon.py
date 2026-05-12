#!/usr/bin/env python3
"""Grimoire Summoning Rite — cross-platform grimoire installer.

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
    """Load the canonical Grimoire instruction block from rites/templates/."""
    template_path = RITE_DIR / "templates" / "grimoire_block.md"
    return "\n" + template_path.read_text(encoding="utf-8")


GRIMOIRE_BLOCK = _load_grimoire_block()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


class Logger:
    """Terminal logger with prefixed output."""

    def info(self, msg):
        print(f"  [INFO]  {msg}")

    def ok(self, msg):
        print(f"  [OK]    {msg}")

    def warn(self, msg):
        print(f"  [WARN]  {msg}")

    def err(self, msg):
        print(f"  [ERROR] {msg}")


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def git(*args, cwd=None):
    """Run a git command. Returns (success: bool, stdout: str)."""
    try:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0, result.stdout.strip()
    except FileNotFoundError:
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
        ok, _ = git("-C", str(ARCANA_DIR), "pull", "--ff-only")
        if ok:
            log.ok(f"Arcana updated: {ARCANA_DIR}")
        else:
            log.warn("Arcana pull failed (local changes?) — skipping update")
            log.ok(f"Arcana exists: {ARCANA_DIR}")
    elif arcana_url:
        log.info(f"Cloning Arcana from {arcana_url}...")
        ok, _ = git("clone", arcana_url, str(ARCANA_DIR))
        if ok:
            log.ok(f"Arcana cloned to {ARCANA_DIR}")
        else:
            log.err("Failed to clone Arcana — check network and git credentials")
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
        ok, _ = git("-C", str(target), "pull", "--ff-only")
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
        ok, _ = git("clone", url, str(target))
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
    """Run the skill registration script."""
    log.info("Registering Grimoire skills...")
    register_script = ARCANA_DIR / "rites" / "register_skills.py"

    if not register_script.is_file():
        # Fall back to current directory during first-time setup
        register_script = RITE_DIR / "register_skills.py"

    if not register_script.is_file():
        log.warn("register_skills.py not found — skipping skill registration")
        return

    result = subprocess.run(
        [sys.executable, str(register_script), "--agent", "all"],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        for line in result.stdout.strip().splitlines():
            print(line)
    if result.returncode != 0:
        log.warn("Skill registration had warnings (see above)")
    else:
        log.ok("Skills registered to ~/.claude/skills/ and ~/.codex/skills/")


# ---------------------------------------------------------------------------
# CLI mode
# ---------------------------------------------------------------------------


def run_cli(args):
    """Terminal-based interactive summoning flow."""
    log = Logger()

    print()
    print("============================================")
    print("  Grimoire Summoning Rite")
    print("============================================")
    print()

    # Check dependencies
    if not check_git(log):
        sys.exit(1)

    # Create install directory
    GRIMOIRES_HOME.mkdir(parents=True, exist_ok=True)
    log.ok(f"Install directory: {GRIMOIRES_HOME}")

    # Install Arcana
    print()
    arcana_url = resolve_arcana_url(args)
    if not install_arcana(arcana_url, log):
        sys.exit(1)

    # Discover grimoires
    print()
    log.info("Discovering grimoires...")

    scope_url = args.scope or os.environ.get("GRIMOIRE_SCOPE", "")

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

    # Build library: static + discovered
    library = load_static_library()

    if scope_url:
        discovered = discover_grimoires(scope_url, log)
        for key, entry in discovered.items():
            if key not in library["grimoires"]:
                library["grimoires"][key] = entry
    else:
        log.info("Skipping discovery")

    if not library["grimoires"]:
        log.err("No grimoires found (library is empty and discovery did not find any)")
        sys.exit(1)

    log.ok(f"Library loaded ({len(library['grimoires'])} grimoire(s) available)")

    # Display menu
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
        selected_keys = keys
    else:
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

    if not selected_keys:
        log.err("No grimoires selected")
        sys.exit(1)

    print()
    log.ok(f"Selected {len(selected_keys)} grimoire(s)")

    # Install grimoires
    print()
    log.info("Installing grimoires...")
    print()

    installed_keys = []
    for key in selected_keys:
        entry = library["grimoires"][key]
        if install_grimoire(key, entry, log):
            installed_keys.append(key)

    if not installed_keys:
        log.err("No grimoires were installed")
        sys.exit(1)

    # Update local library
    print()
    update_local_library(installed_keys, library, log)

    # Inject agent instruction files
    print()
    inject_agent_configs(log)

    # Register skills
    print()
    register_skills(log)

    # Summary
    print()
    print("============================================")
    print("  Grimoire Summoning Complete")
    print("============================================")
    print()
    print("  Arcana:  ~/grimoires/arcana/")
    print()
    print("  Installed grimoires:")
    for key in installed_keys:
        print(f"    - ~/grimoires/{key}/")
    print()
    print(f"  Local library: {LOCAL_LIBRARY}")
    print(f"  CLAUDE.md:     {CLAUDE_MD}")
    print(f"  AGENTS.md:     {CODEX_AGENTS_MD}")
    print("  Skills:        ~/.claude/skills/")
    print("                 ~/.codex/skills/")
    print()
    print("  Next steps:")
    print("    1. Open a new Claude Code or Codex/ChatGPT session")
    print("    2. Try: /grm-meta-help")
    print()


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


def run_gui(args):
    """Dear PyGui summoning flow."""
    dpg = _ensure_dearpygui()

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
            width=420,
            pos=(150, 240),
        ):
            dpg.add_text(message, wrap=380)
            dpg.add_spacer(height=10)
            dpg.add_button(label="OK", width=90, callback=close_modal)

    def set_busy(is_busy):
        for tag in ("discover_btn", "summon_btn", "cancel_btn"):
            if dpg.does_item_exist(tag):
                dpg.configure_item(tag, enabled=not is_busy)

    def populate_grimoires(entries):
        if dpg.does_item_exist("grimoire_list"):
            dpg.delete_item("grimoire_list", children_only=True)

        checkbox_tags.clear()
        library["grimoires"].update(entries)

        if not library["grimoires"]:
            dpg.add_text(
                "No grimoires found. Check your scope URL and authentication tokens.",
                parent="grimoire_list",
                wrap=620,
                color=(136, 136, 160),
            )
            return

        for key in sorted(library["grimoires"]):
            entry = library["grimoires"][key]
            name = entry.get("name", key)
            desc = entry.get("description", "")
            tag = f"grimoire::{key}"
            checkbox_tags[key] = tag
            label = name if not desc else f"{name} - {desc}"
            dpg.add_checkbox(label=label, default_value=True, tag=tag, parent="grimoire_list")

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
        selected = [key for key, tag in checkbox_tags.items() if dpg.get_value(tag)]
        if not selected:
            show_modal("No Selection", "Please select at least one grimoire.")
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

            log.info("Installing grimoires...")
            installed = []
            for key in selected:
                entry = library["grimoires"][key]
                if install_grimoire(key, entry, log):
                    installed.append(key)

            if not installed:
                log.err("No grimoires were installed")
                show_modal("Error", "No grimoires were installed.")
                return

            update_local_library(installed, library, log)
            inject_agent_configs(log)
            register_skills(log)

            log.ok("Summoning complete!")
            show_modal(
                "Summoning Complete",
                f"Installed {len(installed)} grimoire(s).\n\n"
                "Next steps:\n"
                "1. Open a new Claude Code or Codex/ChatGPT session\n"
                "2. Try: /grm-meta-help",
                close_app=True,
            )
        finally:
            set_busy(False)

    dpg.create_context()
    try:
        with dpg.theme() as grimoire_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (26, 27, 46), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (36, 37, 64), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 31, 52), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (124, 92, 191), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (147, 112, 219), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (104, 76, 165), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (224, 224, 232), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (136, 136, 160), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 20, 20, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 8, category=dpg.mvThemeCat_Core)

        dpg.bind_theme(grimoire_theme)

        with dpg.window(tag="main_window", label="Grimoire", no_title_bar=True):
            dpg.add_text("Grimoire", color=(224, 224, 232))
            dpg.add_text("Summoning Rite", color=(136, 136, 160))
            dpg.add_separator()
            dpg.add_spacer(height=8)

            dpg.add_text("Grimoire Location")
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    tag="scope_input",
                    default_value=scope_default,
                    hint="https://github.com/my-org",
                    width=-120,
                    on_enter=True,
                    callback=on_discover,
                )
                dpg.add_button(tag="discover_btn", label="Discover", width=100, callback=on_discover)
            dpg.add_text(
                "e.g. https://github.com/my-org | https://gitlab.company.com/team",
                color=(136, 136, 160),
            )

            dpg.add_text("Token", color=(136, 136, 160))
            dpg.add_input_text(
                tag="token_input",
                password=True,
                hint="Optional - auto-detects from git credentials / env vars",
                width=-1,
                on_enter=True,
                callback=on_discover,
            )

            dpg.add_spacer(height=8)
            dpg.add_text("Available Grimoires")
            with dpg.child_window(tag="grimoire_list", height=260, border=True):
                dpg.add_text(
                    "Enter a scope URL and press Discover to search for grimoires.",
                    color=(136, 136, 160),
                    wrap=620,
                )

            dpg.add_text("Log")
            dpg.add_input_text(
                tag="log_text",
                multiline=True,
                readonly=True,
                height=170,
                width=-1,
            )

            dpg.add_spacer(height=8)
            with dpg.group(horizontal=True):
                dpg.add_button(tag="summon_btn", label="Summon", width=130, callback=on_summon)
                dpg.add_button(
                    tag="cancel_btn",
                    label="Cancel",
                    width=110,
                    callback=lambda *_: dpg.stop_dearpygui(),
                )

        dpg.create_viewport(title="Grimoire - Summoning Rite", width=700, height=820, min_width=560, min_height=680)
        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window", True)
        dpg.show_viewport()

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
        description="Grimoire Summoning Rite — install and configure grimoires"
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
                if not os.environ.get("DISPLAY") and (
                    os.environ.get("WAYLAND_DISPLAY") or session_type == "wayland"
                ):
                    os.environ["DISPLAY"] = ":0"
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
