# ThinkStation 本机部署

本目录用于将紫云命理平台部署在 `user-ThinkStation-PX`：

- `bazi-rag.service`：本机 GPU RAG，监听 `127.0.0.1:8100`
- `bazi-backend.service`：FastAPI，监听 `127.0.0.1:8002`
- `bazi-local-web`：Nginx 静态站与 `/api` 反向代理，监听 `0.0.0.0:8080`
- `bazi-tunnel.service`：Cloudflare Quick Tunnel，将 `8080` 临时映射到公网 HTTPS 地址

前端发布：

```bash
cd /home/feng/liqingfeng/ZY/code/frontend
npm run build
cd ../deploy/local
docker compose up -d
```

用户服务：

```bash
mkdir -p ~/.config/systemd/user
ln -sfn /home/feng/liqingfeng/ZY/code/deploy/local/systemd/bazi-rag.service ~/.config/systemd/user/bazi-rag.service
ln -sfn /home/feng/liqingfeng/ZY/code/deploy/local/systemd/bazi-backend.service ~/.config/systemd/user/bazi-backend.service
systemctl --user daemon-reload
systemctl --user enable --now bazi-rag.service bazi-backend.service
ln -sfn /home/feng/liqingfeng/ZY/code/deploy/local/systemd/bazi-tunnel.service ~/.config/systemd/user/bazi-tunnel.service
systemctl --user daemon-reload
systemctl --user enable --now bazi-tunnel.service
```

检查：

```bash
systemctl --user status bazi-rag.service bazi-backend.service
docker compose ps
curl http://127.0.0.1:8080/healthz
curl http://127.0.0.1:8080/api/v1/health
journalctl --user -u bazi-tunnel.service -n 30 --no-pager
```

局域网访问地址：`http://172.16.7.144:8080`

Quick Tunnel 的公网地址会写入 `bazi-tunnel.service` 日志。该地址在服务重启后可能变化；正式域名应改用命名隧道。
