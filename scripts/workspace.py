from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import yaml


class WorkspaceError(RuntimeError):
    pass


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "workspace.yml"
LOCAL_PATH = ROOT / "workspace.local.yml"
MODEL_SECTIONS = frozenset({"basic", "components", "subassemblies", "assemblies"})
MODEL_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
WORKBENCH_DIR = ".workbench"


def _yaml(path: Path, *, required: bool = True) -> dict:
    if not path.is_file():
        if required:
            raise WorkspaceError(f"missing configuration: {path.name}")
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise WorkspaceError(f"{path.name} must be a schema: 1 mapping")
    return data


def config() -> dict:
    data = _yaml(CONFIG_PATH)
    for key in ("workspace", "environment", "repositories", "solidcraft", "paths"):
        if not isinstance(data.get(key), dict):
            raise WorkspaceError(f"workspace.yml missing mapping: {key}")
    cad = data["repositories"].get("cad")
    if not isinstance(cad, dict):
        raise WorkspaceError("workspace.yml missing repository: cad")
    return data


def local_config(*, required: bool = False) -> dict:
    return _yaml(LOCAL_PATH, required=required)


def selected_target_kind(local: dict) -> str | None:
    target = local.get("target")
    if not isinstance(target, dict):
        return None
    model = bool(target.get("model"))
    workbench = bool(target.get("workbench"))
    if model and workbench:
        raise WorkspaceError(
            "target must contain exactly one of model or workbench"
        )
    if model:
        return "catalog"
    if workbench:
        return "workbench"
    return None


def has_target(local: dict) -> bool:
    return selected_target_kind(local) is not None


def _path(value: str) -> Path:
    return (ROOT / value).resolve()


def workspace_paths(data: dict) -> dict[str, Path]:
    externals = _path(data["paths"].get("externals", "ext"))
    return {
        "mcp": externals / "mcp",
        "forge": externals / "forge",
        "cad": _path(data["paths"].get("cad", ".repos/cad")),
        "generated": _path(data["paths"].get("generated", ".generated")),
    }


def run(args: list[str], *, cwd: Path | None = None, capture: bool = False) -> str:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=capture,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = ""
        if isinstance(exc, subprocess.CalledProcessError):
            detail = (exc.stderr or exc.stdout or "").strip()
        suffix = f": {detail}" if detail else ""
        raise WorkspaceError(f"command failed: {' '.join(args)}{suffix}") from exc
    return result.stdout.strip() if capture else ""


def git(path: Path, *args: str, capture: bool = False) -> str:
    return run(["git", "-C", str(path), *args], capture=capture)


def _same_remote(actual: str, configured: str) -> bool:
    def normalize(value: str) -> str:
        value = value.strip().rstrip("/")
        if value.endswith(".git"):
            value = value[:-4]
        if value.startswith("git@github.com:"):
            value = "https://github.com/" + value.removeprefix("git@github.com:")
        return value.lower()

    return normalize(actual) == normalize(configured)


def require_repo(path: Path, url: str) -> None:
    if not (path / ".git").exists():
        raise WorkspaceError(f"expected Git checkout: {path}")
    actual = git(path, "remote", "get-url", "origin", capture=True)
    if not _same_remote(actual, url):
        raise WorkspaceError(f"unexpected origin for {path.name}: {actual}")


def require_external_toolchain(paths: dict[str, Path]) -> None:
    for name in ("mcp", "forge"):
        path = paths[name]
        if not (path / ".git").is_dir():
            raise WorkspaceError(
                f"missing external checkout: {path}; run scripts/import-dependencies.ps1"
            )


def ensure_cad(data: dict, path: Path) -> None:
    spec = data["repositories"]["cad"]
    url = spec.get("url")
    branch = spec.get("branch")
    if not url:
        raise WorkspaceError(
            "set repositories.cad.url in workspace.yml before bootstrap"
        )
    if not branch:
        raise WorkspaceError("repositories.cad.branch is required")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        run([
            "git",
            "clone",
            "--single-branch",
            "--filter=blob:none",
            "--branch",
            branch,
            url,
            str(path),
        ])
    require_repo(path, url)
    # Never switch, pull, clean or reset an existing CAD worktree.


def install_toolchain(paths: dict[str, Path]) -> None:
    require_external_toolchain(paths)
    run([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        str(paths["mcp"]),
    ])
    run([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        str(paths["forge"] / "cadlib"),
    ])


def model_relative(value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise WorkspaceError("target.model must be a non-empty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise WorkspaceError("target.model must stay inside the CAD repository")
    if not path.parts or path.parts[0] != "models":
        raise WorkspaceError("target.model must be an exact owner below models/")
    return path


def workbench_name(value: str) -> str:
    if not isinstance(value, str) or not MODEL_ID_RE.fullmatch(value):
        raise WorkspaceError(
            "workbench name must contain lowercase letters, digits and hyphens"
        )
    return value


def workbench_root(name: str) -> Path:
    return (ROOT / WORKBENCH_DIR / workbench_name(name)).resolve()


def new_model_relative(value: str) -> Path:
    path = model_relative(value)
    if len(path.parts) != 3 or path.parts[1] not in MODEL_SECTIONS:
        raise WorkspaceError(
            "new model must be models/<basic|components|subassemblies|assemblies>/<owner>"
        )
    return path


def _cad_work_branch(data: dict, cad: Path) -> str:
    branch = git(cad, "branch", "--show-current", capture=True)
    if not branch:
        raise WorkspaceError("CAD repository must be on a named work branch")
    development = data["repositories"]["cad"].get("branch")
    if branch in {"main", development}:
        raise WorkspaceError(
            "create a short-lived CAD work branch before creating a model owner"
        )
    dirty = git(cad, "status", "--porcelain", capture=True)
    if dirty:
        raise WorkspaceError(
            "CAD worktree must be clean before creating a new model owner"
        )
    return branch


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_model(
    model: str,
    model_id: str,
    title: str,
    priority: int = 100,
) -> dict:
    data = config()
    paths = workspace_paths(data)
    cad = paths["cad"]
    if not cad.is_dir():
        raise WorkspaceError("CAD repository is not bootstrapped yet")
    url = data["repositories"]["cad"].get("url")
    if not url:
        raise WorkspaceError("repositories.cad.url is required")
    require_repo(cad, url)
    branch = _cad_work_branch(data, cad)

    relative = new_model_relative(model)
    if not MODEL_ID_RE.fullmatch(model_id):
        raise WorkspaceError("model id must contain lowercase letters, digits and hyphens")
    if not isinstance(title, str) or not title.strip():
        raise WorkspaceError("title must be non-empty")
    if isinstance(priority, bool) or not isinstance(priority, int) or priority < 0:
        raise WorkspaceError("priority must be a non-negative integer")

    owner = (cad / relative).resolve()
    if owner.exists():
        raise WorkspaceError("new model owner already exists")

    section = relative.parts[1]
    owner.mkdir(parents=True)
    model_data = {
        "purpose": ["example"],
        "section": section,
        "priority": priority,
        "title": title.strip(),
        "tagline": "New Forge model",
        "description": "New Forge model authored through the CAD MCP workspace.",
        "parameters": "To be defined",
        "stages": ["Author Forge source", "Verify with SolidCraft"],
    }
    ci_data = {
        "schema": 1,
        "id": model_id,
        "builder": "forge",
        "source": "scpf/model.py",
        "process": True,
    }
    (owner / "model.yml").write_text(
        yaml.safe_dump(model_data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (owner / "ci.yml").write_text(
        yaml.safe_dump(ci_data, sort_keys=False),
        encoding="utf-8",
    )

    existing = local_config(required=False)
    cli = None
    if isinstance(existing.get("solidcraft"), dict):
        cli = existing["solidcraft"].get("cli")
    payload = {
        "schema": 1,
        "target": {"model": relative.as_posix()},
        "solidcraft": {"cli": cli or "solidcraft-cli"},
    }
    LOCAL_PATH.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )
    state = generate(data, payload)
    return {
        "created": True,
        "branch": branch,
        "model": relative.as_posix(),
        "model_id": model_id,
        "files": [
            f"{relative.as_posix()}/model.yml",
            f"{relative.as_posix()}/ci.yml",
        ],
        "source_expected": f"{relative.as_posix()}/scpf/model.py",
        "state": state,
    }


def create_workbench(name: str) -> dict:
    data = config()
    normalized = workbench_name(name)
    owner = workbench_root(normalized)
    if owner.exists():
        raise WorkspaceError("local workbench already exists")
    owner.mkdir(parents=True)
    project = {
        "schema": 1,
        "forge": {"source": "scpf/model.py"},
        "solidcraft": {"connect": "auto"},
        "evidence": {
            "enabled": True,
            "log": "build/session.jsonl",
            "render": "build/live/model.png",
        },
    }
    (owner / "project.yml").write_text(
        yaml.safe_dump(project, sort_keys=False),
        encoding="utf-8",
    )

    existing = local_config(required=False)
    cli = None
    if isinstance(existing.get("solidcraft"), dict):
        cli = existing["solidcraft"].get("cli")
    payload = {
        "schema": 1,
        "target": {"workbench": normalized},
        "solidcraft": {"cli": cli or "solidcraft-cli"},
    }
    LOCAL_PATH.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )
    state = generate(data, payload)
    return {
        "created": True,
        "workbench": normalized,
        "root": str(owner),
        "project": "project.yml",
        "source_expected": "scpf/model.py",
        "state": state,
    }


def target_binding(
    data: dict,
    local: dict,
    paths: dict[str, Path],
) -> dict:
    target = local.get("target")
    if not isinstance(target, dict):
        raise WorkspaceError("workspace.local.yml missing target mapping")
    model = target.get("model")
    workbench = target.get("workbench")
    if bool(model) == bool(workbench):
        raise WorkspaceError(
            "target must contain exactly one of model or workbench"
        )

    if model:
        relative, owner = target_owner(data, local, paths["cad"])
        return {
            "kind": "catalog",
            "name": relative.name,
            "root": owner,
            "target": relative.as_posix(),
            "server_args": [
                "--cad-library",
                str(paths["cad"].resolve()),
                "--model-root",
                relative.as_posix(),
            ],
        }

    normalized = workbench_name(workbench)
    owner = workbench_root(normalized)
    if not owner.is_dir():
        raise WorkspaceError(
            "target.workbench must identify an existing local workbench"
        )
    return {
        "kind": "workbench",
        "name": normalized,
        "root": owner,
        "target": f"workbench:{normalized}",
        "server_args": ["--workspace", str(owner)],
    }


def import_reference(source: str, name: str | None = None) -> dict:
    data = config()
    local = local_config(required=True)
    paths = workspace_paths(data)
    owner = target_binding(data, local, paths)["root"]

    source_path = Path(source).expanduser().resolve()
    if not source_path.is_file() or source_path.suffix.lower() != ".sc":
        raise WorkspaceError("source must be an existing SolidCraft .sc file")

    filename = name or source_path.name
    if Path(filename).name != filename or not filename.lower().endswith(".sc"):
        raise WorkspaceError("reference name must be one .sc filename")

    reference = owner / "reference"
    reference.mkdir(parents=True, exist_ok=True)
    target = reference / filename
    source_hash = _sha256(source_path)

    if target.exists():
        if not target.is_file():
            raise WorkspaceError("reference destination is not a file")
        target_hash = _sha256(target)
        if target_hash != source_hash:
            raise WorkspaceError(
                "reference already exists with different content; use a new checkpoint name"
            )
        return {
            "copied": False,
            "path": target.relative_to(owner).as_posix(),
            "sha256": target_hash,
            "bytes": target.stat().st_size,
        }

    with source_path.open("rb") as src, target.open("xb") as dst:
        shutil.copyfileobj(src, dst)
    target_hash = _sha256(target)
    if target_hash != source_hash:
        target.unlink(missing_ok=True)
        raise WorkspaceError("reference copy hash mismatch")

    return {
        "copied": True,
        "path": target.relative_to(owner).as_posix(),
        "sha256": target_hash,
        "bytes": target.stat().st_size,
    }


def target_owner(data: dict, local: dict, cad: Path) -> tuple[Path, Path]:
    target = local.get("target")
    if not isinstance(target, dict):
        raise WorkspaceError("workspace.local.yml missing target mapping")
    relative = model_relative(target.get("model"))
    owner = (cad / relative).resolve()
    try:
        owner.relative_to(cad.resolve())
    except ValueError as exc:
        raise WorkspaceError("target.model escapes the CAD repository") from exc
    if not owner.is_dir() or not (owner / "model.yml").is_file():
        raise WorkspaceError(
            "target.model must identify an existing owner containing model.yml"
        )
    return relative, owner


def solidcraft_cli(local: dict) -> str:
    solidcraft = local.get("solidcraft")
    if not isinstance(solidcraft, dict) or not solidcraft.get("cli"):
        raise WorkspaceError("workspace.local.yml missing solidcraft.cli")
    return str(solidcraft["cli"])


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def write_codex_workbench_config(
    owner: Path,
    command: str,
    args: list[str],
) -> Path:
    config_dir = owner / ".codex"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.toml"
    content = (
        "[mcp_servers.forgeCad]\n"
        f"command = {_toml_string(command)}\n"
        "args = [\n"
        + "".join(f"  {_toml_string(arg)},\n" for arg in args)
        + "]\n"
    )
    config_path.write_text(content, encoding="utf-8")
    return config_path


def generate(data: dict, local: dict) -> dict:
    paths = workspace_paths(data)
    binding = target_binding(data, local, paths)
    owner = binding["root"]
    cli = solidcraft_cli(local)
    generated = paths["generated"]
    generated.mkdir(parents=True, exist_ok=True)

    command = str(Path(sys.executable).resolve())
    args = [
        "-m",
        "forge_mcp.server",
        *binding["server_args"],
        "--forge-source",
        str(paths["forge"].resolve()),
        "--solidcraft-cli",
        cli,
    ]
    mcp = {
        "mcpServers": {
            "forgeCad": {
                "type": "stdio",
                "command": command,
                "args": args,
                "tools": ["*"],
            }
        }
    }
    (generated / "mcp-config.json").write_text(
        json.dumps(mcp, indent=2) + "\n", encoding="utf-8"
    )

    codex_config = None
    if binding["kind"] == "workbench":
        codex_config = write_codex_workbench_config(owner, command, args)

    code_workspace = {
        "folders": [{"name": binding["name"], "path": str(owner)}],
        "settings": {
            "python.defaultInterpreterPath": command,
        },
    }
    (generated / "forge-cad.code-workspace").write_text(
        json.dumps(code_workspace, indent=2) + "\n", encoding="utf-8"
    )

    state = {
        "workspace_id": data["workspace"].get("id"),
        "target_kind": binding["kind"],
        "target": binding["target"],
        "target_root": str(owner),
        "cad_repository": (
            str(paths["cad"].resolve())
            if binding["kind"] == "catalog"
            else None
        ),
        "forge_repository": str(paths["forge"].resolve()),
        "mcp_repository": str(paths["mcp"].resolve()),
        "python": command,
        "solidcraft_cli": cli,
        "codex_config": str(codex_config) if codex_config is not None else None,
    }
    (generated / "state.json").write_text(
        json.dumps(state, indent=2) + "\n", encoding="utf-8"
    )
    return state


def bootstrap() -> None:
    data = config()
    paths = workspace_paths(data)
    require_external_toolchain(paths)
    install_toolchain(paths)
    local = local_config(required=False)
    kind = selected_target_kind(local)
    if kind == "catalog":
        ensure_cad(data, paths["cad"])
    if kind is not None:
        state = generate(data, local)
        print(json.dumps({"ready_for_doctor": True, **state}, indent=2))
    else:
        print(json.dumps({
            "ready_for_doctor": False,
            "message": (
                "Toolchain installed. No target is selected yet; run "
                "create-workbench.ps1, create-model.ps1 or select-model.ps1, "
                "then run doctor.ps1."
            ),
        }, indent=2))


def update() -> None:
    data = config()
    paths = workspace_paths(data)
    require_external_toolchain(paths)
    install_toolchain(paths)
    local = local_config(required=False)
    kind = selected_target_kind(local)
    if kind == "catalog":
        ensure_cad(data, paths["cad"])
    if kind is not None:
        print(json.dumps(generate(data, local), indent=2))
    else:
        print("toolchain updated; no local target selected")


def doctor() -> None:
    data = config()
    local = local_config(required=True)
    paths = workspace_paths(data)
    require_external_toolchain(paths)
    binding = target_binding(data, local, paths)
    cli = solidcraft_cli(local)
    run([
        sys.executable,
        "-m",
        "forge_mcp.server",
        "doctor",
        *binding["server_args"],
        "--forge-source",
        str(paths["forge"].resolve()),
        "--solidcraft-cli",
        cli,
    ])


def select(model: str) -> None:
    data = config()
    paths = workspace_paths(data)
    existing = local_config(required=False)
    if not paths["cad"].is_dir():
        raise WorkspaceError("CAD repository is not bootstrapped yet")
    relative = model_relative(model)
    owner = (paths["cad"] / relative).resolve()
    if not owner.is_dir() or not (owner / "model.yml").is_file():
        raise WorkspaceError(
            "selected model must be an existing owner containing model.yml"
        )
    cli = None
    if isinstance(existing.get("solidcraft"), dict):
        cli = existing["solidcraft"].get("cli")
    payload = {
        "schema": 1,
        "target": {"model": relative.as_posix()},
        "solidcraft": {"cli": cli or "solidcraft-cli"},
    }
    LOCAL_PATH.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )
    state = generate(data, payload)
    print(json.dumps(state, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage a local Forge CAD MCP workspace")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("bootstrap")
    sub.add_parser("update")
    sub.add_parser("doctor")
    select_parser = sub.add_parser("select")
    select_parser.add_argument("--model", required=True)
    create_parser = sub.add_parser("create-model")
    create_parser.add_argument("--model", required=True)
    create_parser.add_argument("--id", required=True)
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--priority", type=int, default=100)
    workbench_parser = sub.add_parser("create-workbench")
    workbench_parser.add_argument("--name", required=True)
    reference_parser = sub.add_parser("import-reference")
    reference_parser.add_argument("--source", required=True)
    reference_parser.add_argument("--name")
    args = parser.parse_args()
    try:
        if args.command == "bootstrap":
            bootstrap()
        elif args.command == "update":
            update()
        elif args.command == "doctor":
            doctor()
        elif args.command == "select":
            select(args.model)
        elif args.command == "create-model":
            print(json.dumps(create_model(args.model, args.id, args.title, args.priority), indent=2))
        elif args.command == "create-workbench":
            print(json.dumps(create_workbench(args.name), indent=2))
        else:
            print(json.dumps(import_reference(args.source, args.name), indent=2))
    except WorkspaceError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
