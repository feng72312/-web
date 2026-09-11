"""Shared SSH helpers for ThinkStation deploy scripts."""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    import paramiko
except ImportError:
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko", "-q"])
    import paramiko


SKILL_ROOT = Path(__file__).resolve().parents[1]
CREDENTIALS_FILE = SKILL_ROOT / "credentials.env"


def load_credentials() -> dict[str, str]:
    if not CREDENTIALS_FILE.exists():
        example = SKILL_ROOT / "credentials.example.env"
        raise FileNotFoundError(
            f"Missing {CREDENTIALS_FILE}. Copy {example} to credentials.env and set values."
        )

    creds: dict[str, str] = {}
    for line in CREDENTIALS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        creds[key.strip()] = value.strip()
    return creds


def connect(timeout: int = 15) -> paramiko.SSHClient:
    creds = load_credentials()
    host = creds.get("THINKSTATION_HOST", "")
    user = creds.get("THINKSTATION_USER", "")
    password = creds.get("THINKSTATION_PASSWORD", "")
    port = int(creds.get("THINKSTATION_PORT", "22"))

    if not host or not user or not password:
        raise ValueError("THINKSTATION_HOST, THINKSTATION_USER, THINKSTATION_PASSWORD are required.")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=user, password=password, timeout=timeout)
    return client


def run_remote(command: str, timeout: int = 120) -> tuple[int, str, str]:
    client = connect()
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        code = stdout.channel.recv_exit_status()
        return code, out, err
    finally:
        client.close()


def sftp_upload(local_path: str | Path, remote_path: str) -> None:
    local_path = Path(local_path)
    if not local_path.exists():
        raise FileNotFoundError(f"Local path not found: {local_path}")

    client = connect()
    try:
        sftp = client.open_sftp()
        try:
            if local_path.is_dir():
                _upload_dir(sftp, local_path, remote_path)
            else:
                _ensure_remote_dir(sftp, os.path.dirname(remote_path.replace("\\", "/")))
                sftp.put(str(local_path), remote_path)
        finally:
            sftp.close()
    finally:
        client.close()


def _ensure_remote_dir(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    if not remote_dir or remote_dir == "/":
        return
    parts = remote_dir.strip("/").split("/")
    current = ""
    for part in parts:
        current += f"/{part}"
        try:
            sftp.stat(current)
        except OSError:
            sftp.mkdir(current)


def _upload_dir(sftp: paramiko.SFTPClient, local_dir: Path, remote_dir: str) -> None:
    _ensure_remote_dir(sftp, remote_dir)
    for item in local_dir.rglob("*"):
        rel = item.relative_to(local_dir).as_posix()
        remote_item = f"{remote_dir.rstrip('/')}/{rel}"
        if item.is_dir():
            _ensure_remote_dir(sftp, remote_item)
        else:
            _ensure_remote_dir(sftp, os.path.dirname(remote_item))
            sftp.put(str(item), remote_item)
