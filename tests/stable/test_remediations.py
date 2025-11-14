import pytest

from airline_agent.util import TestAgent as Agent
from tests.judge import Judge, assert_judge
from tests.util import Project, assert_log_guardrail


@pytest.mark.main
def test_expert_answer(project: Project) -> None:
    question = "tell me about the bogo promo going on right now"
    answer = "Frontier offers a BOGO promo: if you fly on your birthday, you can get a free companion ticket using promo code BOGOF9 (taxes, fees, and availability apply). For more questions on this promo specifically, please reach out to Frontier staff at 801-401-9000."

    agent1 = Agent()
    print("QUESTION:", question)  # noqa: T201
    _, log_id1 = agent1.chat(question)
    log = assert_log_guardrail(project, log_id1, guardrailed=True)
    assert_judge(
        ["output says that information about the bogo promo is NOT available"],
        log.original_assistant_response,
    )

    project.add_expert_answer(question, answer)

    agent2 = Agent()
    answer2, _ = agent2.chat(question)
    assert answer2 == answer

    agent3 = Agent()
    question2 = "i heard about a bogo promo whats that about"
    answer3, _ = agent3.chat(question2)
    assert answer3 == answer


@pytest.mark.main
def test_expert_review(project: Project) -> None:
    question1 = "Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else"
    question2 = "Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else"

    agent1 = Agent()
    print("QUESTION:", question1)  # noqa: T201
    answer1, log_id1 = agent1.chat(question1)
    log1 = assert_log_guardrail(project, log_id1, guardrailed=False)
    assert_judge(
        [
            "output DOES identify the maximum time you might be stuck on the tarmac without being let off for a domestic flight"
        ],
        answer1,
    )
    project.add_expert_review(log1.id, is_good=False)

    agent2 = Agent()
    _, log_id2 = agent2.chat(question2)
    assert_log_guardrail(project, log_id2, guardrailed=True)


@pytest.mark.main
def test_ai_guidance(project: Project) -> None:
    question1 = "what is the cheapest Frontier flight from SFO to NYC on 11/11?"
    question2 = "when is the earliest Frontier flight from NYC to OAK on 11/15?"

    print("QUESTION:", question1)  # noqa: T201
    agent1 = Agent()
    answer1, log_id1 = agent1.chat(question1)
    log1 = assert_log_guardrail(project, log_id1, guardrailed=False)
    assert_judge(
        ["output does NOT identify a flight that costs $80.84"],
        answer1,
    )

    agent2 = Agent()
    answer2, log_id2 = agent2.chat(question2)
    assert_log_guardrail(project, log_id2, guardrailed=False)
    assert_judge(
        ["output does NOT identify that the earliest flight is from EWR to OAK"],
        answer2,
    )

    guidance_id = project.add_expert_review(
        log1.id,
        is_good=False,
        reason="when the user uses NYC as an airport code, consider the three major New York area airports",
    )
    assert guidance_id is not None
    project.get_draft_guidance(guidance_id)  # wait for guidance to be generated
    project.publish_guidance(guidance_id)

    agent3 = Agent()
    answer3, _ = agent3.chat(question1)
    assert_judge(["output says that the cheapest Frontier flight is $80.84"], answer3)

    agent4 = Agent()
    answer4, _ = agent4.chat(question2)
    assert_judge(["output identifies that the earliest flight is from EWR to OAK"], answer4)


@pytest.mark.additional
def test_additional_ai_guidance(project: Project) -> None:
    question1 = "can i bring a dog with me on a flight?"
    question2 = "can i bring my emotional support dog with me on a domestic flight?"

    print("QUESTION:", question1)  # noqa: T201
    agent1 = Agent()
    answer1, log_id1 = agent1.chat(question1)
    log1 = assert_log_guardrail(project, log_id1, guardrailed=False)
    no_clarifying_judge = Judge(
        [
            "output does NOT ask a clarifying question about whether the user is asking about a domestic or international flight"
        ]
    )
    no_clarifying_judge.assert_judge(answer1)
    agent2 = Agent()
    answer2, log_id2 = agent2.chat(question2)
    assert_log_guardrail(project, log_id2, guardrailed=False)
    no_clarifying_judge.assert_judge(answer2)

    guidance_id = project.add_expert_review(
        log1.id,
        is_good=False,
        reason="""Answer depends if flight is international and if it's a service animal. Should have clarified with user, and then used info from all relevant articles: always use the "do you allow pets on plane" article, then if international/service animal, also the "service animals" article""",
    )
    assert guidance_id is not None
    project.get_draft_guidance(guidance_id)  # wait for guidance to be generated
    project.publish_guidance(guidance_id)

    agent3 = Agent()
    answer3, _ = agent3.chat(question1)
    clarifying_judge = Judge(
        ["output asks a clarifying question about whether the user is asking about a domestic or international flight"]
    )
    clarifying_judge.assert_judge(answer3)
    answer4, _ = agent3.chat("its an international flight. and its a service animal")
    assert_judge(
        ["output describes the requirements of service dogs on Frontier Airlines international flights"], answer4
    )

    agent4 = Agent()
    answer5, _ = agent4.chat(question1)
    clarifying_judge.assert_judge(answer5)
    answer6, _ = agent4.chat("its a domestic flight. and its a house pet")
    assert_judge(
        [
            "output states that domesticated dogs are allowed on domestic flights with Frontier Airlines",
            "output describes the requirements for bringing a dog on board a Frontier Airlines domestic flight",
        ],
        answer6,
    )

    agent5 = Agent()
    answer7, log_id7 = agent5.chat(question2)
    assert_log_guardrail(project, log_id7, guardrailed=False)
    no_clarifying_judge.assert_judge(answer7)
