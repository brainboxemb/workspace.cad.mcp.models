class MergePolicyError(RuntimeError):
    pass


_STABLE_MAIN_PATHS = frozenset({"docs/plan.md", "docs/handoff.md"})


def stable_main_paths(paths) -> bool:
    normalized = {
        str(path).replace("\\", "/").removeprefix("./")
        for path in paths
    }
    return bool(normalized) and normalized <= _STABLE_MAIN_PATHS


def merge_method(*, head: str, base: str, changed_paths=()) -> str:
    if base == "dev" and head not in {"main", "dev"}:
        return "squash"
    if (head, base) in {("dev", "main"), ("main", "dev")}:
        return "merge"
    if (
        base == "main"
        and head not in {"main", "dev"}
        and stable_main_paths(changed_paths)
    ):
        return "squash"
    raise MergePolicyError(f"unsupported branch integration: {head} -> {base}")
