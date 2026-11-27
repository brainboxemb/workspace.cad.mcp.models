import unittest
from unittest.mock import patch

from cad_mcp_workspace_merge_policy.__main__ import require_green_ci
from cad_mcp_workspace_merge_policy.policy import MergePolicyError, merge_method


class PolicyTests(unittest.TestCase):
    def test_feature_to_dev_is_squash(self):
        self.assertEqual(merge_method(head="issue/1-change", base="dev"), "squash")

    def test_dev_to_main_is_merge(self):
        self.assertEqual(merge_method(head="dev", base="main"), "merge")

    def test_main_to_dev_is_merge(self):
        self.assertEqual(merge_method(head="main", base="dev"), "merge")

    def test_feature_to_main_is_rejected(self):
        with self.assertRaises(MergePolicyError):
            merge_method(head="issue/1-change", base="main")

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
