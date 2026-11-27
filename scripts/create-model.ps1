param(
    [Parameter(Mandatory = $true)]
    [string]$Model,
    [Parameter(Mandatory = $true)]
    [string]$Id,
    [Parameter(Mandatory = $true)]
    [string]$Title,
    [int]$Priority = 100
)

$ErrorActionPreference = "Stop"
$Environment = "cad-mcp-workspace"
$Workspace = Join-Path $PSScriptRoot "workspace.py"
conda run --no-capture-output --name $Environment python $Workspace create-model --model $Model --id $Id --title $Title --priority $Priority
