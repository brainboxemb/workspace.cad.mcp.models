$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Previous = $env:PYTHONPATH
Push-Location $Root
try {
    conda run --no-capture-output -n cad-mcp-workspace python -m pytest -q tests
    if ($LASTEXITCODE -ne 0) { throw "Workspace tests failed." }
    foreach ($Module in @("merge-policy","branch-cleanup")) {
        $env:PYTHONPATH = Join-Path $Root "modules/$Module/src"
        conda run --no-capture-output -n cad-mcp-workspace python -m pytest -q "modules/$Module/tests"
        if ($LASTEXITCODE -ne 0) { throw "$Module tests failed." }
    }
} finally {
    $env:PYTHONPATH = $Previous
    Pop-Location
}
