# CloudBase: persist quota and stats on bazi-api

Your env: `zy-feng-d3glt5d93b1a9f08e`
Service: `bazi-api`
Bucket (auto): `7a79-zy-feng-d3glt5d93b1a9f08e-1437107927`

Current status (checked via CloudBase MCP): `VolumesConf` is **empty** on `bazi-api`.
Without COS mount, every redeploy or container restart wipes:

- `/mnt/data/quota.db` (free AI usage, license keys, redeemed credits)
- `/mnt/data/usage_stats.db` (cumulative visitor count)

Symptoms:

- Free AI resets to 15/15 after refresh or redeploy
- Redeemed license keys disappear or show "key not found"

Note: a normal page refresh does **not** reset device id (`localStorage bazi_visitor_id_v1`).
Data loss happens when the backend container is recreated without persistent storage.

## Open the right page

1. Open: https://tcb.cloud.tencent.com/dev?envId=zy-feng-d3glt5d93b1a9f08e#/run
2. Click service **bazi-api** (not bazi-rag).
3. Find **存储挂载** (Storage mount) under service configuration.

If you do not see **存储挂载**:

- Confirm service type is **容器型** (container).
- Try **服务配置** -> **存储挂载**.
- Try **资源连接** -> **连接管理** first.

## Enable COS mount (recommended values)

| Field | Value |
|-------|--------|
| Storage type | 对象存储 (COS) |
| Bucket | 云开发对象存储 (auto-filled) |
| COS path (SrcPath) | `data` |
| Instance mount path (DstPath) | `/mnt` |
| Read/write | Read/write |

Save. Then **publish a new version** or restart instances so pods pick up the mount.

Files on COS after mount:

- `data/data/quota.db`
- `data/data/usage_stats.db`
- `data/data/.bazi_persist_marker` (health marker)

## Environment variables

Dockerfile defaults (also set in deploy EnvParams):

```
BAZI_QUOTA_DB_PATH=/mnt/data/quota.db
BAZI_STATS_DB_PATH=/mnt/data/usage_stats.db
```

## Verify after mount + redeploy

1. Call: `GET /api/v1/quota/persistence`
   - `likelyPersistent` should be `true`
   - `warning` should be null
2. Use a few AI calls (free count drops).
3. Redeploy `bazi-api` again.
4. Free count and license balance should **not** reset.

## Recover lost license keys

Old keys stored in a wiped container DB cannot be restored.
Use admin console `/#/admin` to generate new keys; users redeem again.

## Reference

https://docs.cloudbase.net/run/deploy/configuring/storage/cos
