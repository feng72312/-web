#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/frontend"

if [[ ! -d node_modules ]]; then
  echo "[frontend] installing npm dependencies..."
  npm install --cache .npm-cache
fi

echo "[frontend] building production bundle..."
npm run build

echo "[frontend] preview on http://0.0.0.0:5173 (LAN: http://172.16.7.144:5173)"
exec npm run preview
