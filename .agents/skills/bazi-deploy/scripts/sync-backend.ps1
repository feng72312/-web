# Sync code/backend -> bazi-deploy/backend for CloudBase MCP deploy.
param(
    [string]$SourceRoot = "d:\ZY\code\backend",
    [string]$DeployRoot = "$env:USERPROFILE\bazi-deploy\backend"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $SourceRoot)) {
    throw "Source backend not found: $SourceRoot"
}

New-Item -ItemType Directory -Force -Path $DeployRoot | Out-Null

robocopy "$SourceRoot\app" "$DeployRoot\app" /E /XD __pycache__ /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed with exit code $LASTEXITCODE" }

$knowledgeSrc = Join-Path (Split-Path $SourceRoot -Parent) "knowledge\data"
$knowledgeDst = Join-Path $DeployRoot "knowledge\data"
if (Test-Path $knowledgeSrc) {
    New-Item -ItemType Directory -Force -Path (Split-Path $knowledgeDst -Parent) | Out-Null
    robocopy $knowledgeSrc $knowledgeDst /E /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy knowledge/data failed with exit code $LASTEXITCODE" }
}

Copy-Item -Force "$SourceRoot\Dockerfile" "$DeployRoot\Dockerfile"
Copy-Item -Force "$SourceRoot\requirements.txt" "$DeployRoot\requirements.txt"

# CloudRun deploy context is bazi-deploy/backend (flat app/, not backend/app/).
$dockerfile = Get-Content "$DeployRoot\Dockerfile" -Raw
$dockerfile = $dockerfile -replace "COPY backend/requirements.txt \.", "COPY requirements.txt ."
$dockerfile = $dockerfile -replace "COPY backend/app ./app", "COPY app ./app"
Set-Content -Path "$DeployRoot\Dockerfile" -Value $dockerfile -NoNewline

Write-Output "Synced backend to $DeployRoot"
