"""Run classify -> reconcile -> RAG index build for 01八字命理 in correct order."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parents[2]


def _run(cmd: list[str], *, cwd: Path) -> int:
    print("$", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=str(cwd))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable, help="python executable for rag build")
    parser.add_argument("--no-reset", action="store_true")
    args = parser.parse_args()

    steps = [
        [sys.executable, str(SCRIPTS / "classify_01_sources.py")],
        [sys.executable, str(SCRIPTS / "reconcile_01_sources.py")],
        [
            args.python,
            str(ROOT / "code" / "rag" / "build_index.py"),
            "--category",
            "01",
        ],
    ]
    if args.no_reset:
        steps[-1].append("--no-reset")

    for cmd in steps:
        code = _run(cmd, cwd=SCRIPTS)
        if code != 0:
            print(f"failed: {' '.join(cmd)} (exit {code})")
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
