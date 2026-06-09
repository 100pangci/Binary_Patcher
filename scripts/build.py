from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
BUILD = ROOT / "build"
RELEASES = ROOT / "Releases"


def run(command: list[str]) -> None:
    print(f"[RUN] {' '.join(command)}")
    subprocess.run(command, check=True, cwd=ROOT)


def clean() -> None:
    for path in (BUILD, RELEASES):
        if path.exists():
            shutil.rmtree(path)

    for spec_file in ROOT.glob("*.spec"):
        spec_file.unlink()


def build_executable(script_path: Path, exe_name: str) -> Path:
    RELEASES.mkdir(parents=True, exist_ok=True)
    run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--onefile",
            "--distpath",
            str(RELEASES),
            "--workpath",
            str(BUILD),
            "--name",
            exe_name,
            str(script_path),
        ]
    )
    return RELEASES / f"{exe_name}.exe"


def main() -> None:
    clean()
    build_executable(SRC_DIR / "binary_patcher.py", "binary_patcher")
    build_executable(SRC_DIR / "apply_patch.py", "apply_patch")
    print("\nBuild completed. Output directory:")
    print(f"- Releases: {RELEASES}")


if __name__ == "__main__":
    main()
