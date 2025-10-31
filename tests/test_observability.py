from tests.judge import assert_judge
from tests.util import Agent, Project, wait_and_get_final_log_for


def test_observability(project: Project) -> None:
    question = "Can I bring my cat on a domestic flight?"
    agent = Agent()
    answer, log_id = agent.chat(question)
    assert_judge(["output confirms that cats are allowed on domestic flights"], answer)
    assert log_id is not None
    log = wait_and_get_final_log_for(project, log_id)
    assert not log.is_bad_response


def test_observability_2(project: Project) -> None:
    question = "My flight got canceled, can I get a refund?"
    agent = Agent()
    answer, log_id = agent.chat(question)
    assert_judge(["output explains the refund policy for canceled flights"], answer)
    assert log_id is not None
    log = wait_and_get_final_log_for(project, log_id)
    assert not log.is_bad_response


def test_observability_3(project: Project) -> None:
    question = "Max carry-on size for domestic flight?"
    agent = Agent()
    answer, log_id = agent.chat(question)
    assert_judge(["output provides the maximum carry-on size for domestic flights on Frontier Airlines"], answer)
    assert log_id is not None
    log = wait_and_get_final_log_for(project, log_id)
    assert not log.is_bad_response
