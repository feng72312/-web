#!/usr/bin/env bash
# Cursor PDF Skill — macOS / Linux installer
# Usage: chmod +x install.sh && ./install.sh

set -euo pipefail

PACKAGE_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_SRC="$PACKAGE_DIR/skill"
SKILL_DST="$HOME/.cursor/skills/pdf"

echo "[pdf-skill] Installing to $SKILL_DST ..."

if [[ ! -f "$SKILL_SRC/SKILL.md" ]]; then
  echo "[pdf-skill] ERROR: skill/SKILL.md not found. Run from package root."
  exit 1
fi

mkdir -p "$SKILL_DST"
cp -r "$SKILL_SRC/"* "$SKILL_DST/"

echo "[pdf-skill] Installing Python dependencies ..."
python3 -m pip install --upgrade pip 2>/dev/null || true
python3 -m pip install -r "$PACKAGE_DIR/requirements.txt"

echo "[pdf-skill] Verifying ..."
python3 -c "from pypdf import PdfReader; from reportlab.pdfgen import canvas; print('Python deps OK')"

if [[ -f "$SKILL_DST/SKILL.md" ]]; then
  echo "[pdf-skill] Done. Skill installed at: $SKILL_DST"
  echo "[pdf-skill] Restart Cursor, then ask Agent to work with PDFs."
else
  echo "[pdf-skill] FAIL: SKILL.md not found after install."
  exit 1
fi
