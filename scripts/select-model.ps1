param(
    [Parameter(Mandatory = $true)]
    [string]$Model
)

$ErrorActionPreference = "Stop"
$Environment = "cad-mcp-workspace"
conda run --no-capture-output --name $Environment python (Join-Path $PSScriptRoot "workspace.py") select --model $Model
