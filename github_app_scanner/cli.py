from __future__ import annotations

import argparse
import sys
from typing import Optional

from . import api, scanner


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="GitHub Profile App Scanner: list and scan GitHub App installations."
    )
    parser.add_argument(
        "--token",
        dest="token",
        help="GitHub personal access token (or set GITHUB_TOKEN env var).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full JSON report instead of a table.",
    )
    return parser.parse_args(argv)


def _print_table(report: list[dict]) -> None:
    """
    Pretty-print a simple text table.
    """
    if not report:
        print("No app installations found.")
        return

    headers = [
        "Installation ID",
        "App Slug",
        "Account",
        "Account Type",
        "Repo Selection",
        "Risk",
    ]

    rows = []
    for item in report:
        rows.append(
            [
                str(item.get("installation_id", None)),
                str(item.get("app_slug", None)),
                str(item.get("account_login", None)),
                str(item.get("account_type", None)),
                str(item.get("repository_selection", None)),
                str(item.get("risk", None)),
            ]
        )

    # Compute column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    def format_row(row_vals: list[str]) -> str:
        return " | ".join(
            val.ljust(col_widths[i]) for i, val in enumerate(row_vals)
        )

    # Print header
    print(format_row(headers))
    print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))

    # Print rows
    for row in rows:
        print(format_row(row))


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)

    try:
        installations = api.list_app_installations(token=args.token)
    except api.GitHubAPIError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

    report = scanner.build_report(installations)

    if args.json:
        import json

        print(json.dumps(report, indent=2))
    else:
        _print_table(report)


if __name__ == "__main__":
    main()