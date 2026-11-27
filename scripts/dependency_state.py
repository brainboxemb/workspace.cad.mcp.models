"""Validate vcs2l-managed external checkouts against dependencies.repos."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

import yaml


class DependencyStateError(RuntimeError):
    """External dependency state is unsafe or invalid."""


def _git(path: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(path), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def _normalize_remote(value: str) -> str:
    value = value.strip().rstrip("/")
    if value.endswith(".git"):
        value = value[:-4]
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.removeprefix("git@github.com:")
    return value.lower()


def load_manifest(path: Path) -> dict[str, dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    repositories = data.get("repositories") if isinstance(data, dict) else None
    if not isinstance(repositories, dict) or not repositories:
        raise DependencyStateError("dependencies.repos must contain repositories")

    result: dict[str, dict] = {}
    for name, spec in repositories.items():
        if not isinstance(name, str) or not name:
            raise DependencyStateError("dependency path must be a non-empty string")
        if not isinstance(spec, dict):
            raise DependencyStateError(f"dependency {name} must be a mapping")
        if spec.get("type") != "git":
            raise DependencyStateError(f"dependency {name} must use git")
        url = spec.get("url")
        version = spec.get("version")
        if not isinstance(url, str) or not url:
            raise DependencyStateError(f"dependency {name} must declare url")
        if not isinstance(version, str) or not version:
            raise DependencyStateError(f"dependency {name} must declare version")
        result[name] = {"url": url, "version": version}
    return result


def checkout_state(root: Path, name: str, spec: dict) -> str:
    path = (root / name).resolve()
    if not (path / ".git").exists():
        return "reconcile"

    origin = _git(path, "remote", "get-url", "origin").stdout.strip()
    if _normalize_remote(origin) != _normalize_remote(spec["url"]):
        raise DependencyStateError(
            f"unexpected origin for external {name}: {origin}"
        )

    dirty = _git(
        path,
        "status",
        "--porcelain",
        "--untracked-files=all",
    ).stdout.strip()
    if dirty:
        raise DependencyStateError(
            f"external {name} has local changes; preserve or remove them before update"
        )

    target = _git(
        path,
        "rev-parse",
        "--verify",
        f"{spec['version']}^{{commit}}",
        check=False,
    )
    if target.returncode != 0:
        return "reconcile"

    head = _git(path, "rev-parse", "HEAD").stdout.strip()
    if head != target.stdout.strip():
        return "reconcile"
    return "current"


def dependency_state(manifest: Path, root: Path) -> str:
    repositories = load_manifest(manifest)
    states = [
        checkout_state(root, name, spec)
        for name, spec in repositories.items()
    ]
    return "current" if all(state == "current" for state in states) else "reconcile"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(dependency_state(args.manifest.resolve(), args.root.resolve()))
    except (DependencyStateError, OSError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
