#!/usr/bin/env python3
"""Run a shell command on the ThinkStation server over SSH."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _ssh_common import run_remote  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: py -3 scripts/ssh-exec.py \"remote command\"")
        return 1

    command = sys.argv[1]
    code, out, err = run_remote(command)
    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    if err:
        print(err, end="" if err.endswith("\n") else "\n", file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
