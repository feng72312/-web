# Cursor PDF Skill — Windows installer
# Usage: .\install.ps1

$ErrorActionPreference = "Stop"
$PackageDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillSrc = Join-Path $PackageDir "skill"
$SkillDst = Join-Path $env:USERPROFILE ".cursor\skills\pdf"

Write-Host "[pdf-skill] Installing to $SkillDst ..." -ForegroundColor Cyan

if (-not (Test-Path (Join-Path $SkillSrc "SKILL.md"))) {
    Write-Host "[pdf-skill] ERROR: skill/SKILL.md not found. Run from package root." -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Force -Path $SkillDst | Out-Null
Copy-Item -Path "$SkillSrc\*" -Destination $SkillDst -Recurse -Force

Write-Host "[pdf-skill] Installing Python dependencies ..." -ForegroundColor Cyan
python -m pip install --upgrade pip 2>$null
python -m pip install -r (Join-Path $PackageDir "requirements.txt")

Write-Host "[pdf-skill] Verifying ..." -ForegroundColor Cyan
python -c "from pypdf import PdfReader; from reportlab.pdfgen import canvas; print('Python deps OK')"

if (Test-Path (Join-Path $SkillDst "SKILL.md")) {
    Write-Host "[pdf-skill] Done. Skill installed at: $SkillDst" -ForegroundColor Green
    Write-Host "[pdf-skill] Restart Cursor, then ask Agent to work with PDFs." -ForegroundColor Green
} else {
    Write-Host "[pdf-skill] FAIL: SKILL.md not found after install." -ForegroundColor Red
    exit 1
}
