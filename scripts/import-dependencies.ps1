[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Manifest = Join-Path $Root 'dependencies.repos'
$Ext = Join-Path $Root 'ext'
$Environment = 'cad-mcp-workspace'

if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) {
    throw "Missing dependency manifest: $Manifest"
}

New-Item -ItemType Directory -Path $Ext -Force | Out-Null

Push-Location $Root
try {
    Write-Host "Fetching external toolchain with vcs2l from Conda environment $Environment..."
    & conda run --no-capture-output --name $Environment vcs import --input dependencies.repos ext
    if ($LASTEXITCODE -ne 0) {
        throw "vcs2l dependency checkout failed (exit code $LASTEXITCODE)."
    }
}
finally {
    Pop-Location
}

foreach ($Name in @('mcp', 'forge')) {
    $Target = Join-Path $Ext $Name
    if (-not (Test-Path -LiteralPath (Join-Path $Target '.git') -PathType Container)) {
        throw "vcs2l did not produce the expected Git checkout: $Target"
    }
}
