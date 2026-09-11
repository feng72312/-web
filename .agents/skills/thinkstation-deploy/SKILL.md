---
name: thinkstation-deploy
description: >-
  Connect to the local ThinkStation PX Ubuntu server (172.16.7.144) over SSH,
  run remote commands, upload deploy artifacts, and check CPU/RAM/GPU health.
  Use when the user mentions ThinkStation, user-ThinkStation-PX, 172.16.7.144,
  feng server, local GPU server, RTX 4090 server, or deploying to the on-prem
  Ubuntu machine instead of CloudBase.
---

# ThinkStation Deploy

SSH workflow for **user-ThinkStation-PX** (`172.16.7.144`, user `feng`). Server specs and paths: [reference.md](reference.md).

## Prerequisites

- Windows agent host can reach `172.16.7.144:22` (same LAN / VPN).
- `credentials.env` exists in this skill folder (copy from `credentials.example.env`).
- Python 3 with `paramiko` (scripts auto-install on first run).

## Agent rules

1. **Always load this skill** when deploying or operating the ThinkStation server.
2. **Never paste passwords** into chat; read from `credentials.env` via scripts only.
3. **Prefer scripts** over ad-hoc SSH one-liners for consistency.
4. After driver/kernel changes, remind user to reboot if GPU checks fail.

## Quick commands

Skill root: `d:\ZY\.cursor\skills\thinkstation-deploy`

**Health / performance snapshot**

```powershell
py -3 d:\ZY\.cursor\skills\thinkstation-deploy\scripts\health-check.py
```

**Run arbitrary remote command**

```powershell
py -3 d:\ZY\.cursor\skills\thinkstation-deploy\scripts\ssh-exec.py "ls -lah /home/feng/deploy"
```

**Upload project artifacts to deploy dir**

```powershell
powershell -ExecutionPolicy Bypass -File d:\ZY\.cursor\skills\thinkstation-deploy\scripts\upload.ps1 -LocalPath "d:\ZY\code\backend"
```

Optional subpath under deploy root:

```powershell
powershell -ExecutionPolicy Bypass -File d:\ZY\.cursor\skills\thinkstation-deploy\scripts\upload.ps1 -LocalPath "d:\ZY\code\backend" -RemoteSubPath "bazi-api"
```

## Deploy checklist

Copy and track:

```
- [ ] 1. py -3 .../health-check.py (confirm host reachable, disk/GPU OK)
- [ ] 2. Build artifacts locally (frontend dist, Docker context, etc.)
- [ ] 3. upload.ps1 to THINKSTATION_DEPLOY_DIR (see credentials.env)
- [ ] 4. ssh-exec.py: install deps / docker compose up / systemd restart on server
- [ ] 5. ssh-exec.py: curl or port check smoke test
- [ ] 6. Report URL or service status to user
```

## Common remote operations

Create deploy directory:

```powershell
py -3 d:\ZY\.cursor\skills\thinkstation-deploy\scripts\ssh-exec.py "mkdir -p /home/feng/deploy && ls -lah /home/feng/deploy"
```

Docker (if installed on server):

```powershell
py -3 d:\ZY\.cursor\skills\thinkstation-deploy\scripts\ssh-exec.py "cd /home/feng/deploy && docker compose ps"
```

Reboot when GPU driver mismatch persists:

```powershell
py -3 d:\ZY\.cursor\skills\thinkstation-deploy\scripts\ssh-exec.py "sudo reboot"
```

Note: reboot disconnects SSH; wait ~1 min then re-run health-check.

## Script map

| Script | Purpose |
|--------|---------|
| `scripts/health-check.py` | CPU, RAM, disk, GPU, deploy dir listing |
| `scripts/ssh-exec.py` | Run one remote shell command |
| `scripts/upload.ps1` / `upload.py` | SFTP upload file or directory to deploy dir |
| `scripts/_ssh_common.py` | Shared credentials + SSH/SFTP helpers |

## Credentials setup

```powershell
Copy-Item d:\ZY\.cursor\skills\thinkstation-deploy\credentials.example.env `
  d:\ZY\.cursor\skills\thinkstation-deploy\credentials.env
# Edit credentials.env: THINKSTATION_HOST, USER, PASSWORD, DEPLOY_DIR
```

## When to use ThinkStation vs CloudBase

| Scenario | Target |
|----------|--------|
| Public Bazi site, CloudRun, static hosting | `bazi-deploy` skill + CloudBase MCP |
| Local GPU inference, heavy compute, private dev | This skill (ThinkStation) |

Both skills can coexist; pick based on user intent.
