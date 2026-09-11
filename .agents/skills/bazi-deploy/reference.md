# Bazi CloudBase Deploy Reference

## Environment

| Key | Value |
|-----|-------|
| CloudBase envId | `zy-feng-d3glt5d93b1a9f08e` |
| Region | Shanghai |
| MCP server | `user-cloudbase` |

## Services

| Role | Name / URL |
|------|------------|
| Frontend (static hosting) | https://zy-feng-d3glt5d93b1a9f08e-1437107927.tcloudbaseapp.com/ |
| Backend (CloudRun container) | https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com |
| CloudRun service name | `bazi-api` |
| Backend API prefix | `/api/v1` |
| Container port | `8080` |

## Console

- CloudRun: https://tcb.cloud.tencent.com/dev?envId=zy-feng-d3glt5d93b1a9f08e#/platform-run/service/detail?serverName=bazi-api
- Static hosting: https://tcb.cloud.tencent.com/dev?envId=zy-feng-d3glt5d93b1a9f08e#/static-hosting

## Local paths (Windows)

| Role | Path |
|------|------|
| Source backend | `d:\ZY\code\backend` |
| Source frontend | `d:\ZY\code\frontend` |
| MCP deploy backend copy | `C:\Users\liqingfeng\bazi-deploy\backend` |
| Frontend build output | `d:\ZY\code\frontend\dist` |
| Local env file (secrets) | `d:\ZY\code\backend\.env` |

CloudBase MCP `manageCloudRun(deploy)` requires `targetPath` under the user home directory. Do not point deploy at `d:\ZY\code\backend` directly.

## EnvParams keys (backend)

Merge all keys on every deploy. Read current values from `queryCloudRun(action="detail")` -> `ServerConfig.EnvParams`, then overlay any new keys from `code/backend/.env`.

| Key | Purpose |
|-----|---------|
| `BAZI_DEBUG` | `false` in production |
| `BAZI_RAG_PROVIDER` | `stub` online (local RAG not deployed) |
| `BAZI_CURSOR_API_KEY` | Cursor SDK |
| `BAZI_CURSOR_MODEL` | e.g. `composer-2.5` |
| `BAZI_CURSOR_RUNTIME` | `cloud` on CloudRun |
| `BAZI_DEEPSEEK_API_KEY` | DeepSeek API |
| `BAZI_DEEPSEEK_BASE_URL` | default `https://api.deepseek.com` |

Never write API keys into skill files or git.

## Frontend build

```powershell
$env:VITE_API_BASE = "https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com/api/v1"
npm run build
```

Output: `code/frontend/dist/`

## Post-deploy smoke tests

```powershell
curl.exe -s "https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com/health"
curl.exe -s "https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com/api/v1/chat/status"
curl.exe -s "https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com/api/v1/stats/overview"
```

## Known pitfalls

1. **Partial EnvParams overwrites secrets** -- always merge with existing cloud config.
2. **Port mismatch** -- CloudRun `Port` must be `8080`; Dockerfile listens on `8080`.
3. **Health check fails** -- do not block FastAPI lifespan on Cursor bridge; bridge starts lazily on first chat.
4. **Cloud agent chat** -- do not `agent.close()` after create; cache `AsyncAgent` in memory; cloud resume is unreliable.
5. **Failed deploy with no online version** -- gateway returns `SERVICE_VERSION_NOT_FOUND`; fix Dockerfile/startup, redeploy, poll until `OnlineVersionInfos` has traffic.
6. **Frontend cache** -- tell user to Ctrl+F5 after deploy.
7. **Stats SQLite** -- `data/usage_stats.db` in container is ephemeral unless a volume is added.

## Dockerfile rules (backend)

- Base: `python:3.11-slim`
- Use `uvicorn` without `[standard]` extras
- CMD: `["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--loop", "asyncio"]`
- Do not use `sh -c` with `${PORT}` unless you also set `ENV PORT=8080`
