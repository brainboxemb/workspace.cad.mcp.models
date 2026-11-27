from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

import yaml


class WorkspaceError(RuntimeError):
    pass


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "workspace.yml"
LOCAL_PATH = ROOT / "workspace.local.yml"


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
    repos = data["repositories"]
    for key in ("mcp", "forge", "cad"):
        if not isinstance(repos.get(key), dict):
            raise WorkspaceError(f"workspace.yml missing repository: {key}")
    return data


def local_config(*, required: bool = False) -> dict:
    return _yaml(LOCAL_PATH, required=required)


def _path(value: str) -> Path:
    return (ROOT / value).resolve()


def repo_paths(data: dict) -> dict[str, Path]:
    root = _path(data["paths"].get("repositories", ".repos"))
    return {
        "root": root,
        "mcp": root / "mcp",
        "forge": root / "forge",
        "cad": root / "cad",
    }


def generated_path(data: dict) -> Path:
    return _path(data["paths"].get("generated", ".generated"))


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


def require_clean_toolchain(path: Path) -> None:
    dirty = git(path, "status", "--porcelain", "--untracked-files=no", capture=True)
    if dirty:
        raise WorkspaceError(
            f"{path.name} has tracked modifications; inspect them instead of overwriting"
        )


def ensure_mcp(data: dict, path: Path) -> None:
    spec = data["repositories"]["mcp"]
    url = spec.get("url")
    commit = spec.get("commit")
    if not url or not commit:
        raise WorkspaceError("repositories.mcp requires url and commit")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", url, str(path)])
    require_repo(path, url)
    require_clean_toolchain(path)
    try:
        git(path, "cat-file", "-e", f"{commit}^{{commit}}")
    except WorkspaceError:
        git(path, "fetch", "origin")
    git(path, "checkout", "--detach", commit)
    actual = git(path, "rev-parse", "HEAD", capture=True)
    if actual != commit:
        raise WorkspaceError(f"MCP checkout is {actual}, expected {commit}")


def ensure_forge(data: dict, path: Path) -> None:
    spec = data["repositories"]["forge"]
    url = spec.get("url")
    commit = spec.get("commit")
    if not url or not commit:
        raise WorkspaceError("repositories.forge requires url and commit")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", url, str(path)])
    require_repo(path, url)
    require_clean_toolchain(path)
    try:
        git(path, "cat-file", "-e", f"{commit}^{{commit}}")
    except WorkspaceError:
        git(path, "fetch", "origin")
    git(path, "checkout", "--detach", commit)
    actual = git(path, "rev-parse", "HEAD", capture=True)
    if actual != commit:
        raise WorkspaceError(f"Forge checkout is {actual}, expected {commit}")


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
        run(["git", "clone", "--branch", branch, url, str(path)])
    require_repo(path, url)
    # Never switch, pull, clean or reset an existing CAD worktree.


def install_toolchain(paths: dict[str, Path]) -> None:
    run([sys.executable, "-m", "pip", "install", "-e", str(paths["mcp"])])
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


def generate(data: dict, local: dict) -> dict:
    paths = repo_paths(data)
    relative, owner = target_owner(data, local, paths["cad"])
    cli = solidcraft_cli(local)
    generated = generated_path(data)
    generated.mkdir(parents=True, exist_ok=True)

    command = str(Path(sys.executable).resolve())
    args = [
        "-m",
        "forge_mcp.server",
        "--cad-library",
        str(paths["cad"].resolve()),
        "--model-root",
        relative.as_posix(),
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

    code_workspace = {
        "folders": [{"name": relative.name, "path": str(owner)}],
        "settings": {},
    }
    (generated / "forge-cad.code-workspace").write_text(
        json.dumps(code_workspace, indent=2) + "\n", encoding="utf-8"
    )

    state = {
        "workspace_id": data["workspace"].get("id"),
        "target": relative.as_posix(),
        "cad_repository": str(paths["cad"].resolve()),
        "forge_repository": str(paths["forge"].resolve()),
        "mcp_repository": str(paths["mcp"].resolve()),
        "python": command,
        "solidcraft_cli": cli,
    }
    (generated / "state.json").write_text(
        json.dumps(state, indent=2) + "\n", encoding="utf-8"
    )
    return state


def bootstrap() -> None:
    data = config()
    paths = repo_paths(data)
    paths["root"].mkdir(parents=True, exist_ok=True)
    ensure_mcp(data, paths["mcp"])
    ensure_forge(data, paths["forge"])
    ensure_cad(data, paths["cad"])
    install_toolchain(paths)
    local = local_config(required=False)
    if local:
        state = generate(data, local)
        print(json.dumps({"ready_for_doctor": True, **state}, indent=2))
    else:
        print(json.dumps({
            "ready_for_doctor": False,
            "message": (
                "Toolchain installed. Create workspace.local.yml or run "
                "select-model.ps1, then run doctor.ps1."
            ),
        }, indent=2))


def update() -> None:
    data = config()
    paths = repo_paths(data)
    ensure_mcp(data, paths["mcp"])
    ensure_forge(data, paths["forge"])
    if not paths["cad"].exists():
        ensure_cad(data, paths["cad"])
    else:
        url = data["repositories"]["cad"].get("url")
        if not url:
            raise WorkspaceError("repositories.cad.url is required")
        require_repo(paths["cad"], url)
    install_toolchain(paths)
    local = local_config(required=False)
    if local:
        print(json.dumps(generate(data, local), indent=2))
    else:
        print("toolchain updated; no local target selected")


def doctor() -> None:
    data = config()
    local = local_config(required=True)
    paths = repo_paths(data)
    relative, _ = target_owner(data, local, paths["cad"])
    cli = solidcraft_cli(local)
    run([
        sys.executable,
        "-m",
        "forge_mcp.server",
        "doctor",
        "--cad-library",
        str(paths["cad"].resolve()),
        "--model-root",
        relative.as_posix(),
        "--forge-source",
        str(paths["forge"].resolve()),
        "--solidcraft-cli",
        cli,
    ])


def select(model: str) -> None:
    data = config()
    paths = repo_paths(data)
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
    args = parser.parse_args()
    try:
        if args.command == "bootstrap":
            bootstrap()
        elif args.command == "update":
            update()
        elif args.command == "doctor":
            doctor()
        else:
            select(args.model)
    except WorkspaceError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
