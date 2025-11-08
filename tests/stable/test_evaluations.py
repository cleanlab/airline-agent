import pytest
from codex.types.projects import QueryLogListResponse

from tests.util import Agent, Project, wait_and_get_final_log_for


def assert_failed_eval(log: QueryLogListResponse, eval_name: str) -> None:
    assert log.eval_scores is not None
    score = log.eval_scores[eval_name]
    assert isinstance(score, float)
    assert log.eval_thresholds is not None
    threshold = log.eval_thresholds[eval_name]
    threshold_value = threshold["value"]
    assert isinstance(threshold_value, float)
    threshold_below = threshold.get("direction") == "below"
    assistant_msg = f"Original Assistant Response: {log.original_assistant_response}"
    if threshold_below:
        assert score < threshold_value, assistant_msg
    else:
        assert score > threshold_value, assistant_msg


@pytest.mark.main
def test_evaluation_1(project: Project) -> None:
    question = "Where did Frontier Airlines name come from?"
    agent = Agent()
    _, log_id = agent.chat(question)
    assert log_id is not None
    log = wait_and_get_final_log_for(project, log_id)
    assert_failed_eval(log, "context_sufficiency")
    assert_failed_eval(log, "response_helpfulness")
