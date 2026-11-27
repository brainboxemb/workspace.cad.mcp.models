from pathlib import Path
import subprocess

import pytest
import yaml

from scripts import dependency_state


def git(path: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(path), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def make_repo(root: Path, name: str, url: str, version: str) -> Path:
    repo = root / name
    repo.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Tests"], cwd=repo, check=True)
    subprocess.run(
        ["git", "config", "user.email", "tests@example.invalid"],
        cwd=repo,
        check=True,
    )
    (repo / "file.txt").write_text("baseline\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(
        ["git", "commit", "-m", "baseline"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "tag", version], cwd=repo, check=True)
    subprocess.run(["git", "remote", "add", "origin", url], cwd=repo, check=True)
    return repo


def write_manifest(path: Path, versions: dict[str, str]) -> Path:
    repositories = {}
    for name, version in versions.items():
        repositories[name] = {
            "type": "git",
            "url": f"https://github.com/example/{name}.git",
            "version": version,
        }
    manifest = path / "dependencies.repos"
    manifest.write_text(
        yaml.safe_dump({"repositories": repositories}, sort_keys=False),
        encoding="utf-8",
    )
    return manifest


def test_matching_external_checkouts_are_current(tmp_path):
    root = tmp_path / "ext"
    root.mkdir()
    manifest = write_manifest(tmp_path, {"mcp": "v1.0.0", "forge": "v2.0.0"})
    make_repo(root, "mcp", "https://github.com/example/mcp.git", "v1.0.0")
    make_repo(root, "forge", "https://github.com/example/forge.git", "v2.0.0")

    assert dependency_state.dependency_state(manifest, root) == "current"


def test_missing_or_stale_external_requests_reconcile(tmp_path):
    root = tmp_path / "ext"
    root.mkdir()
    manifest = write_manifest(tmp_path, {"mcp": "v1.1.0"})
    repo = make_repo(root, "mcp", "https://github.com/example/mcp.git", "v1.0.0")

    assert dependency_state.dependency_state(manifest, root) == "reconcile"

    subprocess.run(["git", "tag", "v1.1.0"], cwd=repo, check=True)
    assert dependency_state.dependency_state(manifest, root) == "current"

    (root / "mcp").rename(root / "old-mcp")
    assert dependency_state.dependency_state(manifest, root) == "reconcile"


def test_generated_python_metadata_does_not_make_external_dirty(tmp_path):
    root = tmp_path / "ext"
    root.mkdir()
    manifest = write_manifest(tmp_path, {"mcp": "v1.0.0"})
    repo = make_repo(root, "mcp", "https://github.com/example/mcp.git", "v1.0.0")

    egg = repo / "src" / "forge_cad_mcp.egg-info"
    egg.mkdir(parents=True)
    (egg / "PKG-INFO").write_text("generated\n", encoding="utf-8")
    cache = repo / "src" / "forge_mcp" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "server.cpython-312.pyc").write_bytes(b"generated")

    assert dependency_state.dependency_state(manifest, root) == "current"


def test_untracked_source_content_is_never_discarded(tmp_path):
    root = tmp_path / "ext"
    root.mkdir()
    manifest = write_manifest(tmp_path, {"mcp": "v1.1.0"})
    repo = make_repo(root, "mcp", "https://github.com/example/mcp.git", "v1.0.0")
    (repo / "local.txt").write_text("do not delete\n", encoding="utf-8")

    with pytest.raises(
        dependency_state.DependencyStateError,
        match="untracked local content",
    ):
        dependency_state.dependency_state(manifest, root)


def test_tracked_source_changes_are_never_discarded(tmp_path):
    root = tmp_path / "ext"
    root.mkdir()
    manifest = write_manifest(tmp_path, {"mcp": "v1.1.0"})
    repo = make_repo(root, "mcp", "https://github.com/example/mcp.git", "v1.0.0")
    (repo / "file.txt").write_text("edited\n", encoding="utf-8")

    with pytest.raises(
        dependency_state.DependencyStateError,
        match="tracked local changes",
    ):
        dependency_state.dependency_state(manifest, root)


def test_unexpected_external_origin_is_never_deleted(tmp_path):
    root = tmp_path / "ext"
    root.mkdir()
    manifest = write_manifest(tmp_path, {"mcp": "v1.0.0"})
    make_repo(root, "mcp", "https://github.com/example/not-mcp.git", "v1.0.0")

    with pytest.raises(
        dependency_state.DependencyStateError,
        match="unexpected origin",
    ):
        dependency_state.dependency_state(manifest, root)


def test_import_script_uses_vcs2l_for_reconciliation():
    script = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "import-dependencies.ps1"
    ).read_text(encoding="utf-8")

    assert "dependency_state.py" in script
    assert "vcs delete --input $Manifest --force" in script
    assert "$ManifestContent |" not in script
    assert "vcs import --input dependencies.repos ext" in script
    assert "Remove-Item" not in script
