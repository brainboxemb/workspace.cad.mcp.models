$ErrorActionPreference = "Stop"
$Environment = "cad-mcp-workspace"
conda run --no-capture-output --name $Environment python (Join-Path $PSScriptRoot "workspace.py") doctor
