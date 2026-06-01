# 大六壬上线检查清单

## 环境变量

在 CloudBase / 本机 `code/backend/.env` 增加:

```
BAZI_LIUREN_RAG_CATEGORY=05大六壬
```

确认 RAG 服务可检索 `kb_05_liuren` 集合.

## 后端

1. 部署包含 `app/api/liuren_router.py` 的镜像或函数包.
2. 启动后验证:
   - `GET /api/v1/liuren/methods`
   - `POST /api/v1/liuren/chart` (JSON 占时)
3. 知识图谱: 将 `code/knowledge/data/graph/liuren_nodes.jsonl` 随 knowledge 数据目录挂载.

生成/更新节点:

```
py code/knowledge/scripts/seed_liuren_nodes.py
py code/knowledge/scripts/extract_liuren_from_zhinan.py --merge
```

## 前端

1. 构建并发布含 Tab `05` 大六壬 的静态资源.
2. `VITE_API_BASE` 指向新后端.

## 手工验收

1. Tab 05 起课 (正六壬+金口诀), 见四课三传天地盘.
2. 检索知识库 + AI 解读.
3. 奇门 Tab 勾选「AI 参考八字」前先在八字 Tab 排盘.
