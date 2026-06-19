"""Decrypt helpers for knowledge source pipelines (decrypt skill)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SKILL_DECRYPT_SCRIPT = Path(
    r"C:\Users\liqingfeng\.cursor\skills\decrypt\scripts\file_decrypt.py"
)
PROJECT_DECRYPT_SCRIPT = Path(__file__).resolve().parents[3] / "file_decrypt.py"


def resolve_decrypt_script() -> Path | None:
    if SKILL_DECRYPT_SCRIPT.is_file():
        return SKILL_DECRYPT_SCRIPT
    if PROJECT_DECRYPT_SCRIPT.is_file():
        return PROJECT_DECRYPT_SCRIPT
    return None


def run_decrypt(paths: list[Path]) -> int:
    script = resolve_decrypt_script()
    if script is None:
        print("[error] file_decrypt.py not found (decrypt skill)")
        return 1
    cmd = [sys.executable, str(script), *[str(p) for p in paths]]
    print(f"[decrypt] running: {script}")
    completed = subprocess.run(cmd, check=False)
    return int(completed.returncode or 0)
