from cad_mcp_workspace_branch_cleanup.config import CleanupConfig
from cad_mcp_workspace_branch_cleanup.policy import eligible_post_merge, is_temporary


CONFIG = CleanupConfig(
    stable="main",
    development="dev",
    temporary_prefixes=("issue/", "fix/", "feature/", "docs/", "chore/"),
)


def test_permanent_branches_are_never_temporary():
    assert not is_temporary("main", CONFIG)
    assert not is_temporary("dev", CONFIG)
    assert is_temporary("issue/1-test", CONFIG)


def test_only_merged_same_repo_temp_to_dev_is_cleanup_candidate():
    assert eligible_post_merge(
        head="issue/1-test",
        base="dev",
        same_repository=True,
        merged=True,
        config=CONFIG,
    )
    assert not eligible_post_merge(
        head="dev",
        base="main",
        same_repository=True,
        merged=True,
        config=CONFIG,
    )
