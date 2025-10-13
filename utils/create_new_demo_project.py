"""Create a new demo project from an existing official demo project."""

import logging
import os
from typing import TYPE_CHECKING

from codex import Client
from dotenv import load_dotenv

if TYPE_CHECKING:
    from codex.types.projects import ProjectRetrieveResponse

# Official demo project ID to copy configuration from
OFFICIAL_DEMO_PROJECT_ID = ""  # To be filled in

logger = logging.getLogger(__name__)


def main() -> None:
    """Create a new demo project by copying configuration from the official demo project."""
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    # Validate that the official demo project ID is set
    if not OFFICIAL_DEMO_PROJECT_ID:
        missing_id_msg = "OFFICIAL_DEMO_PROJECT_ID must be set in the script"
        raise ValueError(missing_id_msg)

    # Get codex API key from environment
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
        config=existing_project.config,
        name="(Demo) Frontier Airlines Support Chatbot",
        description=existing_project.description,
        organization_id=existing_project.organization_id,
        auto_clustering_enabled=existing_project.auto_clustering_enabled,
    )

    logger.info("Created new demo project: %s (%s)", new_project.name, new_project.id)
    logger.info("Project can be found in organization: %s", new_project.organization_id)
    logger.info("Set CLEANLAB_PROJECT_ID=%s in your .env file", new_project.id)


if __name__ == "__main__":
    main()
