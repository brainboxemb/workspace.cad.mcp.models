from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass(frozen=True)
class CleanupConfig:
    stable: str
    development: str
    temporary_prefixes: tuple[str, ...]

    @property
    def permanent(self) -> frozenset[str]:
        return frozenset({self.stable, self.development})


def load_config(repo: Path) -> CleanupConfig:
    data = yaml.safe_load((repo / "ci.yml").read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise ValueError("invalid ci.yml")
    branches = data.get("branches")
    if not isinstance(branches, dict):
        raise ValueError("ci.yml branches must be a mapping")
    return CleanupConfig(
        stable=branches["stable"],
        development=branches["development"],
        temporary_prefixes=tuple(branches["temporary_prefixes"]),
    )
