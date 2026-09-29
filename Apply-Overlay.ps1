param(
    [string]$RepoRoot = "C:\mycode\SemantiK_Architect\SemantiK_Architect"
)

$ErrorActionPreference = "Stop"
$OverlayRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"

$files = @(
    "pyproject.toml",
    "CHANGELOG_v1_1.md",
    "docs\22_IMPLEMENTATION_STATUS.md",
    "docs\reference\MULTILINGUAL_CANDIDATE_MATRIX.md",
    "src\semantik_architect\__init__.py",
    "src\semantik_architect\conformance\__init__.py",
    "src\semantik_architect\conformance\candidate.py",
    "src\semantik_architect\conformance\matrix.py",
    "src\semantik_architect\adapters\realization\gf\pgf_runtime.py",
    "tests\integration\test_candidate_matrix.py",
    "tests\integration\test_konstellation.py",
    "tests\unit\test_pgf_runtime_gf_cli.py"
)

foreach ($rel in $files) {
    $src = Join-Path $OverlayRoot $rel
    $dst = Join-Path $RepoRoot $rel
    if (-not (Test-Path $src -PathType Leaf)) {
        throw "Overlay file missing: $src"
    }
    $parent = Split-Path -Parent $dst
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    if (Test-Path $dst -PathType Leaf) {
        Copy-Item $dst "$dst.backup-$Stamp" -Force
        Write-Host "Backup: $dst.backup-$Stamp"
    }
    Copy-Item $src $dst -Force
    Write-Host "Applied: $dst"
}

Write-Host "Overlay v0.2.0 applied: multilingual candidate matrix + GF CLI UTF-8 correction."
Write-Host "No language source modified; no RuntimeSet released or activated; no network access used."
