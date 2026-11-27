from pathlib import Path
import json

import pytest

import scripts.workspace as workspace


def base_config():
    return {
        "schema": 1,
        "workspace": {"id": "test"},
        "environment": {"conda_name": "cad-mcp-workspace"},
        "repositories": {
            "cad": {"url": "https://github.com/example/cad.git", "branch": "dev"},
        },
        "solidcraft": {"version": "0.49.0"},
        "paths": {
            "externals": "ext",
            "cad": ".repos/cad",
            "generated": ".generated",
        },
    }


def test_model_relative_rejects_catalog_and_traversal():
    assert workspace.model_relative("models/components/part") == Path(
        "models/components/part"
    )
    with pytest.raises(workspace.WorkspaceError):
        workspace.model_relative("../other")
    with pytest.raises(workspace.WorkspaceError):
        workspace.model_relative("components/part")


def test_workspace_paths_separate_externals_from_active_cad(monkeypatch, tmp_path):
    monkeypatch.setattr(workspace, "ROOT", tmp_path)
    paths = workspace.workspace_paths(base_config())
    assert paths["mcp"] == (tmp_path / "ext" / "mcp").resolve()
    assert paths["forge"] == (tmp_path / "ext" / "forge").resolve()
    assert paths["cad"] == (tmp_path / ".repos" / "cad").resolve()


def test_generate_opens_only_exact_target(monkeypatch, tmp_path):
    data = base_config()
    local = {
        "schema": 1,
        "target": {"model": "models/components/part"},
        "solidcraft": {"cli": r"C:\SolidCraft\solidcraft-cli.exe"},
    }

    (tmp_path / "ext" / "mcp" / ".git").mkdir(parents=True)
    (tmp_path / "ext" / "forge" / ".git").mkdir(parents=True)
    owner = tmp_path / ".repos" / "cad" / "models" / "components" / "part"
    owner.mkdir(parents=True)
    (owner / "model.yml").write_text("id: part\n", encoding="utf-8")

    monkeypatch.setattr(workspace, "ROOT", tmp_path)
    monkeypatch.setattr(workspace.sys, "executable", str(tmp_path / "python.exe"))

    state = workspace.generate(data, local)
    assert state["target"] == "models/components/part"

    generated = tmp_path / ".generated"
    code = json.loads(
        (generated / "forge-cad.code-workspace").read_text(encoding="utf-8")
    )
    assert code["folders"] == [{"name": "part", "path": str(owner.resolve())}]

    mcp = json.loads(
        (generated / "mcp-config.json").read_text(encoding="utf-8")
    )
    args = mcp["mcpServers"]["forgeCad"]["args"]
    assert "--cad-library" in args
    assert "--model-root" in args
    assert "models/components/part" in args
    assert str((tmp_path / "ext" / "forge").resolve()) in args


def test_missing_vcs2l_external_checkout_is_reported(monkeypatch, tmp_path):
    monkeypatch.setattr(workspace, "ROOT", tmp_path)
    paths = workspace.workspace_paths(base_config())
    with pytest.raises(workspace.WorkspaceError, match="import-dependencies.ps1"):
        workspace.require_external_toolchain(paths)


def test_existing_cad_checkout_is_only_validated(monkeypatch, tmp_path):
    data = base_config()
    cad = tmp_path / "cad"
    cad.mkdir()
    calls = []

    monkeypatch.setattr(
        workspace,
        "require_repo",
        lambda path, url: calls.append((path, url)),
    )
    monkeypatch.setattr(
        workspace,
        "run",
        lambda *args, **kwargs: pytest.fail(
            "existing CAD checkout must not be changed"
        ),
    )

    workspace.ensure_cad(data, cad)
    assert calls == [(cad, data["repositories"]["cad"]["url"])]


def test_template_requires_concrete_cad_url(tmp_path):
    data = base_config()
    data["repositories"]["cad"]["url"] = None
    with pytest.raises(workspace.WorkspaceError, match="repositories.cad.url"):
        workspace.ensure_cad(data, tmp_path / "cad")
