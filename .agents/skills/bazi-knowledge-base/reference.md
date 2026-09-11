# Bazi Knowledge Base Reference

## Architecture

```
数据库/八字/          source txt/doc files
       |
       v
code/rag/build_index.py   read -> chunk (400 chars, 80 overlap) -> embed
       |
       v
code/rag/data/chroma/     ChromaDB persistent store
       |
       v
code/rag/server.py        POST /search  (port 8100)
       |
       v
code/backend/             HttpRagProvider via BAZI_RAG_HTTP_URL
       |
       v
/api/v1/interpret         chart -> RAG query -> excerpts -> agent summary
```

## Key modules

| File | Purpose |
|------|---------|
| `code/rag/config.py` | Source dir, model, chunk size, allowed suffixes |
| `code/rag/doc_reader.py` | txt encoding fallback; doc via Word COM batch |
| `code/rag/chunker.py` | Paragraph-aware text splitting |
| `code/rag/build_index.py` | Full rebuild (default) or `--no-reset` append |
| `code/rag/server.py` | FastAPI search + health endpoints |

## RAG query shape (backend)

`InterpretService.build_query()` sends chart-aware Chinese queries, e.g. day master, month pillar, ten gods, pattern/useful god terms. Not limited to a single book.

## Index size estimates (measured baseline)

Baseline with ~10 MB source (107 files): ~5124 chunks, ~62 MB index.

Rough scaling:

- ~12 KB per chunk in Chroma
- ~150k extracted chars per MB of source file (varies by doc density)
- Adding ~4 GB of similar `.doc` text: on the order of **20-30 GB** index, not 4 GB

Embedding model cache: `%USERPROFILE%\.cache\huggingface\hub\models--BAAI--bge-small-zh-v1.5\`

## Start scripts

| Script | Action |
|--------|--------|
| `code/rag/build-index.bat` | Rebuild index only |
| `code/rag/start-rag.bat` | Install deps, build if missing, start server |
| `code/start-all.bat` | RAG + backend + frontend |
