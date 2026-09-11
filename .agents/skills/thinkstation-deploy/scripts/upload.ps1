# Upload local file or directory to ThinkStation deploy dir via SFTP.
param(
    [Parameter(Mandatory = $true)]
    [string]$LocalPath,

    [string]$RemoteSubPath = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillRoot = Split-Path -Parent $ScriptDir
$PyScript = Join-Path $ScriptDir "upload.py"

if (-not (Test-Path $LocalPath)) {
    throw "Local path not found: $LocalPath"
}

$RemoteSubPathArg = ""
if ($RemoteSubPath) {
    $RemoteSubPathArg = "--remote-subpath `"$RemoteSubPath`""
}

py -3 $PyScript --local "$LocalPath" $RemoteSubPathArg
if ($LASTEXITCODE -ne 0) { throw "upload failed with exit code $LASTEXITCODE" }

Write-Output "Uploaded $LocalPath to ThinkStation deploy dir"
