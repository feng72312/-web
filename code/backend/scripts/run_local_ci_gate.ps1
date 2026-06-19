# Local CI gate for bazi judgement pipeline (no cloud deploy)
$ErrorActionPreference = "Stop"
$Backend = Split-Path -Parent $PSScriptRoot
$Knowledge = Join-Path (Split-Path -Parent $Backend) "knowledge"

Set-Location $Backend
Write-Host "== pytest core =="
py -3.10 -m pytest tests/test_bazi_judgement_chain.py tests/test_no_primary_confidence.py tests/test_interpret_confidence_guard.py tests/test_qishi_context.py -q --tb=short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== regression gate (no LLM) =="
py -3.10 scripts/run_judgement_regression_gate.py --limit 20 --rag
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== node authority audit =="
Set-Location (Join-Path $Knowledge "scripts")
py -3.10 audit_node_authority.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "LOCAL CI GATE PASSED"
