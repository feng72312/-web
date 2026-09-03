#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"
PID_FILE="$LOG_DIR/tunnel.pid"
LOG_FILE="$LOG_DIR/tunnel.log"
BIN="${CLOUDFLARED_BIN:-$ROOT/bin/cloudflared}"
TARGET="${TUNNEL_TARGET:-http://127.0.0.1:5173}"

if [[ ! -x "$BIN" ]]; then
  echo "[tunnel] missing cloudflared: $BIN" >&2
  exit 1
fi

if ! curl -sf --max-time 3 "$TARGET" >/dev/null; then
  echo "[tunnel] frontend not reachable at $TARGET" >&2
  echo "[tunnel] start ZY first: $ROOT/start-all.sh" >&2
  exit 1
fi

CODE_FILE="$LOG_DIR/tunnel.code"
BACKEND_CODE="$ROOT/backend/data/tunnel_access_code.txt"

resolve_access_code() {
  if [[ -n "${ZY_TUNNEL_ACCESS_CODE:-}" ]]; then
    printf '%s' "$ZY_TUNNEL_ACCESS_CODE"
    return
  fi
  if [[ -f "$CODE_FILE" ]]; then
    local existing
    existing="$(tr -d '[:space:]' <"$CODE_FILE")"
    if [[ -n "$existing" ]]; then
      printf '%s' "$existing"
      return
    fi
  fi
  openssl rand -hex 3
}

ACCESS_CODE="$(resolve_access_code)"
mkdir -p "$ROOT/backend/data"
printf '%s\n' "$ACCESS_CODE" >"$CODE_FILE"
printf '%s\n' "$ACCESS_CODE" >"$BACKEND_CODE"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "[tunnel] already running pid=$(cat "$PID_FILE")"
  if [[ -f "$LOG_FILE" ]]; then
    rg -o 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' "$LOG_FILE" | tail -1 || true
  fi
  echo "[tunnel] access code: $ACCESS_CODE"
  exit 0
fi

echo "[tunnel] starting quick tunnel -> $TARGET"
nohup "$BIN" tunnel --no-autoupdate --url "$TARGET" >"$LOG_FILE" 2>&1 &
echo $! >"$PID_FILE"

url=""
for _ in $(seq 1 40); do
  if [[ -f "$LOG_FILE" ]]; then
    url="$(rg -o 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' "$LOG_FILE" | tail -1 || true)"
  fi
  if [[ -n "$url" ]]; then
    echo "[tunnel] public: $url"
    echo "[tunnel] access code: $ACCESS_CODE"
    echo "$url" >"$LOG_DIR/tunnel.url"
    exit 0
  fi
  if ! kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "[tunnel] exited; see $LOG_FILE" >&2
    exit 1
  fi
  sleep 1
done

echo "[tunnel] URL not printed yet; see $LOG_FILE" >&2
exit 1
