import pytest

from airline_agent.util import TestAgent as Agent
from tests.judge import Judge, assert_judge
from tests.util import Project, assert_log_guardrail, wait_and_get_final_log_for


@pytest.mark.main
def test_expert_answer(project: Project) -> None:
    question = "tell me about the bogo promo going on right now"
    answer = "Frontier offers a BOGO promo: if you fly on your birthday, you can get a free companion ticket using promo code BOGOF9 (taxes, fees, and availability apply). For more questions on this promo specifically, please reach out to Frontier staff at 801-401-9000."

    agent1 = Agent()
    print("QUESTION:", question)  # noqa: T201
    _, log_id1 = agent1.chat(question)
    assert log_id1 is not None
    log = wait_and_get_final_log_for(project, log_id1)
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


@pytest.mark.additional
def test_additional_expert_answer_1(project: Project) -> None:
    question = "Is the viral promo code FLYFREE25 legitimate?"
    answer = "Yes, “FLYFREE25” is a legitimate promo code tied to our June 25, 2025 anniversary and is valid only on that day. The first 50 eligible domestic Economy round-trip bookings receive a $0 base fare (taxes apply)."

    agent1 = Agent()
    print("QUESTION:", question)  # noqa: T201
    _, log_id1 = agent1.chat(question)
    assert log_id1 is not None
    log = wait_and_get_final_log_for(project, log_id1)
    assert_judge(
        ["output says it cannot verify the legitimacy of the promo code"],
        log.original_assistant_response,
    )

    project.add_expert_answer(question, answer)

    agent2 = Agent()
    answer2, _ = agent2.chat(question)
    assert answer2 == answer

    agent3 = Agent()
    question2 = "is your promo code FLYFREE25 legit?"
    answer3, _ = agent3.chat(question2)
    assert answer3 == answer


@pytest.mark.main
def test_expert_review(project: Project) -> None:
    question1 = (
        "does frontier reserve the right to cancel the miles program at any time. if so, do i risk losing all my miles?"
    )
    question2 = (
        "Does Frontier have the right to cancel the miles program at any time? Could i risk losing all my miles?"
    )

    agent1 = Agent()
    print("QUESTION:", question1)  # noqa: T201
    answer1, log_id1 = agent1.chat(question1)
    assert log_id1 is not None
    log1 = wait_and_get_final_log_for(project, log_id1)
    assert_log_guardrail(log1, guardrailed=False)
    assert_judge(
        ["output suggests there is a risk of losing miles"],
        answer1,
    )
    project.add_expert_review(log1.id, is_good=False)

    agent2 = Agent()
    _, log_id2 = agent2.chat(question2)
    assert log_id2 is not None
    log2 = wait_and_get_final_log_for(project, log_id2)
    assert_log_guardrail(log2, guardrailed=True)


@pytest.mark.additional
def test_additional_expert_review_1(project: Project) -> None:
    question1 = "Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else"
    question2 = "Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else"

    agent1 = Agent()
    print("QUESTION:", question1)  # noqa: T201
    answer1, log_id1 = agent1.chat(question1)
    assert log_id1 is not None
    log1 = wait_and_get_final_log_for(project, log_id1)
    assert_log_guardrail(log1, guardrailed=False)
    assert_judge(
        [
            "output DOES identify the maximum time you might be stuck on the tarmac without being let off for a domestic flight"
        ],
        answer1,
    )
    project.add_expert_review(log1.id, is_good=False)

    agent2 = Agent()
    _, log_id2 = agent2.chat(question2)
    assert log_id2 is not None
    log2 = wait_and_get_final_log_for(project, log_id2)
    assert_log_guardrail(log2, guardrailed=True)


@pytest.mark.main
def test_ai_guidance(project: Project) -> None:
    question1 = "what is the cheapest Frontier flight from SFO to NYC on 11/11?"
    question2 = "when is the earliest Frontier flight from NYC to OAK on 11/15?"

    print("QUESTION:", question1)  # noqa: T201
    agent1 = Agent()
    _, log_id1 = agent1.chat(question1)
    assert log_id1 is not None
    log1 = wait_and_get_final_log_for(project, log_id1)
    assert_judge(
        ["output does NOT identify a flight that costs $80.84"],
        log1.original_assistant_response,
    )

    agent2 = Agent()
    _, log_id2 = agent2.chat(question2)
    assert log_id2 is not None
    log2 = wait_and_get_final_log_for(project, log_id2)
    assert_judge(
        ["output does NOT identify that the earliest flight is from EWR to OAK"],
        log2.original_assistant_response,
    )

    guidance_id = project.add_expert_review(
        log1.id,
        is_good=False,
        reason="when the user uses NYC as an airport code, consider the three major New York area airports",
    )
    assert guidance_id is not None
    project.get_guidance(guidance_id)  # wait for guidance to be generated

    agent3 = Agent()
    answer3, _ = agent3.chat(question1)
    assert_judge(["output says that the cheapest Frontier flight is $80.84"], answer3)

    agent4 = Agent()
    answer4, _ = agent4.chat(question2)
    assert_judge(["output identifies that the earliest flight is from EWR to OAK"], answer4)


@pytest.mark.additional
def test_additional_ai_guidance_1(project: Project) -> None:
    question1 = "can i bring a dog with me on a flight?"
    question2 = "can i bring my emotional support dog with me on a domestic flight?"

    print("QUESTION:", question1)  # noqa: T201
    agent1 = Agent()
    answer1, log_id1 = agent1.chat(question1)
    assert log_id1 is not None
    log1 = wait_and_get_final_log_for(project, log_id1)
    assert_log_guardrail(log1, guardrailed=False)
    incomplete_judge = Judge(
        [
            (
                "output does NOT provide BOTH requirements TOGETHER for:\n"
                "- specific requirements for pets on domestic flights (e.g., pet age minimums, carrier size or type, weight limits), AND\n"
                "- specific requirements for service animals on international flights (e.g., documentation rules, CDC Dog Import Form receipt, microchip proof, vaccination requirements).\n\n"
                "stating that service dogs are allowed do NOT count as providing requirements."
            )
        ]
    )
    incomplete_judge.assert_judge(answer1)
    agent2 = Agent()
    answer2, log_id2 = agent2.chat(question2)
    assert log_id2 is not None
    log2 = wait_and_get_final_log_for(project, log_id2)
    assert_log_guardrail(log2, guardrailed=False)
    incomplete_judge.assert_judge(answer2)

    guidance_id = project.add_expert_review(
        log1.id,
        is_good=False,
        reason="""Answer depends if flight is international and if it's a service animal. Should have clarified with user, and then used info from all relevant articles: always use the "do you allow pets on plane" article, then if international/service animal, also the "service animals" article""",
    )
    assert guidance_id is not None
    project.get_guidance(guidance_id)  # wait for guidance to be generated

    agent3 = Agent()
    answer3, log_id3 = agent3.chat(question1)
    assert log_id3 is not None
    log3 = wait_and_get_final_log_for(project, log_id3)
    assert_log_guardrail(log3, guardrailed=False)
    clarifying_judge = Judge(
        [
            (
                "output either (a) asks the user to clarify BOTH if the flight is domestic or international"
                "AND whether the animal is a pet or a service animal, "
                "OR (b) provides information for only one case and clearly instructs the user to specify if the other case applies"
            )
        ]
    )
    clarifying_judge.assert_judge(answer3)
    answer4, log_id4 = agent3.chat("its an international flight. and its a service animal")
    assert log_id4 is not None
    log4 = wait_and_get_final_log_for(project, log_id4)
    assert_log_guardrail(log4, guardrailed=False)
    assert_judge(
        ["output describes the requirements of service dogs on Frontier Airlines international flights"], answer4
    )

    agent4 = Agent()
    answer5, log_id5 = agent4.chat(question1)
    assert log_id5 is not None
    log5 = wait_and_get_final_log_for(project, log_id5)
    assert_log_guardrail(log5, guardrailed=False)
    clarifying_judge.assert_judge(answer5)
    answer6, log_id6 = agent4.chat("its a domestic flight. and its a house pet")
    assert log_id6 is not None
    log6 = wait_and_get_final_log_for(project, log_id6)
    assert_log_guardrail(log6, guardrailed=False)
    assert_judge(
        [
            "output states that domesticated dogs are allowed on domestic flights with Frontier Airlines",
            "output describes the requirements for bringing a dog on board a Frontier Airlines domestic flight",
        ],
        answer6,
    )

    agent5 = Agent()
    answer7, log_id7 = agent5.chat(question2)
    assert log_id7 is not None
    log7 = wait_and_get_final_log_for(project, log_id7)
    assert_log_guardrail(log7, guardrailed=False)
    assert_judge(
        [
            (
                "output DOES provide BOTH requirements TOGETHER for:\n"
                "- specific requirements for pets on domestic flights (e.g., pet age minimums, carrier size or type, weight limits), AND\n"
                "- specific requirements for service animals on international flights (e.g., documentation rules, CDC Dog Import Form receipt, microchip proof, vaccination requirements).\n\n"
                "stating that service dogs are allowed do NOT count as providing requirements."
            )
        ],
        answer7,
    )
