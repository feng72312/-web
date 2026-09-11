#!/usr/bin/env python3
"""Upload files to ThinkStation THINKSTATION_DEPLOY_DIR."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _ssh_common import load_credentials, run_remote, sftp_upload  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", required=True, help="Local file or directory to upload")
    parser.add_argument("--remote-subpath", default="", help="Subpath under deploy dir")
    args = parser.parse_args()

    creds = load_credentials()
    deploy_dir = creds.get("THINKSTATION_DEPLOY_DIR", "/home/feng/deploy")
    local_path = Path(args.local).resolve()
    remote_path = deploy_dir.rstrip("/")
    if args.remote_subpath:
        remote_path = f"{remote_path}/{args.remote_subpath.strip('/')}"

    run_remote(f"mkdir -p {deploy_dir}")
    sftp_upload(local_path, remote_path)
    print(f"Uploaded {local_path} -> {remote_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
