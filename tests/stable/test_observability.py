import pytest

from airline_agent.util import TestAgent as Agent
from tests.judge import assert_judge
from tests.util import Project, assert_log_guardrail


@pytest.mark.main
def test_observability(project: Project) -> None:
    question = "Can I bring my cat on a domestic flight?"
    print("QUESTION:", question)  # noqa: T201
    agent = Agent()
    answer, log_id = agent.chat(question)
    assert log_id is not None
    assert_log_guardrail(project, log_id, guardrailed=False)
    assert_judge(["output confirms that cats are allowed on domestic flights"], answer)


@pytest.mark.main
def test_observability_2(project: Project) -> None:
    question = "My flight got canceled, can I get a refund?"
    print("QUESTION:", question)  # noqa: T201
    agent = Agent()
    answer, log_id = agent.chat(question)
    assert log_id is not None
    assert_log_guardrail(project, log_id, guardrailed=False)
    assert_judge(["output explains the refund policy for canceled flights"], answer)


@pytest.mark.main
def test_observability_3(project: Project) -> None:
    question = "Max carry-on size for domestic flight?"
    print("QUESTION:", question)  # noqa: T201
    agent = Agent()
    answer, log_id = agent.chat(question)
    assert log_id is not None
    assert_log_guardrail(project, log_id, guardrailed=False)
    assert_judge(["output provides the maximum carry-on size for domestic flights on Frontier Airlines"], answer)
