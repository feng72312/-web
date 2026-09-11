---
name: bazi-deploy
description: >-
  Deploy the Bazi web platform to Tencent CloudBase: sync backend to bazi-deploy,
  build frontend with VITE_API_BASE, publish static hosting, deploy CloudRun
  container bazi-api via MCP, poll status, and smoke-test. Use when the user asks
  to deploy, publish, release, or update the online site, frontend, backend,
  bazi-api, CloudBase, or 云托管/静态托管.
---

# Bazi CloudBase Deploy

Deploy `code/` to CloudBase: React static hosting + FastAPI CloudRun (`bazi-api`).

Also load `d:\ZY\.agents\skills\cloudbase\references\cloudrun-development\SKILL.md` for generic CloudRun MCP rules.

Constants and URLs: [reference.md](reference.md)

## Prerequisites

- CloudBase MCP server `user-cloudbase` enabled and authenticated
- Read MCP tool schemas under `mcps/user-cloudbase/tools/` before `CallMcpTool`
- Secrets in `code/backend/.env` (never commit; never paste keys into chat output)

## Deploy checklist

Copy and track:

```
- [ ] 1. Review git diff (backend + frontend)
- [ ] 2. Sync backend to bazi-deploy
- [ ] 3. Build frontend with VITE_API_BASE
- [ ] 4. Deploy backend (CloudRun) with merged EnvParams, Port 8080
- [ ] 5. Upload frontend dist to static hosting
- [ ] 6. Poll until latest deploy status=normal, FlowRatio=100
- [ ] 7. Smoke-test API + tell user to Ctrl+F5
```

## Step 1: Review changes

```powershell
git -C d:\ZY\code status --short
git -C d:\ZY\code diff --stat
```

Deploy backend if `code/backend/**` changed. Deploy frontend if `code/frontend/**` changed. Full release = both.

## Step 2: Sync backend

MCP deploy path must be under user home:

```powershell
powershell -ExecutionPolicy Bypass -File d:\ZY\.cursor\skills\bazi-deploy\scripts\sync-backend.ps1
```

Copies `app/`, `Dockerfile`, `requirements.txt` to `%USERPROFILE%\bazi-deploy\backend`.

## Step 3: Build frontend

```powershell
powershell -ExecutionPolicy Bypass -File d:\ZY\.cursor\skills\bazi-deploy\scripts\build-frontend.ps1
```

Uses production `VITE_API_BASE` from [reference.md](reference.md). Output: `d:\ZY\code\frontend\dist`.

## Step 4: Deploy backend (MCP)

1. `queryCloudRun(action="detail", detailServerName="bazi-api")` -- read current `ServerConfig.EnvParams`
2. Build merged JSON (keep existing keys; add new keys from `.env`):

```powershell
powershell -ExecutionPolicy Bypass -File d:\ZY\.cursor\skills\bazi-deploy\scripts\build-env-params.ps1
```

3. `manageCloudRun`:

```json
{
  "server": "user-cloudbase",
  "toolName": "manageCloudRun",
  "arguments": {
    "action": "deploy",
    "serverName": "bazi-api",
    "serverType": "container",
    "targetPath": "C:\\Users\\liqingfeng\\bazi-deploy\\backend",
    "serverConfig": {
      "Port": 8080,
      "EnvParams": "<JSON string from build-env-params.ps1>"
    }
  }
}
```

**Critical:** `EnvParams` replaces the whole object. Always include Codex + DeepSeek keys from `.env` or prior cloud config.

## Step 5: Upload frontend (MCP)

```json
{
  "server": "user-cloudbase",
  "toolName": "manageHosting",
  "arguments": {
    "action": "upload",
    "localPath": "d:\\ZY\\code\\frontend\\dist",
    "cloudPath": "/",
    "ignore": ["**/*.map", "**/.DS_Store"]
  }
}
```

Backend and frontend deploys may run in parallel after steps 2-3 complete.

## Step 6: Poll deploy status

Repeat `queryCloudRun(action="detail", detailServerName="bazi-api")` until:

- `latestDeploy.status` is `normal`
- `latestDeploy.flowRatio` is `100` (or `HasTraffic` true)
- `OnlineVersionInfos` lists the new version

If status is `deploy_failed`, check console deploy logs (Readiness/Liveness on port 8080). See pitfalls in [reference.md](reference.md).

Do not use arbitrary `sleep`; poll MCP or curl until ready.

## Step 7: Smoke test

```powershell
curl.exe -s "https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com/health"
curl.exe -s "https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com/api/v1/chat/status"
curl.exe -s "https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com/api/v1/stats/overview"
```

Report to user:

- Frontend: https://zy-feng-d3glt5d93b1a9f08e-1437107927.tcloudbaseapp.com/
- Backend deploy id / version from `queryCloudRun`
- Remind: **Ctrl+F5** and re-connect AI after backend chat changes

## Scope shortcuts

| User request | Actions |
|--------------|---------|
| 只部署前端 | Steps 3, 5, 7 (frontend URL only) |
| 只部署后端 | Steps 2, 4, 6, 7 |
| 全量发布 | All steps |

## Backend-only constraints

- Codex bridge: lazy start in `service.py` startup; never block lifespan
- Cloud agents: cache handles in memory; no `agent.close()` after create
- `BAZI_RAG_PROVIDER=stub` online unless RAG service is deployed separately

## When not to use this skill

- Local dev (`start-all.bat`, uvicorn, vite dev) -- not a CloudBase deploy
- CloudBase env/MCP setup -- use `cloudbase` skill under `.agents/skills/cloudbase`
- Git commit / PR -- separate workflow
