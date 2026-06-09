from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
BUILD = ROOT / "build"
RELEASES = ROOT / "Releases"
BIN_DIR = ROOT / "bin"
PACKAGE_DIR = RELEASES / "binary_patcher_toolkit"
HDIFFPATCH_REPO_API = "https://api.github.com/repos/sisong/HDiffPatch/releases/latest"
BINARY_DESTINATION = "bin"


def run(command: list[str]) -> None:
    print(f"[RUN] {' '.join(command)}")
    subprocess.run(command, check=True, cwd=ROOT)


def make_relative_display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def clean() -> None:
    for path in (BUILD, RELEASES):
        if path.exists():
            shutil.rmtree(path)

def ensure_hdiffpatch_binaries() -> list[Path]:
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(HDIFFPATCH_REPO_API) as response:
        release = json.load(response)

    asset = next(
        item for item in release["assets"] if item["name"].endswith("windows64.zip")
    )

    print(f"[INFO] Downloading HDiffPatch {release['tag_name']} from {asset['name']}")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        archive_path = temp_path / asset["name"]
        with urllib.request.urlopen(asset["browser_download_url"]) as response:
            archive_path.write_bytes(response.read())

        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(temp_path / "extract")

        extracted_root = temp_path / "extract" / "windows64"
        binaries = [extracted_root / "hdiffz.exe", extracted_root / "hpatchz.exe"]
        for binary in binaries:
            target = BIN_DIR / binary.name
            shutil.copy2(binary, target)
            print(f"[INFO] Prepared {target}")

    return [BIN_DIR / "hdiffz.exe", BIN_DIR / "hpatchz.exe"]


def build_executable(script_path: Path, exe_name: str) -> Path:
    BUILD.mkdir(parents=True, exist_ok=True)
    RELEASES.mkdir(parents=True, exist_ok=True)
    include_data_args = []
    for binary in ensure_hdiffpatch_binaries():
        include_data_args.append(
            f"--include-data-files={binary}={BINARY_DESTINATION}/{binary.name}"
        )

    command = [
        sys.executable,
        "-m",
        "nuitka",
        "--onefile",
        "--assume-yes-for-downloads",
        "--remove-output",
        f"--output-dir={BUILD}",
        f"--output-filename={exe_name}.exe",
        *include_data_args,
        str(script_path),
    ]

    if os.name == "nt":
        command.insert(5, "--windows-console-mode=force")

    run(
        command
    )

    built_executable = BUILD / f"{exe_name}.exe"
    release_executable = RELEASES / built_executable.name
    shutil.copy2(built_executable, release_executable)
    return release_executable


def create_release_package(executables: list[Path]) -> Path:
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    for executable in executables:
        shutil.copy2(executable, PACKAGE_DIR / executable.name)

    archive_base = RELEASES / "binary_patcher_toolkit"
    archive_path = shutil.make_archive(str(archive_base), "zip", root_dir=PACKAGE_DIR)
    shutil.rmtree(PACKAGE_DIR)
    return Path(archive_path)


def main() -> None:
    clean()
    executables = [
        build_executable(SRC_DIR / "binary_patcher.py", "binary_patcher"),
        build_executable(SRC_DIR / "apply_patch.py", "apply_patch"),
        build_executable(SRC_DIR / "rollback_patch.py", "rollback_patch"),
    ]
    archive_path = create_release_package(executables)

    if BUILD.exists():
        shutil.rmtree(BUILD)

    print("\nBuild completed. Output directory:")
    print(f"- Releases: {make_relative_display_path(RELEASES)}")
    print(f"- Toolkit zip: {make_relative_display_path(archive_path)}")


if __name__ == "__main__":
    main()
