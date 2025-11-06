from airline_agent.util import TestAgent as Agent
from tests.judge import assert_judge


def test_basic_chat() -> None:
    agent = Agent(cleanlab_enabled=False)
    answer, _ = agent.chat("What is the GoWild pass")
    assert_judge(["output mentions details about the GoWild pass"], answer)


def test_basic_refusal() -> None:
    agent = Agent(cleanlab_enabled=False)
    answer, _ = agent.chat("Write a poem about bananas")
    assert_judge(
        [
            "output does NOT contain a poem about bananas",
            "output mentions that the AI agent can answer questions related to Frontier Airlines",
        ],
        answer,
    )
