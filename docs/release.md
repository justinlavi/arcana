---
type: reference
title: "Release Workflow"
aliases: ["release", "binary-release"]
tags: [type/reference, arcana/docs]
authority: grimoire
last_verified: 2026-05-19
---

# Arcana Release Guide

How to build and publish Summoning Rite binaries for GitHub Releases.

---

## Release Assets

Arcana does not commit built binaries to the repository. The release workflow builds platform-specific Summoning Rite binaries and uploads them as GitHub Release assets.

Expected assets:
- `grimoire-summon-linux-x86_64.tar.gz`
- `grimoire-summon-linux-x86_64.tar.gz.sha256`
- `grimoire-summon-macos-arm64.tar.gz`
- `grimoire-summon-macos-arm64.tar.gz.sha256`
- `grimoire-summon-windows-x86_64.zip`
- `grimoire-summon-windows-x86_64.zip.sha256`

Actual architecture labels are produced by the build runner.

`rites/summon.sh` is the single bootstrap entry point. Windows users can run it from Git Bash; the bootstrap detects Git Bash's `MINGW*` / `MSYS*` / `CYGWIN*` platform names, downloads the Windows `.zip` asset, and runs `grimoire-summon.exe`. WSL is treated as Linux and uses the Linux assets.

---

## Local Build

Build from a clean virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install '.[build]'
python rites/build_summon_binary.py --clean
```

The `[build]` extra (declared in `pyproject.toml`) pins the same DearPyGui + PyInstaller versions the release pipeline expects.

Artifacts are written to `dist/summon/`.

---

## GitHub Actions

Workflow: `.github/workflows/summon-release.yml`

Manual test build:
1. Open **Actions** in GitHub.
2. Run **Build Summoning Rite Releases**.
3. Leave `publish` disabled.
4. Download the workflow artifacts and test them locally.

Publish a draft release:
1. Push a tag such as `v1.2.3`.
2. The workflow builds Linux, macOS, and Windows artifacts.
3. The publish job creates a draft GitHub Release if needed.
4. The publish job uploads archives and checksums.
5. Review the draft release, edit notes if needed, then publish.

Manual publish is also available from the workflow form by setting `publish` to true and providing a tag.

During active development, you may repeatedly publish the same test tag, such as `v1.0.0`, without creating new version numbers:
1. Run the workflow manually.
2. Set `publish` to true.
3. Set `tag` to `v1.0.0`.
4. Leave `move_tag` enabled to point the tag at the workflow commit.
5. Choose whether the release should be `draft` or `prerelease`.

The workflow uploads assets with clobbering enabled, so new archives replace old archives on the same release. Use this only while the tag is still pre-final; once a release is public and trusted by users, avoid moving its tag.

Draft releases are useful for private review, but they are not useful for unauthenticated curl testing. For public bootstrap testing, publish `v1.0.0` as a prerelease, then repeatedly rerun the workflow with the same tag and clobbered assets. When the release is final, edit the release in GitHub and clear the prerelease flag.

---

## Bootstrap Behavior

`rites/summon.sh` prefers release assets when run through the public curl pipe, except on Linux GUI sessions where it uses the Python source launcher by default. The Linux source-first GUI path avoids frozen GLFW/GLX library drift across fast-moving distro render stacks while preserving binary use for CLI/headless Linux and for macOS/Windows. Running from a local checkout keeps using local source by default, which is better for Arcana development.

Public curl flow:
1. Detect OS and architecture.
2. Download `grimoire-summon-{platform}.tar.gz` on Linux/macOS or `grimoire-summon-{platform}.zip` on Windows from GitHub Releases.
3. Download and verify the matching `.sha256` checksum.
4. Extract and run `grimoire-summon` on Linux/macOS or `grimoire-summon.exe` on Windows.
5. Fall back to the Python source bootstrap if any release step fails.

On Linux with a detected display session, `GRIMOIRE_SUMMON_BINARY=auto` skips steps 2-4 and goes straight to source mode. Use `GRIMOIRE_SUMMON_BINARY=always` to test the Linux release binary directly.

Binary controls:
- `GRIMOIRE_SUMMON_BINARY=auto` - default. Piped scripts try release binaries except Linux GUI sessions; local scripts use source.
- `GRIMOIRE_SUMMON_BINARY=always` - force release binary lookup.
- `GRIMOIRE_SUMMON_BINARY=never` - force Python source bootstrap.
- `GRIMOIRE_SUMMON_RELEASE_TAG=v1.0.0` - download from a specific release tag instead of `latest`.

GitHub's `latest` release URL resolves only to a non-draft, non-prerelease release. For prerelease testing, set `GRIMOIRE_SUMMON_RELEASE_TAG` to the exact tag.

Example test command for a repeatedly overwritten prerelease:

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | GRIMOIRE_SUMMON_RELEASE_TAG=v1.0.0 bash
```

If no matching release binary is available or checksum verification fails, the script falls back to the Python source bootstrap.
