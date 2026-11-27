$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Environment = "cad-mcp-workspace"
$EnvironmentFile = Join-Path $Root "environment.yml"

conda env update --name $Environment --file $EnvironmentFile --prune
if ($LASTEXITCODE -ne 0) {
    throw "Conda environment update failed."
}

& (Join-Path $PSScriptRoot "import-dependencies.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "External dependency import failed."
}

conda run --no-capture-output --name $Environment python (Join-Path $PSScriptRoot "workspace.py") update
