param(
    [Parameter(Mandatory=$true)][ValidateRange(1,2147483647)][int]$Issue,
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-z0-9]+(-[a-z0-9]+)*$')][string]$Name,
    [ValidateSet("dev","main")][string]$Base = "dev",
    [string]$Path = (Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference = "Stop"
function Invoke-RepoGit([string[]]$Arguments) {
    $result = & git -C $Path @Arguments
    if ($LASTEXITCODE -ne 0) { throw "git failed: $Arguments" }
    return $result
}
if (Invoke-RepoGit @("status","--porcelain")) { throw "Commit or explicitly stash local changes first." }
Invoke-RepoGit @("fetch","origin",$Base) | Out-Host
Invoke-RepoGit @("switch","-c","issue/$Issue-$Name","FETCH_HEAD") | Out-Host
