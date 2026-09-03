#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT/backend/.venv"
cd "$ROOT/backend"

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "[backend] missing venv: $VENV" >&2
  exit 1
fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8002}"

echo "[backend] starting on http://${HOST}:${PORT}"
exec "$VENV/bin/python" -m uvicorn app.main:app --host "$HOST" --port "$PORT"
