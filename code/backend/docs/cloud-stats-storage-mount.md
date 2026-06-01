# CloudBase: persist usage stats on bazi-api

See **cloud-persistent-storage-mount.md** for full setup (quota + stats on one COS mount).

Your env: `zy-feng-d3glt5d93b1a9f08e`
Service: `bazi-api`
Bucket (auto): `7a79-zy-feng-d3glt5d93b1a9f08e-1437107927`

Current status (checked via CloudBase MCP): `VolumesConf` is **empty** on `bazi-api`, so redeploy always resets cumulative visitors and quota data.

## Open the right page

1. Open: https://tcb.cloud.tencent.com/dev?envId=zy-feng-d3glt5d93b1a9f08e#/run
2. Click service **bazi-api** (not bazi-rag).
3. In the service detail page, find the left menu or top tabs. The item name is **存储挂载** (Storage mount). It is **not** under version deploy only; it is under service configuration.

If you do not see **存储挂载**:

- Confirm service type is **容器型** (container). `bazi-api` is container.
- Try **服务配置** -> **存储挂载**.
- Try **资源连接** -> **连接管理** first (some accounts require a linked Tencent Cloud API key before mount is enabled).

## Enable COS mount (recommended values)

| Field | Value |
|-------|--------|
| Storage type | 对象存储 (COS) |
| Bucket | 云开发对象存储 (auto-filled) |
| COS path (SrcPath) | `data` |
| Instance mount path (DstPath) | `/mnt` |
| Read/write | Read/write |

Save. Then **publish a new version** (or restart instances) so running pods pick up the mount.

## Environment variable

Image default: `BAZI_STATS_DB_PATH=/mnt/data/usage_stats.db`
Also: `BAZI_QUOTA_DB_PATH=/mnt/data/quota.db`

Optional: add the same keys in CloudRun env vars (console **服务配置** -> **环境变量**) to override.

DB files on COS: under bucket prefix `data/data/`.

## Verify after deploy

1. Open site, wait for heartbeat (about 30s).
2. Note cumulative visitors and AI free count.
3. Redeploy `bazi-api` again.
4. Counts should **not** return to defaults.

Online count may still drop to 0 briefly after restart (in-memory); cumulative and quota should stay.

## Reference

https://docs.cloudbase.net/run/deploy/configuring/storage/cos
