param(
    [ValidateSet("up", "down", "logs")]
    [string]$Command = "up"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$imageTag = "insight-unified:local-build"
$env:INSIGHT_UNIFIED_IMAGE = $imageTag
$env:DASHBOARD_MOCK_AUTH = if ($env:DASHBOARD_MOCK_AUTH) { $env:DASHBOARD_MOCK_AUTH } else { "0" }
$env:AUTH_BASE_URL = if ($env:AUTH_BASE_URL) { $env:AUTH_BASE_URL } else { "http://127.0.0.1:8101" }
$env:TP_AUTHENTICATION_SESSION_URL = if ($env:TP_AUTHENTICATION_SESSION_URL) { $env:TP_AUTHENTICATION_SESSION_URL } else { "http://127.0.0.1:8101/api/auth/session" }
$env:TP_TRUSTED_INTERNAL_ORIGINS = if ($env:TP_TRUSTED_INTERNAL_ORIGINS) { $env:TP_TRUSTED_INTERNAL_ORIGINS } else { "http://127.0.0.1:8080,http://127.0.0.1:8101" }
$env:TP_BN_MANAGER_URL = if ($env:TP_BN_MANAGER_URL) { $env:TP_BN_MANAGER_URL } else { "http://127.0.0.1:8108" }
$env:TP_ENV = if ($env:TP_ENV) { $env:TP_ENV } else { "development" }
$env:INSIGHT_SECRETS_DIR = if ($env:INSIGHT_SECRETS_DIR) { $env:INSIGHT_SECRETS_DIR } else { (Resolve-Path ".\secrets-empty").Path }

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker not found. Install and start Docker Desktop, then run this launcher again."
}

function Test-DockerCommand {
    param([string[]]$Arguments)

    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        & docker @Arguments 2>$null | Out-Null
        return $LASTEXITCODE -eq 0
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
}

switch ($Command) {
    "up" {
        if (-not (Test-DockerCommand @("info"))) {
            throw "Docker Desktop is not running or Linux containers are not enabled."
        }

        if (-not (Test-DockerCommand @("image", "inspect", $imageTag))) {
            $archive = ".\insight-unified.image.tar"
            $checksumLine = Get-Content ".\SHA256SUMS" | Where-Object { $_ -match "insight-unified\.image\.tar$" } | Select-Object -First 1
            if (-not $checksumLine) {
                throw "Image checksum missing from SHA256SUMS."
            }
            $expected = ($checksumLine -split "\s+")[0].ToLowerInvariant()
            $actual = (Get-FileHash $archive -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($actual -ne $expected) {
                throw "Image archive checksum mismatch. Download bundle again."
            }

            Write-Host "Loading Docker image (first run may take a minute)..."
            docker load -i $archive
            if ($LASTEXITCODE -ne 0) { throw "Docker image load failed." }
        }

        if (-not $env:AUTH_JWT_SECRET -and -not (Test-Path ".\.env")) {
            $bytes = New-Object byte[] 48
            $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
            try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
            $secret = [Convert]::ToBase64String($bytes).TrimEnd("=").Replace("+", "-").Replace("/", "_")
            Set-Content -Path ".\.env" -Value "AUTH_JWT_SECRET=$secret" -Encoding ASCII
        }

        docker compose -f docker-compose.yaml up -d --wait --wait-timeout 120
        if ($LASTEXITCODE -ne 0) { throw "Insight startup failed. Run .\run.ps1 logs for details." }

        Write-Host ""
        Write-Host "Insight is ready: http://127.0.0.1:8080/"
        Write-Host "Login: Admin / Admin (change password after first login)"
        Start-Process "http://127.0.0.1:8080/"
    }
    "down" {
        docker compose -f docker-compose.yaml down
        if ($LASTEXITCODE -ne 0) { throw "Insight shutdown failed." }
    }
    "logs" {
        docker compose -f docker-compose.yaml logs --tail=100 -f
    }
}
