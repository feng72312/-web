# ThinkStation PX server reference

## Connection

| Key | Value |
|-----|-------|
| Host | 172.16.7.144 |
| User | feng |
| Port | 22 |
| Hostname | user-ThinkStation-PX |
| OS | Ubuntu 24.04.4 LTS |
| Kernel | 6.17.0-1020-oem x86_64 |

Credentials live in `credentials.env` (copy from `credentials.example.env`). Never commit passwords to git.

## Hardware (verified)

| Resource | Spec |
|----------|------|
| CPU | Intel Xeon Silver 4410T, 10 cores / 20 threads, up to 4.0 GHz |
| RAM | 125 GiB |
| Disk | 3.7 TB LVM (`/dev/mapper/ubuntu--vg-ubuntu--lv`), ~16% used at last check |
| GPU | NVIDIA GeForce RTX 4090 |

## Paths

| Path | Purpose |
|------|---------|
| `/home/feng` | User home |
| `/home/feng/桌面` | Desktop (Chinese locale) |
| `/home/feng/deploy` | Default remote deploy root (`THINKSTATION_DEPLOY_DIR`) |

## Known issues

- Login banner may show **reboot required** after kernel/driver updates.
- `nvidia-smi` may report `Driver/library version mismatch` until reboot: `sudo reboot`.
- Agent runs from Windows; use `py -3` and paramiko scripts in this skill (OpenSSH password prompts are not scriptable).

## Interactive SSH (manual)

```powershell
ssh feng@172.16.7.144
```

Requires same LAN or routed access to 172.16.0.0/16.
