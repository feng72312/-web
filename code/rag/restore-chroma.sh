#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PARTS="$ROOT/data/chroma-parts"
OUT="$ROOT/data/chroma/chroma.sqlite3"

mkdir -p "$ROOT/data/chroma"

if [[ -f "$OUT" ]]; then
  echo "Chroma database already exists: $OUT"
  exit 0
fi

shopt -s nullglob
files=("$PARTS"/chroma.sqlite3.gz.part-*)
if [[ ${#files[@]} -eq 0 ]]; then
  echo "Missing split archive under $PARTS" >&2
  exit 1
fi

cat "${files[@]}" | gzip -dc > "$OUT"
echo "Restored $OUT"
