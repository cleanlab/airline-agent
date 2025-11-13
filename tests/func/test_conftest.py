import uuid

from tests.util import Project


def test_conftest(project: Project) -> None:
    uuid.UUID(project.codex_project.id, version=4)
