param(
    [string]$RepoRoot = "C:\mycode\SemantiK_Architect\SemantiK_Architect",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$OverlayRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ManifestPath = Join-Path $OverlayRoot "overlay-manifest.json"
if (-not (Test-Path $ManifestPath -PathType Leaf)) { throw "overlay-manifest.json missing" }
$Manifest = Get-Content -Raw -Encoding UTF8 $ManifestPath | ConvertFrom-Json
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -Path $Path).Hash.ToLowerInvariant()
}

if (-not (Test-Path $RepoRoot -PathType Container)) { throw "RepoRoot not found: $RepoRoot" }
$Pyproject = Join-Path $RepoRoot "pyproject.toml"
$KristalAcl = Join-Path $RepoRoot "src\semantik_architect\adapters\ecosystem\kristal_v6.py"
if (-not (Test-Path $Pyproject -PathType Leaf)) { throw "Not a SemantiK Architect repo: pyproject.toml missing" }
if (-not (Test-Path $KristalAcl -PathType Leaf)) { throw "Kristal v6 baseline not detected: kristal_v6.py missing" }
$ProjectText = Get-Content -Raw -Encoding UTF8 $Pyproject
if ($ProjectText -notmatch 'version\s*=\s*"1\.2\.0"' -and -not $Force) {
    throw "Expected Kristal v6 SemantiK Architect 1.2.0 baseline. Use -Force only after manual review."
}

foreach ($entry in $Manifest.files) {
    $rel = [string]$entry.path
    $src = Join-Path $OverlayRoot $rel
    $dst = Join-Path $RepoRoot $rel
    if (-not (Test-Path $src -PathType Leaf)) { throw "Overlay file missing: $src" }
    if ($null -ne $entry.base_sha256 -and (Test-Path $dst -PathType Leaf) -and -not $Force) {
        $actual = Get-Sha256 $dst
        $expected = ([string]$entry.base_sha256).ToLowerInvariant()
        if ($actual -ne $expected) {
            throw "Baseline hash mismatch for $rel. Expected $expected, got $actual. Refusing to overwrite Kristal v6 evolution; review or use -Force deliberately."
        }
    }
}

$BackupRoot = Join-Path $RepoRoot (".overlay-backups\kristal-v6-1.2.1-" + $Stamp)
New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null

foreach ($entry in $Manifest.files) {
    $rel = [string]$entry.path
    $src = Join-Path $OverlayRoot $rel
    $dst = Join-Path $RepoRoot $rel
    $parent = Split-Path -Parent $dst
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    if (Test-Path $dst -PathType Leaf) {
        $backup = Join-Path $BackupRoot $rel
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backup) | Out-Null
        Copy-Item $dst $backup -Force
    }
    Copy-Item $src $dst -Force
    $actualNew = Get-Sha256 $dst
    $expectedNew = ([string]$entry.new_sha256).ToLowerInvariant()
    if ($actualNew -ne $expectedNew) { throw "Post-copy hash mismatch: $rel" }
    Write-Host "Applied: $rel"
}

Write-Host ""
Write-Host "SemantiK Architect Kristal v6 updated to 1.2.1."
Write-Host "Kristal v6 ACL/schema/migration were preserved; only candidate extension-capability support was added."
Write-Host "Backup: $BackupRoot"
Write-Host "Recommended validation: PYTHONPATH=src:. python tools/validate_repository.py"
