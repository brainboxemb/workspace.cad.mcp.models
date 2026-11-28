param(
    [Parameter(Mandatory=$true)][string]$Message,
    [Parameter(Mandatory=$true)][string[]]$Files,
    [string]$Path = (Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference = "Stop"
function Invoke-RepoGit([string[]]$Arguments) {
    $result = & git -C $Path @Arguments
    if ($LASTEXITCODE -ne 0) { throw "git failed: $Arguments" }
    return $result
}
$branch = Invoke-RepoGit @("branch","--show-current")
if (-not $branch -or $branch -in @("main","dev","exp")) { throw "Use a temporary work branch." }
if (Invoke-RepoGit @("diff","--cached","--name-only")) { throw "Existing staged changes: review and commit manually first." }
foreach ($file in $Files) {
    if ([string]::IsNullOrWhiteSpace($file) -or $file -match '^[.-]$|^\.\.[\\/]|^:|[*?\[]' -or [IO.Path]::IsPathRooted($file)) {
        throw "Specify explicit repository-relative files, not wildcards or the repository root."
    }
    $candidate = Join-Path $Path $file
    if (Test-Path -LiteralPath $candidate -PathType Container) { throw "Specify files, not directories." }
}
Invoke-RepoGit (@("--literal-pathspecs","add","--") + $Files) | Out-Host
Invoke-RepoGit @("diff","--cached","--check") | Out-Host
if (-not (Invoke-RepoGit @("diff","--cached","--name-only"))) { throw "Nothing staged." }
Invoke-RepoGit @("diff","--cached","--stat") | Out-Host
Invoke-RepoGit @("commit","-m",$Message) | Out-Host
