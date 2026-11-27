from pathlib import Path
import json

import pytest
import yaml

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


def test_initial_cad_checkout_is_single_branch_blobless(monkeypatch, tmp_path):
    data = base_config()
    cad = tmp_path / "cad"
    calls = []

    monkeypatch.setattr(
        workspace,
        "run",
        lambda args, **kwargs: calls.append(args) or "",
    )
    monkeypatch.setattr(workspace, "require_repo", lambda path, url: None)

    workspace.ensure_cad(data, cad)

    assert calls == [[
        "git",
        "clone",
        "--single-branch",
        "--filter=blob:none",
        "--branch",
        "dev",
        data["repositories"]["cad"]["url"],
        str(cad),
    ]]


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


def test_pinned_mcp_is_installed_non_editable(monkeypatch, tmp_path):
    paths = {
        "mcp": tmp_path / "ext" / "mcp",
        "forge": tmp_path / "ext" / "forge",
    }
    calls = []

    monkeypatch.setattr(workspace, "require_external_toolchain", lambda paths: None)
    monkeypatch.setattr(
        workspace,
        "run",
        lambda args, **kwargs: calls.append(args) or "",
    )

    workspace.install_toolchain(paths)

    assert calls[0] == [
        workspace.sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        str(paths["mcp"]),
    ]
    assert "-e" not in calls[0]


def test_environment_contains_vcs2l():
    data = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "environment.yml").read_text(
            encoding="utf-8"
        )
    )
    pip = next(
        item["pip"]
        for item in data["dependencies"]
        if isinstance(item, dict) and "pip" in item
    )
    assert "vcs2l==1.1.7" in pip


def test_new_model_relative_requires_structured_owner():
    assert workspace.new_model_relative("models/basic/new-part") == Path(
        "models/basic/new-part"
    )
    with pytest.raises(workspace.WorkspaceError):
        workspace.new_model_relative("models/new-part")
    with pytest.raises(workspace.WorkspaceError):
        workspace.new_model_relative("models/unknown/new-part")


def test_create_model_scaffolds_owner_and_selects_it(monkeypatch, tmp_path):
    data = base_config()
    cad = tmp_path / ".repos" / "cad"
    cad.mkdir(parents=True)
    (cad / ".git").mkdir()
    (tmp_path / "workspace.local.yml").write_text(
        "schema: 1\ntarget:\n  model: models/basic/old\nsolidcraft:\n  cli: C:\\\\SolidCraft\\\\solidcraft-cli.exe\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(workspace, "ROOT", tmp_path)
    monkeypatch.setattr(workspace, "LOCAL_PATH", tmp_path / "workspace.local.yml")
    monkeypatch.setattr(workspace, "config", lambda: data)
    monkeypatch.setattr(workspace, "require_repo", lambda path, url: None)

    def fake_git(path, *args, capture=False):
        if args[:2] == ("branch", "--show-current"):
            return "issue/100-new-part"
        if args[:2] == ("status", "--porcelain"):
            return ""
        raise AssertionError(args)

    monkeypatch.setattr(workspace, "git", fake_git)

    result = workspace.create_model(
        "models/basic/new-part",
        "new-part",
        "New Part",
        20,
    )

    owner = cad / "models" / "basic" / "new-part"
    assert result["model"] == "models/basic/new-part"
    assert result["source_expected"].endswith("scpf/model.py")
    assert yaml.safe_load((owner / "ci.yml").read_text(encoding="utf-8")) == {
        "schema": 1,
        "id": "new-part",
        "builder": "forge",
        "source": "scpf/model.py",
        "process": True,
    }
    model = yaml.safe_load((owner / "model.yml").read_text(encoding="utf-8"))
    assert model["section"] == "basic"
    assert model["title"] == "New Part"
    local = yaml.safe_load(
        (tmp_path / "workspace.local.yml").read_text(encoding="utf-8")
    )
    assert local["target"]["model"] == "models/basic/new-part"


def test_create_model_requires_short_lived_clean_cad_branch(monkeypatch, tmp_path):
    data = base_config()
    cad = tmp_path / ".repos" / "cad"
    cad.mkdir(parents=True)
    (cad / ".git").mkdir()

    monkeypatch.setattr(workspace, "ROOT", tmp_path)
    monkeypatch.setattr(workspace, "config", lambda: data)
    monkeypatch.setattr(workspace, "require_repo", lambda path, url: None)
    monkeypatch.setattr(
        workspace,
        "git",
        lambda path, *args, capture=False: "dev"
        if args[:2] == ("branch", "--show-current")
        else "",
    )

    with pytest.raises(workspace.WorkspaceError, match="short-lived CAD work branch"):
        workspace.create_model("models/basic/new-part", "new-part", "New Part")


def test_import_reference_is_byte_identical_and_immutable(monkeypatch, tmp_path):
    data = base_config()
    cad = tmp_path / ".repos" / "cad"
    owner = cad / "models" / "components" / "native-part"
    owner.mkdir(parents=True)
    (owner / "model.yml").write_text("title: Native Part\n", encoding="utf-8")
    local = tmp_path / "workspace.local.yml"
    local.write_text(
        "schema: 1\ntarget:\n  model: models/components/native-part\nsolidcraft:\n  cli: solidcraft-cli\n",
        encoding="utf-8",
    )
    source = tmp_path / "original.sc"
    source.write_bytes(b"native-solidcraft-checkpoint")

    monkeypatch.setattr(workspace, "ROOT", tmp_path)
    monkeypatch.setattr(workspace, "LOCAL_PATH", local)
    monkeypatch.setattr(workspace, "config", lambda: data)

    first = workspace.import_reference(str(source), "source.sc")
    target = owner / "reference" / "source.sc"
    assert first["copied"] is True
    assert target.read_bytes() == source.read_bytes()

    second = workspace.import_reference(str(source), "source.sc")
    assert second["copied"] is False
    assert second["sha256"] == first["sha256"]

    changed = tmp_path / "changed.sc"
    changed.write_bytes(b"different-checkpoint")
    with pytest.raises(workspace.WorkspaceError, match="new checkpoint name"):
        workspace.import_reference(str(changed), "source.sc")


def test_local_machine_config_may_exist_without_target():
    assert not workspace.has_target({})
    assert not workspace.has_target({"solidcraft": {"cli": "solidcraft-cli"}})
    assert workspace.has_target(
        {
            "solidcraft": {"cli": "solidcraft-cli"},
            "target": {"model": "models/basic/part"},
        }
    )


def test_pr_helper_uses_repository_merge_policy():
    script = (
        Path(__file__).resolve().parents[1] / "scripts" / "pr.ps1"
    ).read_text(encoding="utf-8")
    assert '"pr", "checks", "$PrNumber", "--watch", "--fail-fast"' in script
    assert '"pr", "comment", "$PrNumber", "--body", "/merge"' in script
    assert '"pr", "merge"' not in script


def test_toolchain_dependencies_use_qualified_release_tags():
    dependencies = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "dependencies.repos").read_text(
            encoding="utf-8"
        )
    )["repositories"]

    assert dependencies["mcp"]["version"] == "v0.0.2"
    assert dependencies["forge"]["version"] == "v0.25.0"
    assert all(
        item["version"].startswith("v")
        for item in (dependencies["mcp"], dependencies["forge"])
    )
