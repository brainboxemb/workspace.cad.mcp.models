$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Environment = "cad-mcp-workspace"
$EnvironmentFile = Join-Path $Root "environment.yml"

& (Join-Path $PSScriptRoot "import-dependencies.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "External dependency import failed."
}

$Known = conda env list --json | ConvertFrom-Json
$Exists = $false
foreach ($Path in $Known.envs) {
    if ((Split-Path $Path -Leaf) -eq $Environment) {
        $Exists = $true
        break
    }
}

if ($Exists) {
    conda env update --name $Environment --file $EnvironmentFile --prune
} else {
    conda env create --file $EnvironmentFile
}

conda run --no-capture-output --name $Environment python (Join-Path $PSScriptRoot "workspace.py") bootstrap
