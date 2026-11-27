from __future__ import annotations

import json
from urllib import error, parse, request


class GitHubClient:
    def __init__(self, repository: str, token: str):
        self.repository = repository
        self.token = token

    def _request(self, path: str, *, method: str = "GET"):
        req = request.Request(
            f"https://api.github.com/repos/{self.repository}/{path}",
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with request.urlopen(req) as response:
                if response.status == 204:
                    return None
                return json.load(response)
        except error.HTTPError as exc:
            if method == "DELETE" and exc.code in {404, 422}:
                return None
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API {exc.code}: {detail}") from exc

    def branches(self):
        return [item["name"] for item in self._request("branches?per_page=100")]

    def open_pr_exists(self, branch):
        owner = self.repository.split("/", 1)[0]
        head = parse.quote(f"{owner}:{branch}", safe="")
        return bool(self._request(f"pulls?state=open&head={head}&per_page=100"))

    def merged_pr_to(self, branch, base):
        owner = self.repository.split("/", 1)[0]
        head = parse.quote(f"{owner}:{branch}", safe="")
        base = parse.quote(base, safe="")
        values = self._request(
            f"pulls?state=closed&head={head}&base={base}&per_page=100"
        )
        return any(item.get("merged_at") for item in values)

    def delete_branch(self, branch):
        encoded = parse.quote(branch, safe="")
        self._request(f"git/refs/heads/{encoded}", method="DELETE")
