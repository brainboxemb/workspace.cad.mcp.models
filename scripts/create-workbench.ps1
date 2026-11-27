param(
    [Parameter(Mandatory = $true)]
    [string]$Name
)

$ErrorActionPreference = "Stop"
$Environment = "cad-mcp-workspace"
$Workspace = Join-Path $PSScriptRoot "workspace.py"
conda run --no-capture-output --name $Environment python $Workspace create-workbench --name $Name
