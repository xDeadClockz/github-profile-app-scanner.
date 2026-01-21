from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests


GITHUB_API_URL = "https://api.github.com"


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    pass


def _get_auth_token(explicit_token: Optional[str] = None) -> str:
    """
    Resolve the GitHub token from an explicit argument or the GITHUB_TOKEN env var.
    """
    token = explicit_token or os.getenv("GITHUB_TOKEN")
    if not token:
        raise GitHubAPIError(
            "GitHub token not provided. Use --token or set GITHUB_TOKEN."
        )
    return token


def _build_headers(token: str) -> Dict[str, str]:
    """
    Build HTTP headers for GitHub REST API.
    """
    return {
        "Authorization": f"Bearer {token}",
        # Recommended versioned API header. [web:19][web:22]
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-profile-app-scanner",
    }


def list_app_installations(token: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List GitHub App installations accessible to the user access token. [web:19][web:22]

    Returns a list of installation objects with None used for missing IDs or fields.
    """
    auth_token = _get_auth_token(token)
    headers = _build_headers(auth_token)

    # This endpoint lists app installations accessible to the user access token. [web:22]
    url = f"{GITHUB_API_URL}/user/installations"

    resp = requests.get(url, headers=headers, timeout=10)
    if not resp.ok:
        raise GitHubAPIError(
            f"Failed to list app installations: {resp.status_code} {resp.text}"
        )

    data = resp.json()
    installations = data.get("installations", [])

    normalized: List[Dict[str, Any]] = []
    for inst in installations:
        account = inst.get("account") or {}

        # Normalize with NoneType where entries might be missing.
        normalized.append(
            {
                "installation_id": inst.get("id", None),
                "app_id": inst.get("app_id", None),
                "app_slug": inst.get("app_slug", None),
                "html_url": inst.get("html_url", None),
                "permissions": inst.get("permissions", {}) or {},
                "repository_selection": inst.get("repository_selection", None),
                "created_at": inst.get("created_at", None),
                "updated_at": inst.get("updated_at", None),
                "suspended_at": inst.get("suspended_at", None),
                "target_type": inst.get("target_type", None),
                # Account-level info (user/org)
                "account": {
                    "id": account.get("id", None),
                    "login": account.get("login", None),
                    "type": account.get("type", None),
                    "html_url": account.get("html_url", None),
                },
            }
        )

    return normalized


def list_repositories_for_installation(
    token: Optional[str], installation: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Optional helper: list repositories accessible to a specific installation. [web:20][web:26]

    Requires an installation access token in real-world use, but for simplicity this
    function assumes the user token has appropriate rights and uses the installation's
    repositories_url when available.

    If repositories cannot be listed, returns an empty list.
    """
    auth_token = _get_auth_token(token)
    headers = _build_headers(auth_token)

    repos_url = installation.get("repositories_url")
    if not repos_url:
        # Not provided in our normalized dict; use generic installation endpoint. [web:26]
        inst_id = installation.get("installation_id")
        if inst_id is None:
            return []
        repos_url = f"{GITHUB_API_URL}/user/installations/{inst_id}/repositories"

    resp = requests.get(repos_url, headers=headers, timeout=10)
    if not resp.ok:
        # Do not hard-fail; just return empty so the scanner can still run.
        return []

    data = resp.json()
    repos = data.get("repositories", [])

    normalized_repos: List[Dict[str, Any]] = []
    for repo in repos:
        normalized_repos.append(
            {
                "id": repo.get("id", None),
                "name": repo.get("name", None),
                "full_name": repo.get("full_name", None),
                "private": repo.get("private", None),
                "html_url": repo.get("html_url", None),
            }
        )

    return normalized_repos