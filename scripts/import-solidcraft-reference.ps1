param(
    [Parameter(Mandatory = $true)]
    [string]$Source,
    [string]$Name
)

$ErrorActionPreference = "Stop"
$Environment = "cad-mcp-workspace"
$Workspace = Join-Path $PSScriptRoot "workspace.py"
$Arguments = @($Workspace, "import-reference", "--source", $Source)
if ($Name) { $Arguments += @("--name", $Name) }
conda run --no-capture-output --name $Environment python @Arguments
