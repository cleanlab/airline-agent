"""Utilities to open the configured Cleanlab Codex project in a browser."""

import os
import sys
import webbrowser

from dotenv import load_dotenv

PROJECT_URL_TEMPLATE = "https://codex.cleanlab.ai/projects/{project_id}"


def build_project_url(project_id: str) -> str:
    return PROJECT_URL_TEMPLATE.format(project_id=project_id)


def main() -> None:
    """Open the configured Cleanlab Codex project in the default browser."""
    load_dotenv()
    project_id = os.getenv("CLEANLAB_PROJECT_ID")
    if not project_id:
        msg = "CLEANLAB_PROJECT_ID environment variable is not set"
        raise ValueError(msg)

    project_url = build_project_url(project_id)
    if not webbrowser.open(project_url, new=2):
        print(f"Navigate to {project_url}", file=sys.stderr)  # noqa: T201


if __name__ == "__main__":
    main()
