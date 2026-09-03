#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOT/logs/tunnel.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "[tunnel] not running"
  exit 0
fi

pid="$(cat "$PID_FILE")"
if kill -0 "$pid" 2>/dev/null; then
  kill "$pid" 2>/dev/null || true
  sleep 1
  if kill -0 "$pid" 2>/dev/null; then
    kill -9 "$pid" 2>/dev/null || true
  fi
  echo "[tunnel] stopped pid=$pid"
else
  echo "[tunnel] pid $pid already dead"
fi
rm -f "$PID_FILE" "$ROOT/logs/tunnel.url"
