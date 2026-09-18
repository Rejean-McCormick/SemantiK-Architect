param(
    [int]$Port = 8304
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $repo '.venv\Scripts\python.exe'
Set-Location $repo

function Get-UvCommand {
    $cmd = Get-Command uv -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

$uv = Get-UvCommand
if (-not (Test-Path $venvPython)) {
    Write-Host '[SemantiK/Koali] Creating Python 3.12 virtual environment...'
    if ($uv) {
        & $uv venv .venv --python 3.12
    } elseif (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.12 -m venv .venv
    } else {
        throw 'Python 3.12 environment missing. Install uv or Python 3.12 (py launcher).'
    }
    if ($LASTEXITCODE -ne 0) { throw 'Failed to create SemantiK virtual environment.' }
}

& $venvPython -c 'import pgf, uvicorn' 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host '[SemantiK/Koali] Installing runtime dependencies into .venv...'
    if ($uv) {
        & $uv pip install --python $venvPython -r requirements.txt
    } else {
        & $venvPython -m pip install -r requirements.txt
    }
    if ($LASTEXITCODE -ne 0) { throw 'SemantiK dependency installation failed.' }
}

if (-not $env:PGF_PATH) {
    $env:PGF_PATH = Join-Path $repo 'runtime\semantik_architect.pgf'
}

Write-Host '[SemantiK/Koali] Verifying PGF runtime...'
& $venvPython manage.py doctor
if ($LASTEXITCODE -ne 0) {
    throw "SemantiK runtime is not ready. Verify pgf==1.1 and PGF artifact: $env:PGF_PATH"
}

Write-Host "[SemantiK/Koali] Starting API on http://127.0.0.1:$Port"
& $venvPython manage.py serve --reload --host 127.0.0.1 --port $Port
exit $LASTEXITCODE
