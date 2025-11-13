import time
from collections.abc import Callable
from typing import Any

from cleanlab_codex import Client
from cleanlab_codex import Project as CodexProject
from codex.types.projects import QueryLogListResponse


class Project:
    __test__ = False

    def __init__(self, codex_project: CodexProject, codex_client: Client) -> None:
        self._project = codex_project
        self._client = codex_client
        self._sdk_client = self._client._client  # noqa: SLF001

    @property
    def codex_project(self) -> CodexProject:
        return self._project

    def logs(self) -> list[QueryLogListResponse]:
        return list(self._sdk_client.projects.query_logs.list(self._project.id))

    def add_expert_answer(self, question: str, answer: str) -> None:
        self._sdk_client.projects.remediations.create(self._project.id, question=question, answer=answer)

    def add_expert_review(self, log_id: str, *, is_good: bool, reason: str | None = None) -> str | None:
        status = "good" if is_good else "bad"
        body = {"status": status}
        if not is_good:
            body["explanation"] = reason if reason is not None else ""
        response = self._sdk_client.post(
            f"/api/projects/{self._project.id}/query_logs/{log_id}/expert_review?generate_guidance=true",
            body=body,
            cast_to=dict[str, Any],
        )
        return response.get("ai_guidance_id")

    def get_draft_guidance(self, guidance_id: str) -> str:
        while True:
            response = self._sdk_client.get(
                f"/api/projects/{self._project.id}/guidance_remediations/{guidance_id}",
                cast_to=dict[str, Any],
            )
            pending = response["pending"]
            assert isinstance(pending, bool)
            if not pending:
                draft_guidance = response.get("draft_guidance")
                assert isinstance(draft_guidance, str)
                return draft_guidance
            time.sleep(0.5)

    def publish_guidance(self, guidance_id: str) -> None:
        self._sdk_client.patch(
            f"/api/projects/{self._project.id}/guidance_remediations/{guidance_id}/publish", cast_to=dict[str, Any]
        )


def find[T](iterable: list[T], predicate: Callable[[T], bool]) -> T:
    for item in iterable:
        if predicate(item):
            return item
    msg = "no item found matching predicate"
    raise ValueError(msg)


def wait_until(predicate: Callable[[], bool], *, poll_interval: float = 1.0, timeout: float = 30.0) -> None:
    start_time = time.time()
    while True:
        if predicate():
            return
        if time.time() - start_time > timeout:
            msg = "timeout waiting for predicate to be true"
            raise TimeoutError(msg)
        time.sleep(poll_interval)


def project_has_log_with_id(project: Project, log_id: str) -> Callable[[], bool]:
    def predicate() -> bool:
        logs = project.logs()
        try:
            find(logs, lambda log: log.id == log_id)
        except ValueError:
            return False
        else:
            return True

    return predicate


def wait_and_get_final_log_for(project: Project, log_id: str) -> QueryLogListResponse:
    wait_until(project_has_log_with_id(project, log_id))
    logs = project.logs()
    return find(logs, lambda log: log.id == log_id)
