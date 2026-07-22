$ErrorActionPreference = "Stop"
if (-not $env:TP_ENV) { $env:TP_ENV = "development" }
python -m treatment_plan

