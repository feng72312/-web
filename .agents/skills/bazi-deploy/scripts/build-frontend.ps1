# Build frontend with production API base URL.
param(
    [string]$FrontendRoot = "d:\ZY\code\frontend",
    [string]$ApiBase = "https://bazi-api-262409-10-1437107927.sh.run.tcloudbase.com/api/v1"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $FrontendRoot)) {
    throw "Frontend root not found: $FrontendRoot"
}

Push-Location $FrontendRoot
try {
    $productionApiBase = $ApiBase.TrimEnd("/")
    $env:VITE_API_BASE = $productionApiBase
    $envFile = Join-Path $FrontendRoot ".env"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            $line = $_.Trim()
            if ($line -eq "" -or $line.StartsWith("#")) { return }
            $idx = $line.IndexOf("=")
            if ($idx -lt 1) { return }
            $key = $line.Substring(0, $idx).Trim()
            $val = $line.Substring($idx + 1).Trim()
            if ($key.StartsWith("VITE_")) {
                Set-Item -Path "env:$key" -Value $val
            }
        }
    }
    # Keep the deployment target authoritative even if local env files define VITE_API_BASE.
    $env:VITE_API_BASE = $productionApiBase
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }
    Write-Output "Built frontend -> $FrontendRoot\dist"
}
finally {
    Pop-Location
}
