import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PWSH = shutil.which("pwsh") or shutil.which("powershell")
pytestmark = pytest.mark.skipif(not PWSH, reason="PowerShell is unavailable")


def test_operator_scripts_parse():
    for path in (ROOT / "scripts").glob("*.ps1"):
        result = subprocess.run(
            [PWSH, "-NoProfile", "-Command",
             "$errors = $null; $tokens = $null; "
             "[void][System.Management.Automation.Language.Parser]::ParseFile("
             "'"+str(path).replace("'", "''")+"',[ref]$tokens,[ref]$errors); "
             "if ($errors) { $errors | Out-String; exit 1 }"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"{path}: {result.stdout} {result.stderr}"


def test_branch_and_commit_helpers(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    def git(*args):
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()
    git("init", "-b", "dev")
    git("config", "user.name", "Test")
    git("config", "user.email", "test@example.invalid")
    (repo / "a.txt").write_text("before")
    git("add", "a.txt")
    git("commit", "-m", "initial")
    git("remote", "add", "origin", str(repo))
    def script(name, *args):
        return subprocess.run([PWSH, "-NoProfile", "-File", str(ROOT / "scripts" / name),
                               "-Path", str(repo), *args], capture_output=True, text=True)
    (repo / "a.txt").write_text("dirty")
    assert script("branch.ps1", "-Issue", "123", "-Name", "test").returncode != 0
    git("restore", "a.txt")
    result = script("branch.ps1", "-Issue", "123", "-Name", "test")
    assert result.returncode == 0, result.stderr
    assert git("branch", "--show-current") == "issue/123-test"
    (repo / "a.txt").write_text("after")
    (repo / "untracked.txt").write_text("keep")
    result = script("commit.ps1", "-Message", "change", "-Files", "a.txt")
    assert result.returncode == 0, result.stderr
    assert git("show", "--format=", "--name-only", "HEAD") == "a.txt"
    assert "untracked.txt" in git("status", "--porcelain")
