"""Create a new demo project from an existing official demo project."""

import logging
import os
from typing import TYPE_CHECKING

from codex import Client
from dotenv import find_dotenv, load_dotenv, set_key

if TYPE_CHECKING:
    from codex.types import ProjectRetrieveResponse

# Official demo project ID to copy configuration from
OFFICIAL_DEMO_PROJECT_ID = "3aae1f96-2dda-492f-8c86-17d453d3c298"
logger = logging.getLogger(__name__)


def main() -> None:
    """Create a new demo project by copying configuration from the official demo project."""
    logging.basicConfig(level=logging.INFO)
    load_dotenv(override=True)

    codex_api_key = os.getenv("CODEX_API_KEY")
    if not codex_api_key:
        missing_key_msg = "CODEX_API_KEY environment variable is not set"
        raise ValueError(missing_key_msg)

    logger.info("Using official demo project ID: %s", OFFICIAL_DEMO_PROJECT_ID)

    client = Client(api_key=codex_api_key)

    # Retrieve the existing project configuration
    try:
        existing_project: ProjectRetrieveResponse = client.projects.retrieve(project_id=OFFICIAL_DEMO_PROJECT_ID)
    except Exception as err:
        retrieve_error_msg = f"Failed to retrieve project {OFFICIAL_DEMO_PROJECT_ID}: {err}"
        raise ValueError(retrieve_error_msg) from err

    # Create a new project with the same configuration
    new_project = client.projects.create(
        config=existing_project.config,  # type: ignore[arg-type]
        name="(Demo) Frontier Airlines Support Chatbot",
        description=existing_project.description,
        organization_id=existing_project.organization_id,
        auto_clustering_enabled=existing_project.auto_clustering_enabled or False,
    )

    set_key(find_dotenv(), "CLEANLAB_PROJECT_ID", new_project.id)

    logger.info("Created new demo project: %s (%s)", new_project.name, new_project.id)
    logger.info("Project can be found in organization: %s", new_project.organization_id)
    logger.info("Set CLEANLAB_PROJECT_ID=%s in your .env file", new_project.id)


if __name__ == "__main__":
    main()
