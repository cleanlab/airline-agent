import pytest

from airline_agent.util import TestAgent as Agent
from tests.constants import ERROR_MESSAGE
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
def test_expert_guidance(project: Project) -> None:
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
def test_additional_expert_guidance_1(project: Project) -> None:
    question1 = "My flight got canceled how to use my Peace Pass benefit?"
    question2 = "does peace pass still work if trip canceled due to weather?"

    print("QUESTION:", question1)  # noqa: T201
    agent1 = Agent()
    answer1, log_id1 = agent1.chat(question1)
    assert log_id1 is not None
    log1 = wait_and_get_final_log_for(project, log_id1)
    assert_log_guardrail(log1, guardrailed=True)
    assert "disruption assistance" not in (log1.original_assistant_response or "").lower(), ERROR_MESSAGE.format(
        log1.original_assistant_response, "output does NOT mention string 'Disruption Assistance'"
    )

    agent2 = Agent()
    _, log_id2 = agent2.chat(question2)
    assert log_id2 is not None
    log2 = wait_and_get_final_log_for(project, log_id2)
    assert_log_guardrail(log2, guardrailed=True)
    assert "disruption assistance" not in (log2.original_assistant_response or "").lower(), ERROR_MESSAGE.format(
        log2.original_assistant_response, "output does NOT mention string 'Disruption Assistance'"
    )

    guidance_id = project.add_expert_review(
        log1.id,
        is_good=False,
        reason="Peace Pass is another term for Disruption Assistance",
    )
    assert guidance_id is not None
    project.get_guidance(guidance_id)  # wait for guidance to be generated

    disruption_assistance_judge = Judge(
        ["output includes an explanation of Frontier Airlines's Disruption Assistance program"]
    )

    agent3 = Agent()
    answer3, _ = agent3.chat(question1)
    disruption_assistance_judge.assert_judge(answer3)

    agent4 = Agent()
    answer4, _ = agent4.chat(question2)
    disruption_assistance_judge.assert_judge(answer4)
