$ErrorActionPreference = "Stop"
$Environment = "cad-mcp-workspace"

& (Join-Path $PSScriptRoot "import-dependencies.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "External dependency import failed."
}

conda run --no-capture-output --name $Environment python (Join-Path $PSScriptRoot "workspace.py") update
