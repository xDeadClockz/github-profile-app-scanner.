from __future__ import annotations

from typing import Any, Dict, List, Optional


def _permission_risk_score(permissions: Dict[str, str]) -> int:
    """
    Simple heuristic: write > read > none.
    """
    score = 0
    for resource, level in permissions.items():
        level = (level or "").lower()
        if level == "write":
            score += 3
        elif level == "read":
            score += 1
        elif level == "admin":
            score += 5
    return score


def classify_installation_risk(installation: Dict[str, Any]) -> str:
    """
    Classify an installation into 'low', 'medium', or 'high' risk based on permissions
    and repository selection. [web:26]
    """
    permissions: Dict[str, str] = installation.get("permissions", {}) or {}
    repo_selection: Optional[str] = installation.get("repository_selection")

    score = _permission_risk_score(permissions)

    if repo_selection == "all":
        score += 3  # broader scope, slightly higher risk

    if score >= 10:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


def build_report(installations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build a simple report for each installation with risk classification.
    """
    report: List[Dict[str, Any]] = []
    for inst in installations:
        account = inst.get("account") or {}
        risk = classify_installation_risk(inst)

        report.append(
            {
                "installation_id": inst.get("installation_id", None),
                "app_id": inst.get("app_id", None),
                "app_slug": inst.get("app_slug", None),
                "app_url": inst.get("html_url", None),
                "account_login": account.get("login", None),
                "account_type": account.get("type", None),
                "repository_selection": inst.get("repository_selection", None),
                "risk": risk,
            }
        )
    return report