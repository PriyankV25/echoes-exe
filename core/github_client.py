"""
Echoes.exe — GitHub Public API Client
Safely fetches public repository metadata, releases, issues, and commit summaries.
Distinguishes between empty data and unavailable/rate-limited data.
"""
import os
import requests
from typing import Dict, Any, List, Optional


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        # GitHub token is optional, increases rate limits from 60/hr to 5000/hr
        self.token = token or os.getenv("GITHUB_TOKEN", "").strip()
        self.session = requests.Session()
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Echoes-Ghost-Archaeologist/1.0"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        self.session.headers.update(headers)

    def get_repo_details(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetches repository metadata from GitHub API."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "status": "available",
                    "name": data.get("name"),
                    "full_name": data.get("full_name"),
                    "description": data.get("description") or "No description provided.",
                    "html_url": data.get("html_url"),
                    "default_branch": data.get("default_branch", "main"),
                    "language": data.get("language"),
                    "stars": data.get("stargazers_count", 0),
                    "forks": data.get("forks_count", 0),
                    "open_issues_count": data.get("open_issues_count", 0),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "pushed_at": data.get("pushed_at"),
                    "archived": data.get("archived", False),
                    "license": data.get("license", {}).get("spdx_id") if data.get("license") else None,
                    "topics": data.get("topics", [])
                }
            elif resp.status_code == 404:
                return {"status": "not_found", "message": "Repository not found or private."}
            elif resp.status_code == 403:
                return {"status": "rate_limited", "message": "GitHub API rate limit reached."}
            else:
                return {"status": "unavailable", "message": f"GitHub returned HTTP {resp.status_code}"}
        except requests.RequestException as e:
            return {"status": "unavailable", "message": f"Network error contacting GitHub API: {str(e)}"}

    def get_releases(self, owner: str, repo: str, limit: int = 5) -> Dict[str, Any]:
        """Fetches releases if available."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/releases"
        try:
            resp = self.session.get(url, params={"per_page": limit}, timeout=10)
            if resp.status_code == 200:
                releases = resp.json()
                items = [
                    {
                        "tag_name": r.get("tag_name"),
                        "name": r.get("name") or r.get("tag_name"),
                        "published_at": r.get("published_at"),
                        "html_url": r.get("html_url"),
                        "prerelease": r.get("prerelease", False)
                    }
                    for r in releases
                ]
                return {
                    "status": "available",
                    "count": len(items),
                    "items": items
                }
            elif resp.status_code == 403:
                return {"status": "rate_limited", "count": None, "items": []}
            else:
                return {"status": "unavailable", "count": None, "items": []}
        except requests.RequestException:
            return {"status": "unavailable", "count": None, "items": []}

    def get_issues(self, owner: str, repo: str, state: str = "open", limit: int = 10) -> Dict[str, Any]:
        """Fetches issues (excluding pull requests)."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/issues"
        try:
            resp = self.session.get(url, params={"state": state, "per_page": limit}, timeout=10)
            if resp.status_code == 200:
                raw_issues = resp.json()
                # Exclude pull requests (GitHub API returns PRs in issues endpoint)
                pure_issues = [
                    {
                        "number": i.get("number"),
                        "title": i.get("title"),
                        "created_at": i.get("created_at"),
                        "updated_at": i.get("updated_at"),
                        "comments_count": i.get("comments", 0),
                        "html_url": i.get("html_url"),
                        "state": i.get("state")
                    }
                    for i in raw_issues if "pull_request" not in i
                ]
                return {
                    "status": "available",
                    "count": len(pure_issues),
                    "items": pure_issues
                }
            elif resp.status_code == 403:
                return {"status": "rate_limited", "count": None, "items": []}
            else:
                return {"status": "unavailable", "count": None, "items": []}
        except requests.RequestException:
            return {"status": "unavailable", "count": None, "items": []}
