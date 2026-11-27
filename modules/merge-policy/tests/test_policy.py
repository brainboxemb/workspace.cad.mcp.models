import unittest
from unittest.mock import patch

from cad_mcp_workspace_merge_policy.__main__ import (
    pull_request_paths,
    require_green_ci,
)
from cad_mcp_workspace_merge_policy.policy import (
    MergePolicyError,
    merge_method,
    stable_main_paths,
)


class PolicyTests(unittest.TestCase):
    def test_feature_to_dev_is_squash(self):
        self.assertEqual(merge_method(head="issue/1-change", base="dev"), "squash")

    def test_dev_to_main_is_merge(self):
        self.assertEqual(merge_method(head="dev", base="main"), "merge")

    def test_main_to_dev_is_merge(self):
        self.assertEqual(merge_method(head="main", base="dev"), "merge")

    def test_stable_control_doc_to_main_is_squash(self):
        self.assertEqual(
            merge_method(
                head="issue/1-plan",
                base="main",
                changed_paths=("docs/plan.md",),
            ),
            "squash",
        )
        self.assertEqual(
            merge_method(
                head="docs/handoff-refresh",
                base="main",
                changed_paths=("docs/plan.md", "docs/handoff.md"),
            ),
            "squash",
        )

    def test_feature_to_main_is_rejected(self):
        for paths in (
            (),
            ("README.md",),
            ("docs/plan.md", "README.md"),
        ):
            with self.subTest(paths=paths):
                with self.assertRaises(MergePolicyError):
                    merge_method(
                        head="issue/1-change",
                        base="main",
                        changed_paths=paths,
                    )

    def test_stable_main_paths_normalize_and_reject_mixed_content(self):
        self.assertTrue(stable_main_paths(("./docs/plan.md",)))
        self.assertTrue(
            stable_main_paths((r"docs\plan.md", r"docs\handoff.md"))
        )
        self.assertFalse(stable_main_paths(()))
        self.assertFalse(stable_main_paths(("docs/plan.md", "src/tool.py")))

    @patch("cad_mcp_workspace_merge_policy.__main__.api")
    def test_pull_request_paths_reads_every_page(self, api):
        api.side_effect = [
            [{"filename": f"docs/file-{index}.md"} for index in range(100)],
            [{"filename": "docs/plan.md"}],
        ]
        paths = pull_request_paths("owner/repo", 7, 101, "token")
        self.assertEqual(len(paths), 101)
        self.assertEqual(paths[-1], "docs/plan.md")
        self.assertEqual(api.call_count, 2)

    @patch("cad_mcp_workspace_merge_policy.__main__.api")
    def test_pull_request_paths_rejects_incomplete_listing(self, api):
        api.side_effect = [
            [{"filename": "docs/plan.md"}],
            [],
        ]
        with self.assertRaisesRegex(
            MergePolicyError,
            "complete pull request file list",
        ):
            pull_request_paths("owner/repo", 7, 2, "token")

    @patch("cad_mcp_workspace_merge_policy.__main__.api")
    def test_latest_pr_ci_must_be_green(self, api):
        api.return_value = {
            "check_runs": [
                {
                    "id": 1,
                    "name": "ci",
                    "status": "completed",
                    "conclusion": "failure",
                    "pull_requests": [{"number": 7}],
                },
                {
                    "id": 2,
                    "name": "ci",
                    "status": "completed",
                    "conclusion": "success",
                    "pull_requests": [{"number": 7}],
                },
            ]
        }
        require_green_ci("owner/repo", "sha", 7, "token")


if __name__ == "__main__":
    unittest.main()
