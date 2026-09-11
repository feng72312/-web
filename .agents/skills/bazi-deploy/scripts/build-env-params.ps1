# Build EnvParams JSON for CloudRun deploy from backend/.env + production defaults.

param(

    [string]$EnvFile = "d:\ZY\code\backend\.env",

    [string]$RagProvider = "",

    [string]$RagUrl = "https://bazi-rag-262409-10-1437107927.sh.run.tcloudbase.com"

)



$ErrorActionPreference = "Stop"



$defaults = [ordered]@{

    BAZI_DEBUG             = "false"

    BAZI_RAG_PROVIDER      = "stub"

    BAZI_CURSOR_RUNTIME    = "cloud"

    BAZI_CURSOR_MODEL      = "composer-2.5"

    BAZI_DEEPSEEK_BASE_URL = "https://api.deepseek.com"

    BAZI_QUOTA_DB_PATH       = "/mnt/data/quota.db"

    BAZI_STATS_DB_PATH       = "/mnt/data/usage_stats.db"

}



if (Test-Path $EnvFile) {

    Get-Content $EnvFile | ForEach-Object {

        $line = $_.Trim()

        if ($line -eq "" -or $line.StartsWith("#")) { return }

        $idx = $line.IndexOf("=")

        if ($idx -lt 1) { return }

        $key = $line.Substring(0, $idx).Trim()

        $val = $line.Substring($idx + 1).Trim()

        if ($key.StartsWith("BAZI_")) {

            $defaults[$key] = $val

        }

    }

}



# Production overrides

$defaults["BAZI_DEBUG"] = "false"

$defaults["BAZI_CURSOR_RUNTIME"] = "cloud"



if ($RagProvider -ne "") {

    $defaults["BAZI_RAG_PROVIDER"] = $RagProvider

} else {

    $defaults["BAZI_RAG_PROVIDER"] = "http"

}



if ($RagUrl -ne "") {

    $defaults["BAZI_RAG_HTTP_URL"] = $RagUrl

}



$json = ($defaults | ConvertTo-Json -Compress)

Write-Output $json

