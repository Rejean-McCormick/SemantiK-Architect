$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if (-not $env:PGF_PATH) { $env:PGF_PATH = Join-Path $Root "runtime\semantik_architect.pgf" }
python manage.py doctor
if ($LASTEXITCODE -ne 0) { throw "Runtime not ready. Supply runtime\semantik_architect.pgf and pgf Python package." }
python manage.py serve --reload
