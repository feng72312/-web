---
name: bazi-knowledge-base
description: >-
  Add documents to the local Bazi classics RAG knowledge base, rebuild the
  Chroma vector index, and restart or verify the search service. Use when the
  user asks to add, ingest, update, or rebuild the knowledge base, RAG index,
  or 典籍/八字资料库 under 数据库/八字.
---

# Bazi Knowledge Base

Local semantic RAG for the Bazi web app. Source docs live on disk; search uses a Chroma index and `BAAI/bge-small-zh-v1.5` embeddings.

## Paths

| Role | Path |
|------|------|
| Source documents | `数据库/` (10 category subfolders: `01八字命理` ... `10杂占方术`) |
| RAG code | `code/rag/` |
| Vector index | `code/rag/data/chroma/` (one Chroma collection per category) |
| Build report | `code/rag/data/index_report.json` |
| Migrate script | `code/rag/migrate_library.py` |
| Backend RAG config | `code/backend/.env` (`BAZI_RAG_HTTP_URL=http://127.0.0.1:8100`) |
| Search API | `http://127.0.0.1:8100` |

## Supported formats

- Include: `.txt`, `.doc`, `.docx`
- Exclude: `.pdf`, anything under `ocr/`

Put new files anywhere under `数据库/八字/`. Rebuild rescans the whole tree.

## Add-documents workflow

Copy this checklist and track progress:

```
- [ ] 1. Confirm files are txt/doc/docx (not pdf)
- [ ] 2. Copy files into 数据库/八字/ (or a subfolder)
- [ ] 3. Stop RAG service on port 8100 (index rebuild locks chroma)
- [ ] 4. Rebuild index with Python 3.10
- [ ] 5. Read index_report.json and report stats to user
- [ ] 6. Restart RAG service
- [ ] 7. Verify /health and one /search query
```

### Step 1-2: Add source files

Put new files under `d:\ZY\数据库\{01..10 category}/`. Pending intake: `未入库古籍/1/` then run `migrate_library.py`.

### Step 3: Stop RAG before rebuild

Chroma files are locked while the server runs. Stop the process on port 8100 first.

PowerShell:

```powershell
Get-NetTCPConnection -LocalPort 8100 -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
```

### Step 4: Rebuild index

Always use **Python 3.10** (`py -3.10`). Python 3.8 breaks chromadb.

```powershell
cd d:\ZY\code\rag
py -3.10 migrate_library.py
py -3.10 -m pip install -r requirements.txt -q
py -3.10 build_index.py
```

Or double-click `code/rag/build-index.bat` (add migrate step manually if needed).

Source root is `数据库/` with 10 category folders. Each folder maps to one Chroma collection (`kb_01_bazi` ...).

### Search by category

```powershell
py -3.10 -c "import httpx; print(httpx.post('http://127.0.0.1:8100/search', json={'query':'用神','topK':3,'category':'01八字命理'}).json())"
```

Backend default category: `BAZI_RAG_DEFAULT_CATEGORY=01八字命理` for `/interpret`.

### Step 5: Report results

Read `code/rag/data/index_report.json` and summarize:

- `files_total`, `chunks_total`, `built_at`
- Per-file `status`: flag any `error` or `empty` entries
- Index size: sum file sizes under `code/rag/data/chroma/`

### Step 6: Restart RAG

```powershell
cd d:\ZY\code\rag
py -3.10 server.py
```

Or `code/rag/start-rag.bat` (skips rebuild if index already exists).

### Step 7: Verify

```powershell
py -3.10 -c "import httpx; print(httpx.get('http://127.0.0.1:8100/health', timeout=30).json())"
py -3.10 -c "import httpx, json; r=httpx.post('http://127.0.0.1:8100/search', json={'query':'日主甲木 用神 格局', 'topK': 3}, timeout=30); print(len(r.json()), 'hits')"
```

Health should show `status: ok` and `chunks` matching the report.

## Constraints

- **Python 3.10** required for `code/rag/`
- **`.doc` on Windows** needs Microsoft Word or WPS (COM via `win32com`)
- **Embedding model** (`BAAI/bge-small-zh-v1.5`, ~130 MB) is downloaded once; it does not grow with new docs
- **Index disk usage** grows with chunk count (~12 KB/chunk in current setup)

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `PermissionError` on `chroma/data_level0.bin` | Stop RAG on port 8100, rebuild |
| All `.doc` files skipped | Word/WPS not installed or COM blocked; test one file with `doc_reader.read_doc_win32` |
| `TypeError: 'type' object is not subscriptable` in chromadb | Wrong Python version; use `py -3.10` |
| Backend still returns stub excerpts | Confirm `code/backend/.env` has `BAZI_RAG_PROVIDER=http` and RAG is running |
| Search returns irrelevant hits | Normal for broad queries; interpret layer builds chart-specific queries in `interpret/service.py` |

## Optional: ingest-only subfolder

To index one folder without changing defaults, pass `--source`:

```powershell
py -3.10 build_index.py --source "d:\ZY\数据库\八字\2.蔡昔琼"
```

Default source is all of `数据库/八字/` (see `code/rag/config.py`).

## Do not

- Ingest `.pdf` unless OCR pipeline is added separately
- Commit API keys from `code/backend/.env`
- Use simulated or fake document content

## Additional reference

See [reference.md](reference.md) for architecture and size estimates.
