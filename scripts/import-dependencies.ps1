[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Manifest = Join-Path $Root 'dependencies.repos'
$Ext = Join-Path $Root 'ext'
$Environment = 'cad-mcp-workspace'
$StateScript = Join-Path $PSScriptRoot 'dependency_state.py'

if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) {
    throw "Missing dependency manifest: $Manifest"
}

New-Item -ItemType Directory -Path $Ext -Force | Out-Null

function Get-DependencyState {
    $Output = & conda run --no-capture-output --name $Environment python $StateScript --manifest $Manifest --root $Ext
    if ($LASTEXITCODE -ne 0) {
        throw "External dependency state validation failed."
    }

    $State = ($Output | Select-Object -Last 1).ToString().Trim()
    if ($State -notin @('current', 'reconcile')) {
        throw "Unexpected external dependency state: $State"
    }
    return $State
}

$State = Get-DependencyState
if ($State -eq 'current') {
    Write-Host "External toolchain already matches dependencies.repos."
    return
}

Write-Host "Reconciling external toolchain from dependencies.repos with vcs2l..."

$HasExisting = $false
foreach ($Name in @('mcp', 'forge')) {
    if (Test-Path -LiteralPath (Join-Path $Ext $Name)) {
        $HasExisting = $true
        break
    }
}

if ($HasExisting) {
    $ManifestContent = Get-Content -LiteralPath $Manifest -Raw
    Push-Location $Ext
    try {
        $ManifestContent | & conda run --no-capture-output --name $Environment vcs delete --force
        if ($LASTEXITCODE -ne 0) {
            throw "vcs2l external dependency deletion failed (exit code $LASTEXITCODE)."
        }
    }
    finally {
        Pop-Location
    }
}

Push-Location $Root
try {
    & conda run --no-capture-output --name $Environment vcs import --input dependencies.repos ext
    if ($LASTEXITCODE -ne 0) {
        throw "vcs2l dependency checkout failed (exit code $LASTEXITCODE)."
    }
}
finally {
    Pop-Location
}

$State = Get-DependencyState
if ($State -ne 'current') {
    throw "vcs2l completed but external toolchain does not match dependencies.repos."
}

Write-Host "External toolchain matches dependencies.repos."
