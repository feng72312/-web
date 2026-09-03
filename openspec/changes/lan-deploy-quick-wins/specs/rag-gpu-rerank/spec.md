## ADDED Requirements

### Requirement: Compute device is configurable and defaults to GPU when available
The RAG service SHALL read `RAG_DEVICE` (`auto` | `cuda` | `cpu`, default `auto`) and use it for both the sentence-transformer embedding function and the cross-encoder reranker. With `auto`, it SHALL select `cuda` when `torch.cuda.is_available()` is true and `cpu` otherwise.

#### Scenario: Auto on a CUDA host
- **WHEN** the service starts with `RAG_DEVICE` unset on the RTX 4090 server with a CUDA torch build installed
- **THEN** `/health` reports `"device": "cuda"` and `nvidia-smi` shows a python process from `rag/.venv` holding GPU memory after the first `/search`

#### Scenario: Forced CPU
- **WHEN** the service starts with `RAG_DEVICE=cpu`
- **THEN** `/health` reports `"device": "cpu"` and no GPU memory is allocated by the service

### Requirement: Reranking is enabled by default on Linux
`start-rag.sh` SHALL export `RAG_RERANK=1` unless the caller already set `RAG_RERANK`.

#### Scenario: Default start
- **WHEN** `start-rag.sh` is run without environment overrides
- **THEN** `/health` reports `"rerank": true`

#### Scenario: Explicit disable
- **WHEN** `RAG_RERANK=0 ./start-rag.sh` is run
- **THEN** `/health` reports `"rerank": false`

### Requirement: Health endpoint reports index and runtime facts
`GET /health` SHALL return `status`, `chromaDir`, `chromaExists`, `chunks` (integer, from the loaded collection count or, if not yet loaded, from `data/index_report.json`), `device`, `rerank`, `embedModel`, `rerankModel`.

#### Scenario: Health after index loaded
- **WHEN** `/health` is called after at least one `/search`
- **THEN** `chunks` equals the collection count (currently 67269) and the backend `ragStatus.chunks` shown in the UI is non-zero without relying on the report-file fallback

### Requirement: Chroma telemetry is disabled
The service SHALL construct its Chroma client with `anonymized_telemetry=False`.

#### Scenario: Clean log
- **WHEN** the service handles 20 searches
- **THEN** `rag.log` contains no "Failed to send telemetry" lines

### Requirement: Search latency stays interactive with reranking on GPU
With `RAG_RERANK=1` and `device=cuda`, `POST /search` with `topK=5` SHALL complete in under 500ms median on the deployment server after warm-up.

#### Scenario: Latency check
- **WHEN** 10 consecutive searches for "庚金生于巳月 用神" are timed after a warm-up call
- **THEN** the median wall-clock time is below 500ms

### Requirement: Linux-installable requirements
`rag/requirements.txt` SHALL NOT list `pywin32`, and SHALL document that torch is installed separately with the CUDA index URL.

#### Scenario: Fresh install on Linux
- **WHEN** `uv pip install -r rag/requirements.txt` runs in a fresh Linux venv
- **THEN** it completes without a platform resolution error
