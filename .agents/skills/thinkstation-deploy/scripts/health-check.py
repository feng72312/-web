#!/usr/bin/env python3
"""Quick ThinkStation server health and performance snapshot."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _ssh_common import load_credentials, run_remote  # noqa: E402


CHECK_SCRIPT = r"""
export LANG=C.UTF-8
echo '=== HOST ==='
hostname
echo
echo '=== UPTIME / LOAD ==='
uptime
echo
echo '=== CPU ==='
lscpu | egrep 'Model name|CPU\(s\)|Thread|Core|Socket|MHz'
echo
echo '=== MEMORY ==='
free -h
echo
echo '=== DISK / ==='
df -h /
echo
echo '=== GPU ==='
nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader 2>&1 | head -3
echo
echo '=== DEPLOY DIR ==='
DEPLOY="${THINKSTATION_DEPLOY_DIR:-/home/feng/deploy}"
ls -lah "$DEPLOY" 2>/dev/null || echo "(not created yet)"
"""


def main() -> int:
    creds = load_credentials()
    deploy_dir = creds.get("THINKSTATION_DEPLOY_DIR", "/home/feng/deploy")
    command = f"export THINKSTATION_DEPLOY_DIR={deploy_dir}; {CHECK_SCRIPT}"
    code, out, err = run_remote(command)
    print(out)
    if err.strip():
        print(err, file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
