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

from agent_targets import (
    automatic_instruction_target_ids,
    automatic_instruction_targets,
    skill_registration_targets,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RITE_DIR = Path(__file__).resolve().parent
REPO_ROOT = RITE_DIR.parent
GRIMOIRES_HOME = Path.home() / "grimoires"
ARCANA_DIR = GRIMOIRES_HOME / "arcana"
LOCAL_LIBRARY = GRIMOIRES_HOME / "library.json"
DEFAULT_ARCANA_URL = "https://github.com/justinlavi/arcana.git"


DEFAULT_AGENT_TARGETS = automatic_instruction_target_ids(REPO_ROOT)
SETTINGS_PATH = Path.home() / ".config" / "grimoire" / "summon.json"
SETTINGS_DEFAULTS = {
    "version": 1,
    "last_scope_url": "",
    "agent_targets": DEFAULT_AGENT_TARGETS,
    "skip_skill_registration": False,
    "custom_arcana_url": "",
    "custom_arcana_ref": "",
}


def _load_grimoire_block():
    """Load the canonical Grimoire instruction block from the markdown template."""
    candidates = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        bundle_root = Path(meipass)
        candidates.extend(
            [
                bundle_root / "rites" / "templates" / "grimoire_block.md",
                bundle_root / "templates" / "grimoire_block.md",
            ]
        )
    candidates.extend(
        [
            RITE_DIR / "templates" / "grimoire_block.md",
            REPO_ROOT / "rites" / "templates" / "grimoire_block.md",
            ARCANA_DIR / "rites" / "templates" / "grimoire_block.md",
        ]
    )

    for template_path in candidates:
        if template_path.is_file():
            return "\n" + template_path.read_text(encoding="utf-8")

    checked = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(
        "Could not find canonical Grimoire block template. "
        f"Checked: {checked}"
    )


GRIMOIRE_BLOCK = _load_grimoire_block()

# Idempotency sentinels for the injected Grimoire block. The canonical template
# wraps the block in BEGIN/END markers with the heading inside; older injections
# carried only the heading. A block written by any path - this injector, the
# template, /arc-agent-update, or RESTORATION.md - counts as present when EITHER
# sentinel is found, so a re-run never double-injects regardless of which form is
# on disk. summon_state imports these so the detector and injector cannot drift.
BEGIN_SENTINEL = "<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->"
END_SENTINEL = "<!-- END GRIMOIRE KNOWLEDGE BASE -->"
HEADING_SENTINEL = "## Grimoire Knowledge Base"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


class Logger:
    """Terminal logger with prefixed output.

    Both this terminal logger and the GUI's GuiLogger expose the same surface
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


def system_python():
    """Return a usable Python executable for spawning sister scripts.

    In a frozen PyInstaller binary, `sys.executable` points at the binary
    itself (e.g. `grimoire-summon`) - invoking it as a Python interpreter
    just makes the binary's argparse choke on the script path. Probe the
    PATH for a real `python3` / `python` interpreter and prefer that;
    fall back to `sys.executable` only when not frozen.
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
    return sys.executable


GIT_TIMEOUT = 600  # seconds; backstop so a stalled fetch cannot hang the install


def git(*args, cwd=None, log=None):
    """Run a git command. Returns (success: bool, stdout: str)."""
    env = _subprocess_env()
    if env is None:
        env = dict(os.environ)
    env.setdefault("GIT_TERMINAL_PROMPT", "0")  # fail instead of blocking on an auth prompt
    try:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=cwd,
            capture_output=True,
            text=True,
            env=env,
            timeout=GIT_TIMEOUT,
        )
        if result.returncode != 0 and log is not None:
            stderr = (result.stderr or "").rstrip()
            if stderr:
                for line in stderr.splitlines():
                    log.line(line)
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        if log is not None:
            log.line(
                f"git timed out after {GIT_TIMEOUT}s - check network access "
                "and that authentication is configured"
            )
        return False, ""
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
        or os.environ.get("ARCANA_URL", "")
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
    h = host.lower()
    return h == "github.com" or h.endswith(".github.com") or h.split(".")[0] == "github"


def _is_gitlab_host(host):
    h = host.lower()
    return h == "gitlab.com" or h.endswith(".gitlab.com") or h.split(".")[0] == "gitlab"


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
        "description": repo.get("description") or "Grimoire",
        "online_path": repo.get("clone_url", ""),
    }


def _gitlab_entry(project):
    path = project.get("path") or _library_key_from_repo_path(project.get("path_with_namespace", ""))
    return {
        "name": project.get("name", path),
        "description": project.get("description") or "Grimoire",
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
                log.warn("No credentials found - set GITLAB_TOKEN or configure git credential helper")
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
        log.warn("No credentials found - set GITLAB_TOKEN or configure git credential helper")
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
                log.warn("No credentials found - set GITHUB_TOKEN or configure git credential helper")
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

    log.err(f"No grimoires found at {scope_url} - check the URL, network, and auth tokens")
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


# Top-level files we expect in a healthy working tree. If `.git/` exists but
# none of these are checked out, the working tree is partial - most commonly
# because `git checkout` aborted on a path that's invalid on this OS (Windows
# rejects names containing < > : " | ? *).
WORKING_TREE_SENTINELS = ("README.md", "arcana.json", "arcana.md")


def working_tree_populated(target_dir):
    """True if the working tree under target_dir has at least one sentinel file."""
    return any((target_dir / s).exists() for s in WORKING_TREE_SENTINELS)


def attempt_working_tree_recovery(target_dir, name, log, git_fn=git):
    """Re-run checkout from HEAD to recover a partial working tree.

    Returns True if recovery succeeded (sentinel present afterward), False otherwise.
    """
    log.warn(f"{name}: .git/ present but working tree is partial - attempting recovery")
    ok, _ = git_fn("-C", str(target_dir), "checkout", "HEAD", "--", ".", log=log)
    if ok and working_tree_populated(target_dir):
        log.ok(f"{name}: working tree recovered via `git checkout HEAD -- .`")
        return True
    log.err(
        f"{name}: working tree still partial after recovery. The repository "
        f"likely contains a path invalid on this OS (Windows reserves "
        f"< > : \" | ? *). Inspect with `cd {target_dir} && git status`, "
        f"then either fix the upstream repo or remove {target_dir} and re-summon "
        f"once upstream is corrected."
    )
    return False


def install_arcana(arcana_url, log, git_fn=git, cancel_event=None):
    """Clone or update Arcana."""
    log.info("Installing Arcana...")
    if cancel_event is not None and cancel_event.is_set():
        log.warn("Cancelled before Arcana install")
        return False
    if (ARCANA_DIR / ".git").is_dir():
        log.info("Arcana already installed - pulling latest...")
        ok, _ = git_fn("-C", str(ARCANA_DIR), "pull", "--ff-only", log=log)
        if ok:
            log.ok(f"Arcana updated: {ARCANA_DIR}")
        else:
            log.warn("Arcana pull failed (local changes?) - skipping update")
            log.ok(f"Arcana exists: {ARCANA_DIR}")
        if not working_tree_populated(ARCANA_DIR):
            if not attempt_working_tree_recovery(ARCANA_DIR, "Arcana", log, git_fn):
                return False
    elif arcana_url:
        log.info(f"Cloning Arcana from {arcana_url}...")
        ok, _ = git_fn("clone", arcana_url, str(ARCANA_DIR), log=log)
        if not ok:
            log.err("Failed to clone Arcana - check network and git credentials")
            if (ARCANA_DIR / ".git").is_dir() and not working_tree_populated(ARCANA_DIR):
                log.err(
                    "A partial clone was left at {0}. After resolving the cause, "
                    "remove that directory and re-run summon.".format(ARCANA_DIR)
                )
            return False
        if not working_tree_populated(ARCANA_DIR):
            if not attempt_working_tree_recovery(ARCANA_DIR, "Arcana", log, git_fn):
                return False
        log.ok(f"Arcana cloned to {ARCANA_DIR}")
    else:
        if ARCANA_DIR.is_dir():
            log.ok(f"Arcana exists: {ARCANA_DIR}")
        else:
            log.err("Cannot detect Arcana origin URL")
            return False
    return True


def install_grimoire(key, entry, log, git_fn=git, cancel_event=None):
    """Clone or update a single grimoire. Returns True on success."""
    name = entry.get("name", key)
    url = entry.get("online_path", "")
    target = GRIMOIRES_HOME / key

    if cancel_event is not None and cancel_event.is_set():
        log.warn(f"Cancelled before installing {name}")
        return False

    if (target / ".git").is_dir():
        log.info(f"{name} already installed - pulling latest...")
        ok, _ = git_fn("-C", str(target), "pull", "--ff-only", log=log)
        if ok:
            log.ok(f"{name} updated: {target}")
        else:
            log.warn(f"{name} pull failed (local changes?) - skipping update")
            log.ok(f"{name} exists: {target}")
        if not working_tree_populated(target):
            if not attempt_working_tree_recovery(target, name, log, git_fn):
                return False
        return True
    elif target.is_dir():
        log.warn(f"{name} directory exists but is not a git repo - skipping")
        return True
    else:
        log.info(f"Cloning {name} from {url}...")
        ok, _ = git_fn("clone", url, str(target), log=log)
        if not ok:
            log.err(f"Failed to clone {name} - check VPN and git credentials")
            if (target / ".git").is_dir() and not working_tree_populated(target):
                log.err(
                    f"A partial clone was left at {target}. After resolving "
                    f"the cause, remove that directory and re-run summon."
                )
            return False
        if not working_tree_populated(target):
            if not attempt_working_tree_recovery(target, name, log, git_fn):
                return False
        log.ok(f"Cloned {name} to {target}")
        return True


def write_json_atomic(path, data):
    """Write JSON to path atomically: full content to a temp file, then os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)


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

    write_json_atomic(LOCAL_LIBRARY, local)
    log.ok(f"Local library updated: {LOCAL_LIBRARY}")


def inject_agent_file(log, target_path, title):
    """Inject Grimoire routing block into an agent instruction file."""
    log.info(f"Configuring {target_path.name}...")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if not target_path.is_file():
        target_path.write_text(f"# {title}\n", encoding="utf-8", newline="\n")
        log.info(f"Created {target_path}")

    content = target_path.read_text(encoding="utf-8")

    if BEGIN_SENTINEL in content or HEADING_SENTINEL in content:
        log.ok(f"Grimoire block already present in {target_path.name} (skipping)")
        return

    if content.startswith(f"# {title}"):
        first_line_end = content.index("\n") if "\n" in content else len(content)
        content = content[:first_line_end + 1] + GRIMOIRE_BLOCK + content[first_line_end + 1:]
    else:
        content += GRIMOIRE_BLOCK

    target_path.write_text(content, encoding="utf-8", newline="\n")
    log.ok(f"Grimoire block injected into {target_path}")


def inject_agent_configs(log):
    """Inject Grimoire routing blocks into supported agent instruction files."""
    for target in automatic_instruction_targets(REPO_ROOT):
        inject_agent_file(log, target["path"], target["title"])


def _registered_skill_count(skills_dir):
    """Count Arcana-managed installed skill directories under one target."""
    if not skills_dir.is_dir():
        return 0
    count = 0
    for skill_dir in skills_dir.iterdir():
        skill_file = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_file.is_file():
            continue
        try:
            content = skill_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "ARCANA_SKILL_OWNERSHIP" in content:
            count += 1
    return count


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
        [system_python(), str(register_script), "--agent", "all"],
        capture_output=True, text=True,
        env=_subprocess_env(),
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

    counts = []
    total = 0
    for config in skill_registration_targets(REPO_ROOT).values():
        count = _registered_skill_count(config["path"])
        counts.append(f"{count} to {config['path']}")
        total += count
    log.ok(f"Skills registered: {', '.join(counts)}")
    if total == 0:
        expected = ", ".join(str(config["path"]) for config in skill_registration_targets(REPO_ROOT).values())
        log.warn(
            "No Arcana-managed skills landed in any registered agent directory - "
            "this usually means no supported local agent is set up on this machine."
        )
        log.warn(f"Expected skill target(s): {expected}")
        log.warn(f"Re-run after installing your agent of choice: python3 {register_script}")
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


def _prompt_text(prompt, default=""):
    """Read an interactive prompt from stdin or the controlling terminal."""
    try:
        if sys.stdin.isatty():
            return input(prompt)
        try:
            with open("/dev/tty", "r", encoding="utf-8") as tty_in, \
                    open("/dev/tty", "w", encoding="utf-8") as tty_out:
                tty_out.write(prompt)
                tty_out.flush()
                line = tty_in.readline()
                if line == "":
                    raise EOFError
                return line.rstrip("\n")
        except OSError:
            if default is not None:
                return default
            raise EOFError
    except EOFError:
        if default is not None:
            return default
        raise


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
        choice = _prompt_text("  Choice [1]: ", default="1").strip() or "1"
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
    selection = _prompt_text(
        "  Select grimoires to install (e.g. 1 3 or a for all): ",
        default="",
    ).strip()
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
        print("  Grimoires: none cloned - Arcana only.")
        print("  To create your first grimoire, open an agent session and run: /grm-create")
    elif installed_keys:
        print("  Installed grimoires:")
        for key in installed_keys:
            print(f"   - ~/grimoires/{key}/")
    else:
        print("  Grimoires: none landed (clone failures - see log above).")
    print()
    print(f"  Local library: {LOCAL_LIBRARY}")
    print("  Agent instruction files:")
    for target in automatic_instruction_targets(REPO_ROOT):
        print(f"   - {target['label']}: {target['path']}")
    print("  Skill directories:")
    for config in skill_registration_targets(REPO_ROOT).values():
        print(f"   - {config['label']}: {config['path']}")
    print()
    if not skills_ok:
        print("  *** Skill registration failed - see errors above. Re-run: ***")
        print(f"      python3 {ARCANA_DIR / 'rites' / 'register_skills.py'}")
        print()
    print("  Next steps:")
    agent_labels = ", ".join(target["label"] for target in automatic_instruction_targets(REPO_ROOT))
    print(f"    1. Open a new {agent_labels} session")
    print("    2. Try: /arc-help")
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
            print("  Press Enter to skip grimoire cloning and install Arcana only.")
            print()
            print("  Examples:")
            print("    https://github.com/my-org")
            print("    https://gitlab.company.com/my-team")
            print("    https://gitlab.com/company/grimoires")
            print()
            scope_url = _prompt_text("  Grimoire location: ", default="").strip()

        library = {"grimoires": {}}
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
                    log.warn("No grimoires were cloned successfully - continuing with Arcana-only install.")

    print()
    skills_ok = finalize_install(installed_keys, library, log)
    _print_cli_summary(mode, installed_keys, skills_ok)

    # Leave a machine-readable record of the install so an orchestrator can
    # diff intent vs outcome. Lazy import breaks the summon_state<->summon_core
    # cycle; best-effort so a transcript failure never fails the install.
    try:
        from summon_state import record_install_transcript
        record_install_transcript(GRIMOIRES_HOME, REPO_ROOT, installed_keys, skills_ok)
    except Exception:
        pass
