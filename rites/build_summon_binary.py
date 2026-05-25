#!/usr/bin/env python3
"""Build the Summoning Rite desktop binary with PyInstaller.

Usage:
    python3 rites/build_summon_binary.py [--clean] [--output-dir dist/summon]

The resulting artifact is intended for GitHub Release assets, not for committing
to the repository.

Exit codes:
    0  Release artifact built successfully
    1  Build failed or PyInstaller did not produce the expected binary
"""

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / "dist" / "summon"


def platform_id():
    """Return a stable platform label for release asset names."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    machine = {
        "amd64": "x86_64",
        "x86_64": "x86_64",
        "aarch64": "arm64",
        "arm64": "arm64",
    }.get(machine, machine)

    if system == "darwin":
        system = "macos"
    return f"{system}-{machine}"


def run(cmd):
    """Run a command from the repository root."""
    print("+ " + " ".join(str(part) for part in cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def sha256_file(path):
    """Calculate a SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archive_file(binary, output_dir, name):
    """Package one binary as a platform-appropriate archive."""
    if platform.system().lower() == "windows":
        archive = output_dir / f"{name}.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(binary, arcname=binary.name)
    else:
        archive = output_dir / f"{name}.tar.gz"
        with tarfile.open(archive, "w:gz") as tf:
            tf.add(binary, arcname=binary.name)
    return archive


def main():
    parser = argparse.ArgumentParser(description="Build summon binary release artifact")
    parser.add_argument("--clean", action="store_true", help="Remove build output first")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for release artifacts",
    )
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    pyinstaller_work = ROOT / "build" / "summon-pyinstaller"
    pyinstaller_dist = ROOT / "dist" / "pyinstaller"

    if args.clean:
        for path in (output_dir, pyinstaller_work, pyinstaller_dist):
            shutil.rmtree(path, ignore_errors=True)

    output_dir.mkdir(parents=True, exist_ok=True)

    binary_base = "grimoire-summon"
    binary_name = binary_base
    if platform.system().lower() == "windows":
        binary_name += ".exe"

    pyinstaller_args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconfirm",
        "--clean",
        "--name",
        binary_base,
        "--distpath",
        str(pyinstaller_dist),
        "--workpath",
        str(pyinstaller_work),
        "--specpath",
        str(pyinstaller_work),
        "--collect-all",
        "dearpygui",
    ]

    # Bundle the resources/ folder so the runtime icon (and any future assets)
    # is accessible from the frozen binary via the path summon.py searches.
    # PyInstaller's --add-data separator is ':' on Linux/macOS and ';' on Windows.
    resources_dir = ROOT / "resources"
    if resources_dir.is_dir():
        sep = ";" if platform.system().lower() == "windows" else ":"
        pyinstaller_args += ["--add-data", f"{resources_dir}{sep}resources"]

    templates_dir = ROOT / "rites" / "templates"
    if templates_dir.is_dir():
        sep = ";" if platform.system().lower() == "windows" else ":"
        pyinstaller_args += ["--add-data", f"{templates_dir}{sep}rites/templates"]

    # Platform-native executable icon (Windows .exe icon / macOS .app icon).
    # Only used if a native-format file exists alongside the PNGs; we don't
    # auto-convert to keep the build dependency surface tiny.
    system = platform.system().lower()
    if system == "windows":
        icon_path = resources_dir / "arcana_icon.ico"
        if icon_path.is_file():
            pyinstaller_args += ["--icon", str(icon_path)]
    elif system == "darwin":
        icon_path = resources_dir / "arcana_icon.icns"
        if icon_path.is_file():
            pyinstaller_args += ["--icon", str(icon_path)]

    pyinstaller_args.append(str(ROOT / "rites" / "summon.py"))

    try:
        run(pyinstaller_args)
    except subprocess.CalledProcessError as exc:
        print()
        print(f"[ERROR] PyInstaller failed with exit code {exc.returncode}.")
        print("        Install or repair PyInstaller, then re-run this rite.")
        return 1

    binary = pyinstaller_dist / binary_name
    if not binary.is_file():
        print(f"[ERROR] PyInstaller did not produce expected binary: {binary}")
        return 1

    os.chmod(binary, os.stat(binary).st_mode | 0o755)

    asset_name = f"{binary_base}-{platform_id()}"
    archive = archive_file(binary, output_dir, asset_name)
    checksum = output_dir / f"{archive.name}.sha256"
    checksum.write_text(f"{sha256_file(archive)}  {archive.name}\n", encoding="utf-8")

    print()
    print(f"Built:    {binary}")
    print(f"Archive:  {archive}")
    print(f"Checksum: {checksum}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
