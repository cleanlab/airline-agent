import os
from collections.abc import Generator
from unittest.mock import patch

import pytest
from cleanlab_codex import Client

from airline_agent.constants import OFFICIAL_DEMO_PROJECT_ID
from tests.util import Project


@pytest.fixture(scope="session")
def codex_client() -> Client:
    codex_api_key = os.getenv("CODEX_API_KEY")
    return Client(api_key=codex_api_key)


@pytest.fixture
def project(codex_client: Client) -> Generator[Project]:
    new_project = codex_client.create_project_from_template(
        template_project_id=OFFICIAL_DEMO_PROJECT_ID,
        name="(automated test) Demo Project",
        description="Created for automated testing purposes, can be deleted / should be automatically deleted after tests complete.",
    )
    prev_cleanlab_project_id = os.getenv("CLEANLAB_PROJECT_ID")
    os.environ["CLEANLAB_PROJECT_ID"] = new_project.id
    with patch("airline_agent.backend.services.airline_chat.project", new_project):
        yield Project(new_project, codex_client)
    if prev_cleanlab_project_id is not None:
        os.environ["CLEANLAB_PROJECT_ID"] = prev_cleanlab_project_id
    else:
        os.environ.pop("CLEANLAB_PROJECT_ID")
    codex_client._client.projects.delete(new_project.id)  # noqa: SLF001
