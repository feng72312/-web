# Install git hooks from scripts/git-hooks/ into .git/hooks/

$ErrorActionPreference = "Stop"

$root = git rev-parse --show-toplevel 2>$null
if (-not $root) {
    Write-Error "Not inside a git repository."
}

$srcDir = Join-Path $root "scripts\git-hooks"
$dstDir = Join-Path $root ".git\hooks"

if (-not (Test-Path $srcDir)) {
    Write-Error "Hook source directory not found: $srcDir"
}

New-Item -ItemType Directory -Force -Path $dstDir | Out-Null

Get-ChildItem -Path $srcDir -File | ForEach-Object {
    $dst = Join-Path $dstDir $_.Name
    Copy-Item -Path $_.FullName -Destination $dst -Force
    Write-Host "Installed: $dst"
}

Write-Host "Git hooks installed."
