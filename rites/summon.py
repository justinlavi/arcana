#!/usr/bin/env python3
"""Grimoire Summoning Rite — cross-platform grimoire installer.

Usage:
    python3 summon.py [--scope URL] [--cli] [--gui]

One-liner entry point (substitute your Arcana URL):
    git clone --depth 1 <your-arcana-url> /tmp/grimoire-summon && bash /tmp/grimoire-summon/rites/summon.sh

Options:
    --scope URL    URL of the group/org containing your grimoires
    --cli          Force terminal mode (no GUI)
    --gui          Force GUI mode
    -h, --help     Show this help message

Environment variables:
    GRIMOIRE_SCOPE    Same as --scope (flag takes precedence)
    GITLAB_TOKEN      GitLab personal access token for private instances
    GITHUB_TOKEN      GitHub token for private orgs
"""

import argparse
import json
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GRIMOIRE_HOME = Path.home() / "grimoire"
ARCANA_DIR = GRIMOIRE_HOME / "arcana"
LOCAL_CATALOG = GRIMOIRE_HOME / "catalog.json"
CLAUDE_MD = Path.home() / ".claude" / "CLAUDE.md"
RITE_DIR = Path(__file__).resolve().parent
REPO_ROOT = RITE_DIR.parent

GRIMOIRE_BLOCK = """\

## Grimoire Knowledge Base

**Catalog**: `~/grimoire/catalog.json` — read this file to resolve named grimoire keys and their paths.

**Arcana key**: `GRIMOIRE_ARCANA` — resolved from catalog or defaults to `~/grimoire/arcana/`

**Skills**: Grimoire operations are available as `/grm-*` skills (e.g., `/grm-help`, `/grm-improve`).

**Routing**:
1. Determine the active grimoire from working directory or project context; look up its `local_path` in the catalog.
2. Read `{active grimoire}/INDEX.md` first; route deterministically: `INDEX.md` > chapter `INDEX.md` > 1-2 page docs.
3. For Grimoire meta-knowledge: read `GRIMOIRE_ARCANA/INDEX.md`.
4. Do not modify Grimoire files unless a `/grm-*` skill or explicit instruction asks for it.
"""

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
        https://gitlab.co/team/grimoire → ("gitlab.co", "team/grimoire")
        https://server.com              → ("server.com", "")
    """
    path = re.sub(r"^https?://", "", url).rstrip("/")
    if "/" in path:
        host, scope = path.split("/", 1)
    else:
        host, scope = path, ""
    return host, scope


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


def _gitlab_filter_grimoires(data, log):
    """Extract *-grimoire entries from a GitLab project list."""
    if not isinstance(data, list):
        log.warn(f"GitLab API returned unexpected response type: {type(data).__name__}")
        return {}
    entries = {}
    for project in data:
        path = project.get("path", "")
        if not path.endswith("-grimoire"):
            continue
        entries[path] = {
            "name": project.get("name", path),
            "description": project.get("description") or "Domain grimoire",
            "online_path": project.get("http_url_to_repo", ""),
        }
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
    """Query GitLab API for *-grimoire repos. Returns dict of catalog entries."""
    auth_h = "PRIVATE-TOKEN" if token else None
    auth_v = token or None

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

    encoded = scope.replace("/", "%2F")
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
    """Query GitHub API for *-grimoire repos. Returns dict of catalog entries."""
    if host == "github.com":
        api_base = "https://api.github.com"
    else:
        api_base = f"https://{host}/api/v3"

    url = f"{api_base}/orgs/{scope}/repos?per_page=100"

    log.info(f"Trying GitHub API: {url}")
    data, err = _api_get(
        url,
        token_header="Authorization" if token else None,
        token_value=f"Bearer {token}" if token else None,
    )
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
        if not name.endswith("-grimoire"):
            continue
        entries[name] = {
            "name": name,
            "description": repo.get("description") or "Domain grimoire",
            "online_path": repo.get("clone_url", ""),
        }
    return entries


def discover_grimoires(scope_url, log, explicit_token=""):
    """Discover grimoires from a scope URL. Returns dict of catalog entries."""
    host, scope = parse_scope_url(scope_url)
    if not host:
        log.warn("Could not parse host from URL")
        return {}

    if scope:
        log.info(f"Searching {host}/{scope} for grimoires...")
    else:
        log.info(f"Searching {host} for grimoires...")

    gl_token = _resolve_token(host, "GITLAB_TOKEN", explicit_token, log)
    entries = try_gitlab_discovery(host, scope, gl_token, log)
    if entries:
        log.ok(f"Discovered {len(entries)} grimoire(s) via GitLab API")
        return entries

    if scope:
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


def load_static_catalog():
    """Load the global catalog.json from Arcana. Returns dict."""
    catalog_path = ARCANA_DIR / "catalog.json"
    if not catalog_path.is_file():
        catalog_path = REPO_ROOT / "catalog.json"
    if not catalog_path.is_file():
        return {"grimoires": {}}
    try:
        with open(catalog_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"grimoires": {}}


def install_grimoire(key, entry, log):
    """Clone or update a single grimoire. Returns True on success."""
    name = entry.get("name", key)
    url = entry.get("online_path", "")
    target = GRIMOIRE_HOME / key

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


def update_local_catalog(installed_keys, catalog, log):
    """Update ~/grimoire/catalog.json with installed grimoires."""
    log.info("Updating local catalog...")

    if LOCAL_CATALOG.is_file():
        try:
            with open(LOCAL_CATALOG) as f:
                local = json.load(f)
        except (json.JSONDecodeError, OSError):
            local = {"grimoires": {}}
    else:
        local = {"grimoires": {}}

    for key in installed_keys:
        entry = catalog.get("grimoires", {}).get(key, {})
        local["grimoires"][key] = {
            "local_path": f"$HOME/grimoire/{key}",
            "online_path": entry.get("online_path", ""),
        }

    with open(LOCAL_CATALOG, "w") as f:
        json.dump(local, f, indent=2)
        f.write("\n")

    log.ok(f"Local catalog updated: {LOCAL_CATALOG}")


def inject_claude_md(log):
    """Inject Grimoire routing block into ~/.claude/CLAUDE.md."""
    log.info("Configuring CLAUDE.md...")

    claude_dir = CLAUDE_MD.parent
    claude_dir.mkdir(parents=True, exist_ok=True)

    if not CLAUDE_MD.is_file():
        CLAUDE_MD.write_text("# CLAUDE.md\n", encoding="utf-8")
        log.info(f"Created {CLAUDE_MD}")

    content = CLAUDE_MD.read_text(encoding="utf-8")

    if "## Grimoire Knowledge Base" in content:
        log.ok("Grimoire block already present in CLAUDE.md (skipping)")
        return

    if content.startswith("# CLAUDE.md"):
        first_line_end = content.index("\n") if "\n" in content else len(content)
        content = content[: first_line_end + 1] + GRIMOIRE_BLOCK + content[first_line_end + 1 :]
    else:
        content += GRIMOIRE_BLOCK

    CLAUDE_MD.write_text(content, encoding="utf-8")
    log.ok(f"Grimoire block injected into {CLAUDE_MD}")


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
        [sys.executable, str(register_script)],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        for line in result.stdout.strip().splitlines():
            print(line)
    if result.returncode != 0:
        log.warn("Skill registration had warnings (see above)")
    else:
        log.ok("Skills registered to ~/.claude/skills/")


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
    GRIMOIRE_HOME.mkdir(parents=True, exist_ok=True)
    log.ok(f"Install directory: {GRIMOIRE_HOME}")

    # Install Arcana
    print()
    arcana_url = detect_arcana_url()
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
        print("  Press Enter to skip and use the static catalog only.")
        print()
        print("  Examples:")
        print("    https://github.com/my-org")
        print("    https://gitlab.company.com/my-team")
        print("    https://gitlab.com/company/grimoires")
        print()
        scope_url = input("  Grimoire location: ").strip()

    # Build catalog: static + discovered
    catalog = load_static_catalog()

    if scope_url:
        discovered = discover_grimoires(scope_url, log)
        for key, entry in discovered.items():
            if key not in catalog["grimoires"]:
                catalog["grimoires"][key] = entry
    else:
        log.info("Skipping discovery")

    if not catalog["grimoires"]:
        log.err("No grimoires found (catalog is empty and discovery did not find any)")
        sys.exit(1)

    log.ok(f"Catalog loaded ({len(catalog['grimoires'])} grimoire(s) available)")

    # Display menu
    print()
    print("  Available Grimoires:")
    print("  --------------------")

    keys = sorted(catalog["grimoires"].keys())
    for i, key in enumerate(keys, 1):
        entry = catalog["grimoires"][key]
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
        entry = catalog["grimoires"][key]
        if install_grimoire(key, entry, log):
            installed_keys.append(key)

    if not installed_keys:
        log.err("No grimoires were installed")
        sys.exit(1)

    # Update local catalog
    print()
    update_local_catalog(installed_keys, catalog, log)

    # Inject CLAUDE.md
    print()
    inject_claude_md(log)

    # Register skills
    print()
    register_skills(log)

    # Summary
    print()
    print("============================================")
    print("  Grimoire Summoning Complete")
    print("============================================")
    print()
    print("  Arcana:  ~/grimoire/arcana/")
    print()
    print("  Installed grimoires:")
    for key in installed_keys:
        print(f"    - ~/grimoire/{key}/")
    print()
    print(f"  Local catalog: {LOCAL_CATALOG}")
    print(f"  CLAUDE.md:     {CLAUDE_MD}")
    print("  Skills:        ~/.claude/skills/")
    print()
    print("  Next steps:")
    print("    1. Open a new Claude Code session")
    print("    2. Try: /grm-help")
    print()


# ---------------------------------------------------------------------------
# GUI mode
# ---------------------------------------------------------------------------


def _ensure_customtkinter():
    """Import customtkinter, auto-installing via pip if missing."""
    try:
        import customtkinter
        return customtkinter
    except ImportError:
        pass
    for pip_args in (
        [sys.executable, "-m", "pip", "install", "--user", "customtkinter"],
        [sys.executable, "-m", "pip", "install", "customtkinter"],
    ):
        result = subprocess.run(pip_args, capture_output=True, text=True)
        if result.returncode == 0:
            break
    else:
        raise ImportError(
            "Failed to install customtkinter. Install manually: pip install customtkinter"
        )
    import customtkinter
    return customtkinter


# Grimoire color palette
_COLORS = {
    "bg": "#1a1b2e",
    "surface": "#242540",
    "surface2": "#2d2f4e",
    "border": "#3a3c5e",
    "primary": "#7c5cbf",
    "primary_hover": "#9370db",
    "text": "#e0e0e8",
    "text_dim": "#8888a0",
    "entry_bg": "#1e1f34",
    "log_bg": "#141524",
    "ok": "#66bb6a",
    "warn": "#ffa726",
    "err": "#ef5350",
    "info": "#64b5f6",
}


def run_gui(args):
    """CustomTkinter GUI summoning flow."""
    ctk = _ensure_customtkinter()
    from tkinter import messagebox

    C = _COLORS
    log_widget = None

    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.title("Grimoire — Summoning Rite")
    root.geometry("700x820")
    root.minsize(560, 680)
    root.configure(fg_color=C["bg"])

    class GUILogger:
        TAG_MAP = {
            "OK": ("ok", C["ok"]),
            "INFO": ("info", C["info"]),
            "WARN": ("warn", C["warn"]),
            "ERROR": ("err", C["err"]),
        }

        def _append(self, tag, msg):
            if not log_widget:
                return
            log_widget.configure(state="normal")
            _, color = self.TAG_MAP.get(tag, ("info", C["info"]))
            log_widget.insert("end", f"  [{tag}]  {msg}\n", tag)
            log_widget.tag_config(tag, foreground=color)
            log_widget.see("end")
            log_widget.configure(state="disabled")
            root.update_idletasks()

        def info(self, msg):
            self._append("INFO", msg)

        def ok(self, msg):
            self._append("OK", msg)

        def warn(self, msg):
            self._append("WARN", msg)

        def err(self, msg):
            self._append("ERROR", msg)

    log = GUILogger()

    # --- Main container (grid layout for stable resizing) ---
    main = ctk.CTkFrame(root, fg_color=C["bg"])
    main.pack(fill="both", expand=True, padx=24, pady=20)
    main.columnconfigure(0, weight=1)

    row = 0

    # --- Header ---
    ctk.CTkLabel(
        main, text="Grimoire", font=("Segoe UI", 24, "bold"),
        text_color=C["text"], anchor="w",
    ).grid(row=row, column=0, sticky="ew"); row += 1

    ctk.CTkLabel(
        main, text="Summoning Rite", font=("Segoe UI", 13),
        text_color=C["text_dim"], anchor="w",
    ).grid(row=row, column=0, sticky="ew", pady=(0, 12)); row += 1

    # Separator
    ctk.CTkFrame(main, height=2, fg_color=C["border"]).grid(
        row=row, column=0, sticky="ew", pady=(0, 16)); row += 1

    # --- Scope section ---
    ctk.CTkLabel(
        main, text="Grimoire Location", font=("Segoe UI", 13, "bold"),
        text_color=C["text"], anchor="w",
    ).grid(row=row, column=0, sticky="ew", pady=(0, 6)); row += 1

    scope_row = ctk.CTkFrame(main, fg_color="transparent")
    scope_row.grid(row=row, column=0, sticky="ew", pady=(0, 4)); row += 1

    scope_var = ctk.StringVar(value=args.scope or os.environ.get("GRIMOIRE_SCOPE", ""))
    scope_entry = ctk.CTkEntry(
        scope_row, textvariable=scope_var, font=("Consolas", 13),
        fg_color=C["entry_bg"], border_color=C["border"], text_color=C["text"],
        placeholder_text="https://github.com/my-org", placeholder_text_color=C["text_dim"],
        height=38, corner_radius=6,
    )
    scope_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

    discover_btn = ctk.CTkButton(
        scope_row, text="Discover", width=110, height=38, corner_radius=6,
        fg_color=C["primary"], hover_color=C["primary_hover"],
        font=("Segoe UI", 13, "bold"),
        command=lambda: on_discover(),
    )
    discover_btn.pack(side="right")

    ctk.CTkLabel(
        main,
        text="e.g.  https://github.com/my-org  |  https://gitlab.company.com/team",
        font=("Segoe UI", 11), text_color=C["text_dim"], anchor="w",
    ).grid(row=row, column=0, sticky="ew", pady=(2, 10)); row += 1

    # --- Token field ---
    token_row = ctk.CTkFrame(main, fg_color="transparent")
    token_row.grid(row=row, column=0, sticky="ew", pady=(0, 14)); row += 1

    ctk.CTkLabel(
        token_row, text="Token", font=("Segoe UI", 12),
        text_color=C["text_dim"], anchor="w", width=50,
    ).pack(side="left", padx=(0, 8))

    token_var = ctk.StringVar()
    token_entry = ctk.CTkEntry(
        token_row, textvariable=token_var, font=("Consolas", 12), show="*",
        fg_color=C["entry_bg"], border_color=C["border"], text_color=C["text"],
        placeholder_text="Optional — auto-detects from git credentials / env vars",
        placeholder_text_color=C["text_dim"],
        height=34, corner_radius=6,
    )
    token_entry.pack(side="left", fill="x", expand=True)

    # --- Grimoire selection (expandable) ---
    ctk.CTkLabel(
        main, text="Available Grimoires", font=("Segoe UI", 13, "bold"),
        text_color=C["text"], anchor="w",
    ).grid(row=row, column=0, sticky="ew", pady=(0, 6)); row += 1

    grimoire_row = row; row += 1
    main.rowconfigure(grimoire_row, weight=3, minsize=80)

    grimoire_frame = ctk.CTkScrollableFrame(
        main, fg_color=C["surface"], border_color=C["border"],
        border_width=1, corner_radius=8,
        scrollbar_button_color=C["surface2"],
        scrollbar_button_hover_color=C["border"],
    )
    grimoire_frame.grid(row=grimoire_row, column=0, sticky="nsew", pady=(0, 14))

    placeholder = ctk.CTkLabel(
        grimoire_frame,
        text="Enter a scope URL and press Discover to search for grimoires.",
        font=("Segoe UI", 12), text_color=C["text_dim"],
    )
    placeholder.pack(pady=30, padx=16)

    checkbox_vars = {}
    catalog = {"grimoires": {}}

    def populate_grimoires(entries):
        nonlocal catalog
        for widget in grimoire_frame.winfo_children():
            widget.destroy()

        checkbox_vars.clear()
        catalog["grimoires"].update(entries)

        if not catalog["grimoires"]:
            ctk.CTkLabel(
                grimoire_frame,
                text="No grimoires found. Check your scope URL and authentication tokens.",
                font=("Segoe UI", 12), text_color=C["text_dim"],
            ).pack(pady=30, padx=16)
            return

        for key in sorted(catalog["grimoires"]):
            entry = catalog["grimoires"][key]
            var = ctk.BooleanVar(value=True)
            checkbox_vars[key] = var
            name = entry.get("name", key)
            desc = entry.get("description", "")

            row_f = ctk.CTkFrame(grimoire_frame, fg_color="transparent")
            row_f.pack(fill="x", padx=6, pady=4)

            ctk.CTkCheckBox(
                row_f, variable=var, text="",
                width=24, height=24, corner_radius=4,
                fg_color=C["primary"], hover_color=C["primary_hover"],
                border_color=C["border"], checkmark_color="#ffffff",
            ).pack(side="left", padx=(4, 10))

            ctk.CTkLabel(
                row_f, text=name, font=("Segoe UI", 13, "bold"),
                text_color=C["text"], anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row_f, text=f"  —  {desc}", font=("Segoe UI", 12),
                text_color=C["text_dim"], anchor="w",
            ).pack(side="left", fill="x", expand=True)

    def on_discover():
        scope = scope_var.get().strip()
        token = token_var.get().strip()
        static = load_static_catalog()
        catalog["grimoires"] = dict(static.get("grimoires", {}))

        if scope:
            discovered = discover_grimoires(scope, log, explicit_token=token)
            for k, v in discovered.items():
                if k not in catalog["grimoires"]:
                    catalog["grimoires"][k] = v
        else:
            log.info("No scope URL — using static catalog only")

        populate_grimoires(catalog["grimoires"])

    # --- Log area (expandable, but less than grimoire list) ---
    ctk.CTkLabel(
        main, text="Log", font=("Segoe UI", 13, "bold"),
        text_color=C["text"], anchor="w",
    ).grid(row=row, column=0, sticky="ew", pady=(0, 6)); row += 1

    log_row = row; row += 1
    main.rowconfigure(log_row, weight=1, minsize=100)

    log_widget = ctk.CTkTextbox(
        main, corner_radius=8,
        fg_color=C["log_bg"], border_color=C["border"], border_width=1,
        text_color=C["text_dim"], font=("Consolas", 12),
        state="disabled", wrap="word",
        scrollbar_button_color=C["surface2"],
        scrollbar_button_hover_color=C["border"],
    )
    log_widget.grid(row=log_row, column=0, sticky="nsew", pady=(0, 18))

    # --- Keyboard shortcuts ---
    def _select_all_entry(event):
        event.widget.select_range(0, "end")
        event.widget.icursor("end")
        return "break"

    def _select_all_textbox(event):
        event.widget.tag_add("sel", "1.0", "end")
        return "break"

    scope_entry.bind("<Control-a>", _select_all_entry)
    scope_entry.bind("<Return>", lambda _: on_discover())
    token_entry.bind("<Control-a>", _select_all_entry)
    token_entry.bind("<Return>", lambda _: on_discover())
    log_widget.bind("<Control-a>", _select_all_textbox)

    # --- Bottom buttons (fixed height, never shrinks) ---
    btn_row = ctk.CTkFrame(main, fg_color="transparent", height=48)
    btn_row.grid(row=row, column=0, sticky="ew"); row += 1

    def on_summon():
        selected = [k for k, v in checkbox_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one grimoire.")
            return

        summon_btn.configure(state="disabled")
        cancel_btn.configure(state="disabled")
        discover_btn.configure(state="disabled")
        root.update_idletasks()

        if not check_git(log):
            messagebox.showerror("Error", "git is not installed.")
            root.destroy()
            return

        GRIMOIRE_HOME.mkdir(parents=True, exist_ok=True)

        arcana_url = detect_arcana_url()
        if not install_arcana(arcana_url, log):
            messagebox.showerror("Error", "Failed to install Arcana.")
            root.destroy()
            return

        log.info("Installing grimoires...")
        installed = []
        for key in selected:
            entry = catalog["grimoires"][key]
            if install_grimoire(key, entry, log):
                installed.append(key)

        if not installed:
            log.err("No grimoires were installed")
            messagebox.showerror("Error", "No grimoires were installed.")
            summon_btn.configure(state="normal")
            cancel_btn.configure(state="normal")
            discover_btn.configure(state="normal")
            return

        update_local_catalog(installed, catalog, log)
        inject_claude_md(log)
        register_skills(log)

        log.ok("Summoning complete!")
        messagebox.showinfo(
            "Summoning Complete",
            f"Installed {len(installed)} grimoire(s).\n\n"
            "Next steps:\n"
            "1. Open a new Claude Code session\n"
            "2. Try: /grm-help",
        )
        root.destroy()

    cancel_btn = ctk.CTkButton(
        btn_row, text="Cancel", width=120, height=42, corner_radius=6,
        fg_color=C["surface2"], hover_color=C["border"],
        text_color=C["text"], font=("Segoe UI", 13),
        command=root.destroy,
    )
    cancel_btn.pack(side="right", padx=(12, 0))

    summon_btn = ctk.CTkButton(
        btn_row, text="Summon", width=140, height=42, corner_radius=6,
        fg_color=C["primary"], hover_color=C["primary_hover"],
        font=("Segoe UI", 13, "bold"),
        command=on_summon,
    )
    summon_btn.pack(side="right")

    if scope_var.get():
        root.after(100, on_discover)

    signal.signal(signal.SIGINT, lambda *_: root.destroy())
    root.mainloop()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Grimoire Summoning Rite — install and configure grimoires"
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
                # tkinter needs X11 — on Wayland, ensure DISPLAY points to XWayland
                if not os.environ.get("DISPLAY") and (
                    os.environ.get("WAYLAND_DISPLAY") or session_type == "wayland"
                ):
                    os.environ["DISPLAY"] = ":0"
                try:
                    import tkinter
                    tkinter.Tk().destroy()
                    use_gui = True
                except ImportError:
                    gui_skip_reason = (
                        "tkinter is not installed — install python3-tk (apt) / python3-tkinter (dnf)"
                    )
                except Exception:
                    gui_skip_reason = "tkinter cannot connect to display"

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
