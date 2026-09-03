#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT/rag/.venv"
cd "$ROOT/rag"

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "[rag] missing venv: $VENV" >&2
  exit 1
fi

export RAG_HOST="${RAG_HOST:-127.0.0.1}"
export PORT="${PORT:-8100}"

echo "[rag] starting on http://${RAG_HOST}:${PORT}"
exec "$VENV/bin/python" server.py
