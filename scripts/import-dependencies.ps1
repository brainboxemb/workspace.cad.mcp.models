[CmdletBinding()]
param(
    [string]$CondaExe
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Manifest = Join-Path $Root 'dependencies.repos'
$Ext = Join-Path $Root 'ext'

if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) {
    throw "Missing dependency manifest: $Manifest"
}

New-Item -ItemType Directory -Path $Ext -Force | Out-Null

$vcs = Get-Command vcs -CommandType Application -ErrorAction SilentlyContinue
Push-Location $Root
try {
    if ($vcs) {
        Write-Host "Fetching external toolchain using: $($vcs.Source)"
        & $vcs.Source import --input dependencies.repos ext
    } else {
        $condaOnPath = Get-Command conda.exe -CommandType Application -ErrorAction SilentlyContinue
        $candidates = @(
            $CondaExe
            $env:CONDA_EXE
            $(if ($condaOnPath) { $condaOnPath.Source })
            'C:\tools\miniconda3\Scripts\conda.exe'
            'C:\tools\miniforge3\Scripts\conda.exe'
            $(if ($env:USERPROFILE) { Join-Path $env:USERPROFILE 'miniconda3\Scripts\conda.exe' })
            $(if ($env:USERPROFILE) { Join-Path $env:USERPROFILE 'miniforge3\Scripts\conda.exe' })
        )
        $conda = $candidates |
            Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } |
            Select-Object -First 1

        if (-not $conda) {
            throw "vcs2l was not found. Install brainboxemb-dev-tools via brainboxemb/tool.py-dev-env, or activate that environment and rerun."
        }

        $conda = (Resolve-Path -LiteralPath $conda).Path
        Write-Host 'Fetching external toolchain from Conda environment brainboxemb-dev-tools...'
        & $conda run --no-capture-output --name brainboxemb-dev-tools vcs import --input dependencies.repos ext
    }

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
