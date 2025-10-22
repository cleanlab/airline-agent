"""Create a new demo project from an existing official demo project."""

import argparse
import logging
import os

import httpx
from cleanlab_codex import Client
from codex.types.project_return_schema import ProjectReturnSchema
from dotenv import load_dotenv

from airline_agent.constants import OFFICIAL_DEMO_PROJECT_ID

DEFAULT_DEMO_PROJECT_NAME = "(Demo) Frontier Airlines Support Chatbot"
DEFAULT_DEMO_PROJECT_DESCRIPTION = "Do not delete please!"
COPY_PROJECT_ROUTE = "https://api-codex.cleanlab.ai/api/admin/projects/copy_project_settings"
logger = logging.getLogger(__name__)


def copy_project_configuration(new_project_id: str, api_key: str) -> ProjectReturnSchema:
    with httpx.Client(headers={"X-API-Key": api_key}) as client:
        response = client.patch(
            COPY_PROJECT_ROUTE,
            params={
                "project_id": OFFICIAL_DEMO_PROJECT_ID,
                "new_project_id": new_project_id,
            },
        )
        response.raise_for_status()
        return ProjectReturnSchema.model_validate(response.json())


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

    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    codex_api_key = os.getenv("CODEX_API_KEY")
    if not codex_api_key:
        missing_key_msg = "CODEX_API_KEY environment variable is not set"
        raise ValueError(missing_key_msg)

    logger.info("Using official demo project ID: %s", OFFICIAL_DEMO_PROJECT_ID)

    codex_client = Client(api_key=codex_api_key)

    new_project = codex_client.create_project(
        name=args.name,
        description=args.description,
    )

    new_project_with_updated_config = copy_project_configuration(new_project.id, codex_api_key)

    logger.info(
        "Created new demo project: %s (%s)",
        new_project_with_updated_config.name,
        new_project_with_updated_config.id,
    )
    logger.info(
        "Project can be found in organization: %s",
        new_project_with_updated_config.organization_id,
    )
    logger.info(
        "Set CLEANLAB_PROJECT_ID=%s in your .env file",
        new_project_with_updated_config.id,
    )


if __name__ == "__main__":
    main()
