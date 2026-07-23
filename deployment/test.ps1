$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

python scripts/check_deployment.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python scripts/verify_unified_deployment.py offline
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m unittest `
  tests.test_deployment_contract `
  tests.test_unified_image `
  tests.test_tp22_unified_verification `
  -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Push-Location Modules\Treatment-Plan
try {
  $env:PYTHONPATH = "."
  python -m unittest tests.test_tp22_deployment -v
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  python scripts/verify_deployment.py integrity
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
  Pop-Location
}

Write-Host "deployment verification (Windows offline) passed"
