# Deploy ZY stack to CloudBase (requires CloudBase MCP logged in)
# Usage: powershell -File d:\ZY\code\scripts\deploy-cloud.ps1

$ErrorActionPreference = "Stop"
$ApiBase = "https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com/api/v1"
$EnvId = "zy-feng-d3glt5d93b1a9f08e"
$SiteUrl = "https://zy-feng-d3glt5d93b1a9f08e-1437107927.tcloudbaseapp.com"

Write-Host "[1/4] Ensure junctions for MCP deploy paths..."
if (-not (Test-Path "C:\Users\liqingfeng\zy-code")) {
    cmd /c mklink /J C:\Users\liqingfeng\zy-code d:\ZY\code | Out-Null
}
if (-not (Test-Path "C:\Users\liqingfeng\zy-code-rag")) {
    cmd /c mklink /J C:\Users\liqingfeng\zy-code-rag d:\ZY\code\rag | Out-Null
}

Write-Host "[2/4] Build frontend..."
Set-Location d:\ZY\code\frontend
$env:VITE_API_BASE = $ApiBase
npm run build

Write-Host "[3/4] Deploy via CloudBase MCP in Cursor (manageCloudRun + manageHosting)."
Write-Host "  - bazi-rag: target C:\Users\liqingfeng\zy-code-rag"
Write-Host "  - bazi-api: target C:\Users\liqingfeng\zy-code, Dockerfile backend/Dockerfile"
Write-Host "  - static: upload d:\ZY\code\frontend\dist to /"

Write-Host "[4/4] URLs after deploy:"
Write-Host "  Site: $SiteUrl"
Write-Host "  Admin: $SiteUrl/admin"
Write-Host "  API:  https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com"
