from .config import CleanupConfig


def is_temporary(branch: str, config: CleanupConfig) -> bool:
    return branch not in config.permanent and branch.startswith(config.temporary_prefixes)


def eligible_post_merge(*, head, base, same_repository, merged, config):
    return (
        merged
        and same_repository
        and base == config.development
        and is_temporary(head, config)
    )


def eligible_sweep(
    *, branch, has_open_pr, has_merged_pr_to_development, config
):
    return (
        is_temporary(branch, config)
        and not has_open_pr
        and has_merged_pr_to_development
    )
