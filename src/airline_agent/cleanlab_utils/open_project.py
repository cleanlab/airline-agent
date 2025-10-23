"""Utilities to open the configured Cleanlab Codex project in a browser."""

import os
import sys
import webbrowser
from uuid import UUID

from dotenv import load_dotenv

PROJECT_URL_TEMPLATE = "https://codex.cleanlab.ai/projects/{project_id}"


def build_project_url(project_id: str) -> str:
    return PROJECT_URL_TEMPLATE.format(project_id=project_id)


def normalize_project_id(project_id: str) -> str:
    """Return the canonical UUID string for the provided project ID."""
    try:
        return str(UUID(project_id))
    except ValueError as exc:
        msg = f"CLEANLAB_PROJECT_ID is not a valid UUID: {project_id!r}"
        raise ValueError(msg) from exc


def main() -> None:
    """Open the configured Cleanlab Codex project in the default browser."""
    load_dotenv()
    project_id = os.getenv("CLEANLAB_PROJECT_ID")
    if not project_id:
        msg = "CLEANLAB_PROJECT_ID environment variable is not set"
        raise ValueError(msg)

    canonical_project_id = normalize_project_id(project_id)
    project_url = build_project_url(canonical_project_id)
    if not webbrowser.open(project_url, new=2):
        print(f"Navigate to {project_url}", file=sys.stderr)  # noqa: T201


if __name__ == "__main__":
    main()
