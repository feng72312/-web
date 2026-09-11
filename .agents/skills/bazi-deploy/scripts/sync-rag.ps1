# Sync code/rag search service + Chroma index to bazi-deploy/rag for CloudBase MCP.
param(
    [string]$SourceRoot = "d:\ZY\code\rag",
    [string]$DeployRoot = "$env:USERPROFILE\bazi-deploy\rag"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $SourceRoot)) {
    throw "Source rag not found: $SourceRoot"
}

$chroma = Join-Path $SourceRoot "data\chroma"
if (-not (Test-Path $chroma)) {
    throw "Chroma index missing. Run code/rag/build-index.bat first."
}

New-Item -ItemType Directory -Force -Path $DeployRoot | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $DeployRoot "data") | Out-Null

foreach ($file in @("server.py", "bazi_rag_engine.py", "categories.py", "config.py", "Dockerfile", "requirements-server.txt", ".dockerignore")) {
    Copy-Item -Force (Join-Path $SourceRoot $file) (Join-Path $DeployRoot $file)
}

robocopy $chroma (Join-Path $DeployRoot "data\chroma") /E /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy chroma failed with exit code $LASTEXITCODE" }

Write-Output "Synced rag to $DeployRoot"
