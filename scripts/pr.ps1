param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("open", "merge", "publish")]
    [string]$Action,

    [string]$Path = ".",
    [string]$Base,
    [string]$Title,
    [string]$Body,
    [int]$Number = 0
)

$ErrorActionPreference = "Stop"
$BodySpecified = $PSBoundParameters.ContainsKey("Body")

function Invoke-Git {
    param([string[]]$Arguments)

    $Output = & git @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git failed: $($Output | Out-String)"
    }
    return ($Output | Out-String).Trim()
}

function Invoke-Gh {
    param(
        [string[]]$Arguments,
        [switch]$AllowFailure
    )

    $Output = & gh @Arguments 2>&1
    $Code = $LASTEXITCODE
    $Text = ($Output | Out-String).Trim()
    if (-not $AllowFailure -and $Code -ne 0) {
        throw "gh failed: $Text"
    }
    return [pscustomobject]@{
        Code = $Code
        Text = $Text
    }
}

function Current-Pr {
    $Result = Invoke-Gh -Arguments @("pr", "view", "--json", "number,url,state,baseRefName") -AllowFailure
    if ($Result.Code -ne 0) {
        return $null
    }
    return $Result.Text | ConvertFrom-Json
}

function Resolve-Base {
    param(
        [string]$Branch,
        [string]$ExplicitBase
    )

    if ($ExplicitBase) {
        return $ExplicitBase
    }
    if ($Branch -eq "dev") {
        return "main"
    }
    if ($Branch -eq "main") {
        throw "main requires an explicit -Base; normal publication is dev -> main."
    }
    return "dev"
}

function Open-Pr {
    param([string]$RequestedBase)

    $Branch = Invoke-Git -Arguments @("branch", "--show-current")
    if (-not $Branch) {
        throw "repository must be on a named branch"
    }

    $Dirty = Invoke-Git -Arguments @("status", "--porcelain")
    if ($Dirty) {
        throw "working tree has uncommitted changes; commit or stash them before opening a PR"
    }

    $TargetBase = Resolve-Base -Branch $Branch -ExplicitBase $RequestedBase
    $Existing = Current-Pr
    if ($null -ne $Existing -and $Existing.state -eq "OPEN") {
        if ($Existing.baseRefName -ne $TargetBase) { throw "Existing PR has a different base." }
        Invoke-Git -Arguments @("push", "--set-upstream", "origin", $Branch) | Out-Null
        Write-Host "PR #$($Existing.number) already exists: $($Existing.url)"
        return [int]$Existing.number
    }

    Invoke-Git -Arguments @("push", "--set-upstream", "origin", $Branch) | Out-Null

    $PrTitle = $Title
    if (-not $PrTitle) {
        $PrTitle = Invoke-Git -Arguments @("log", "-1", "--pretty=%s")
    }

    $PrBody = $Body
    if (-not $BodySpecified -and $Branch -match "^issue/(\d+)(?:-|$)") {
        $PrBody = "Closes #$($Matches[1])."
    }
    if ($null -eq $PrBody) {
        $PrBody = ""
    }

    $Created = Invoke-Gh -Arguments @(
        "pr", "create",
        "--base", $TargetBase,
        "--head", $Branch,
        "--title", $PrTitle,
        "--body", $PrBody
    )
    if ($Created.Text) {
        Write-Host $Created.Text
    }

    $Pr = Current-Pr
    if ($null -eq $Pr) {
        throw "PR was created but could not be resolved from the current branch"
    }
    return [int]$Pr.number
}

function Wait-PrChecks {
    param([int]$PrNumber)

    $ChecksFound = $false
    for ($Attempt = 0; $Attempt -lt 30; $Attempt++) {
        $Probe = Invoke-Gh -Arguments @(
            "pr", "checks", "$PrNumber", "--json", "name,state"
        ) -AllowFailure

        if ($Probe.Text) {
            try {
                $Checks = @($Probe.Text | ConvertFrom-Json)
                if ($Checks.Count -gt 0) {
                    $ChecksFound = $true
                    break
                }
            } catch {
                # GitHub can briefly report that no checks exist yet.
            }
        }
        Start-Sleep -Seconds 2
    }

    if (-not $ChecksFound) {
        throw "PR #$PrNumber has no CI checks to wait for"
    }

    $Watched = Invoke-Gh -Arguments @(
        "pr", "checks", "$PrNumber", "--watch", "--fail-fast"
    ) -AllowFailure
    if ($Watched.Text) {
        Write-Host $Watched.Text
    }
    if ($Watched.Code -ne 0) {
        throw "PR #$PrNumber checks did not complete successfully"
    }
}

function Request-Merge {
    param([int]$PrNumber)

    if ($PrNumber -le 0) {
        $Pr = Current-Pr
        if ($null -eq $Pr) {
            throw "no PR found for the current branch; pass -Number or open the PR first"
        }
        $PrNumber = [int]$Pr.number
    }

    Wait-PrChecks -PrNumber $PrNumber
    $Result = Invoke-Gh -Arguments @("pr", "comment", "$PrNumber", "--body", "/merge")
    if ($Result.Text) {
        Write-Host $Result.Text
    }
    Write-Host "Requested repository-policy merge for PR #$PrNumber."
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is required"
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) is required; install it and run 'gh auth login' first"
}

$RepositoryPath = (Resolve-Path -LiteralPath $Path).Path
Push-Location $RepositoryPath
try {
    Invoke-Git -Arguments @("rev-parse", "--show-toplevel") | Out-Null

    switch ($Action) {
        "open" {
            [void](Open-Pr -RequestedBase $Base)
        }
        "merge" {
            Request-Merge -PrNumber $Number
        }
        "publish" {
            $PrNumber = Open-Pr -RequestedBase $Base
            Request-Merge -PrNumber $PrNumber
        }
    }
} finally {
    Pop-Location
}
