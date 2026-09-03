#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"

CODE_FILE="$ROOT/backend/data/tunnel_access_code.txt"
if [[ -f "$CODE_FILE" ]]; then
  if [[ ! -f "$LOG_DIR/tunnel.pid" ]] || ! kill -0 "$(cat "$LOG_DIR/tunnel.pid")" 2>/dev/null; then
    rm -f "$CODE_FILE"
  fi
fi

port_in_use() {
  local port="$1"
  ss -tln | awk '{print $4}' | grep -E "[:.]${port}\$" >/dev/null 2>&1
}

for spec in "8100 RAG" "8002 backend" "5173 frontend"; do
  port="${spec%% *}"
  name="${spec#* }"
  if port_in_use "$port"; then
    echo "[start-all] port ${port} (${name}) is already in use; refuse to start or kill anything" >&2
    exit 1
  fi
done

echo "[start-all] starting RAG..."
nohup "$ROOT/start-rag.sh" >"$LOG_DIR/rag.log" 2>&1 &
echo $! >"$LOG_DIR/rag.pid"

for _ in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:8100/health" >/dev/null; then
    echo "[start-all] RAG ready"
    break
  fi
  if ! kill -0 "$(cat "$LOG_DIR/rag.pid")" 2>/dev/null; then
    echo "[start-all] RAG exited; see $LOG_DIR/rag.log" >&2
    exit 1
  fi
  sleep 1
done
if ! curl -sf "http://127.0.0.1:8100/health" >/dev/null; then
  echo "[start-all] RAG health timeout; see $LOG_DIR/rag.log" >&2
  exit 1
fi

echo "[start-all] starting backend..."
nohup "$ROOT/start-backend.sh" >"$LOG_DIR/backend.log" 2>&1 &
echo $! >"$LOG_DIR/backend.pid"

for _ in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:8002/health" >/dev/null; then
    echo "[start-all] backend ready"
    break
  fi
  if ! kill -0 "$(cat "$LOG_DIR/backend.pid")" 2>/dev/null; then
    echo "[start-all] backend exited; see $LOG_DIR/backend.log" >&2
    exit 1
  fi
  sleep 1
done
if ! curl -sf "http://127.0.0.1:8002/health" >/dev/null; then
  echo "[start-all] backend health timeout; see $LOG_DIR/backend.log" >&2
  exit 1
fi

echo "[start-all] starting frontend (build + preview)..."
nohup "$ROOT/start-frontend.sh" >"$LOG_DIR/frontend.log" 2>&1 &
echo $! >"$LOG_DIR/frontend.pid"

for _ in $(seq 1 180); do
  if curl -sf "http://127.0.0.1:5173" >/dev/null; then
    echo "[start-all] frontend ready"
    break
  fi
  if ! kill -0 "$(cat "$LOG_DIR/frontend.pid")" 2>/dev/null; then
    echo "[start-all] frontend exited; see $LOG_DIR/frontend.log" >&2
    exit 1
  fi
  sleep 1
done
if ! curl -sf "http://127.0.0.1:5173" >/dev/null; then
  echo "[start-all] frontend timeout; see $LOG_DIR/frontend.log" >&2
  exit 1
fi

echo "[start-all] ok"
echo "  local:  http://127.0.0.1:5173"
echo "  LAN:    http://172.16.7.144:5173"
echo "  logs:   $LOG_DIR"
