"""Create a new demo project from an existing official demo project."""

import argparse
import logging
import os

from cleanlab_codex import Client
from dotenv import load_dotenv

from airline_agent.constants import OFFICIAL_DEMO_PROJECT_ID

DEFAULT_DEMO_PROJECT_NAME = "(Demo) Frontier Airlines Support Chatbot"
DEFAULT_DEMO_PROJECT_DESCRIPTION = "Do not delete please!"
logger = logging.getLogger(__name__)


def main() -> None:
    """Create a new demo project by copying configuration from the official demo project."""
    parser = argparse.ArgumentParser(
        description="Create a new demo project by copying configuration from the official demo project."
    )
    parser.add_argument(
        "--name",
        type=str,
        default=DEFAULT_DEMO_PROJECT_NAME,
        help="Name of the new demo project",
    )
    parser.add_argument(
        "--description",
        type=str,
        default=DEFAULT_DEMO_PROJECT_DESCRIPTION,
        help="Description of the new demo project",
    )
    args = parser.parse_args()

    load_dotenv()

    codex_api_key = os.getenv("CODEX_API_KEY")
    if not codex_api_key:
        missing_key_msg = "CODEX_API_KEY environment variable is not set"
        raise ValueError(missing_key_msg)

    codex_client = Client(api_key=codex_api_key)

    new_project = codex_client.create_project_from_template(
        template_project_id=OFFICIAL_DEMO_PROJECT_ID,
        name=args.name,
        description=args.description,
    )

    print("Demo project created!")  # noqa: T201
    print(  # noqa: T201
        f"Set CLEANLAB_PROJECT_ID={new_project.id} in your .env file."
    )


if __name__ == "__main__":
    main()
