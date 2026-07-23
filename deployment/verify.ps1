# Windows Docker Desktop helper for unified deployment checks.
# See deployment/WINDOWS_DOCKER_DESKTOP.md for bind/path constraints.
param(
  [ValidateSet("offline", "unified", "topology", "matrix")]
  [string]$Command = "offline",
  [string]$BaseUrl = "http://127.0.0.1:8080"
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

switch ($Command) {
  "offline" {
    python scripts/verify_unified_deployment.py offline
  }
  "topology" {
    python scripts/verify_unified_deployment.py topology
  }
  "matrix" {
    python scripts/verify_unified_deployment.py matrix
  }
  "unified" {
    if (-not $env:INSIGHT_UNIFIED_IMAGE) {
      Write-Error "Set INSIGHT_UNIFIED_IMAGE to an immutable @sha256 digest before live checks that start containers."
    }
    python scripts/verify_unified_deployment.py unified --base-url $BaseUrl
  }
}

exit $LASTEXITCODE
