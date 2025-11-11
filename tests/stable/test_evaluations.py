import pytest
from codex.types.projects import QueryLogListResponse

from airline_agent.util import TestAgent as Agent
from tests.constants import ERROR_MESSAGE
from tests.util import Project, wait_and_get_final_log_for


def assert_failed_eval(log: QueryLogListResponse, eval_name: str) -> None:
    assert log.eval_scores is not None
    score = log.eval_scores[eval_name]
    assert isinstance(score, float)
    assert log.eval_thresholds is not None
    threshold = log.eval_thresholds[eval_name]
    threshold_value = threshold["value"]
    assert isinstance(threshold_value, float)
    threshold_below = threshold.get("direction") == "below"
    error_msg = ERROR_MESSAGE.format(log.original_assistant_response, f"{eval_name} threshold")
    if threshold_below:
        assert score < threshold_value, error_msg
    else:
        assert score > threshold_value, error_msg


@pytest.mark.main
def test_evaluation_1(project: Project) -> None:
    query = "Where did Frontier Airlines name come from?"
    print(query) # noqa: T201
    agent = Agent()
    _, log_id = agent.chat(query)
    assert log_id is not None
    log = wait_and_get_final_log_for(project, log_id)
    assert_failed_eval(log, "context_sufficiency")
