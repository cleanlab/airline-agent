import pytest

from airline_agent.util import TestAgent as Agent
from tests.judge import assert_judge
from tests.util import Project, assert_log_guardrail, wait_and_get_final_log_for


@pytest.mark.main
def test_observability_1(project: Project) -> None:
    question = "Can I bring my cat on a domestic flight?"
    print("QUESTION:", question)  # noqa: T201
    agent = Agent()
    answer, log_id = agent.chat(question)
    assert log_id is not None
    log = wait_and_get_final_log_for(project, log_id)
    assert_log_guardrail(log, guardrailed=False)
    assert_judge(["output confirms that cats are allowed on domestic flights"], answer)


@pytest.mark.main
def test_observability_2(project: Project) -> None:
    question = "My flight got canceled, can I get a refund?"
    print("QUESTION:", question)  # noqa: T201
    agent = Agent()
    answer, log_id = agent.chat(question)
    assert log_id is not None
    log = wait_and_get_final_log_for(project, log_id)
    log = assert_log_guardrail(log, guardrailed=False)
    assert_judge(["output explains the refund policy for canceled flights"], answer)


@pytest.mark.main
def test_observability_3(project: Project) -> None:
    question = "Max carry-on size for domestic flight?"
    print("QUESTION:", question)  # noqa: T201
    agent = Agent()
    answer, log_id = agent.chat(question)
    assert log_id is not None
    log = wait_and_get_final_log_for(project, log_id)
    log = assert_log_guardrail(log, guardrailed=False)
    assert_judge(["output provides the maximum carry-on size for domestic flights on Frontier Airlines"], answer)
