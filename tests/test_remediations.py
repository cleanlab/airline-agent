from tests.judge import Judge, assert_judge
from tests.util import Agent, Project, wait_and_get_final_log_for


def test_expert_answer(project: Project) -> None:
    question = "Who founded Frontier Airlines?"
    answer = 'Frontier Airlines was founded by Frederick W. "Rick" Brown, Janice Brown, and Bob Schulman in 1994.'

    agent1 = Agent()
    answer1, _ = agent1.chat(question)
    assert answer1 != answer
    assert_judge(["output does not reflect knowledge of who founded Frontier Airlines"], answer1)

    project.add_expert_answer(question, answer)

    agent2 = Agent()
    answer2, _ = agent2.chat(question)
    assert answer2 == answer

    agent3 = Agent()
    question2 = "list the founders of Frontier Airlines"
    answer3, _ = agent3.chat(question2)
    assert answer3 == answer


def test_expert_review(project: Project) -> None:
    question1 = "Whats the maximum time we might be stuck on the tarmac without being let off"
    question2 = "Whats the maximum time we might be stuck on the tarmac without being let off"

    agent1 = Agent()
    _, log_id1 = agent1.chat(question1)
    assert log_id1 is not None
    log1 = wait_and_get_final_log_for(project, log_id1)
    project.add_expert_review(log1.id, is_good=False)

    agent2 = Agent()
    _, log_id2 = agent2.chat(question2)
    assert log_id2 is not None
    log2 = wait_and_get_final_log_for(project, log_id2)
    assert log2.guardrailed


def test_ai_guidance(project: Project) -> None:
    question1 = "My flight got canceled how to use my Peace Pass benefit?"
    question2 = "does peace pass still work if trip canceled due to weather?"

    agent1 = Agent()
    answer1, log_id1 = agent1.chat(question1)
    assert log_id1 is not None
    idk_judge = Judge(["output does NOT include an explanation of Frontier Airlines's Disruption Assistance program"])
    idk_judge.assert_judge(answer1)
    agent2 = Agent()
    answer2, _ = agent2.chat(question2)
    idk_judge.assert_judge(answer2)

    log1 = wait_and_get_final_log_for(project, log_id1)
    guidance_id = project.add_expert_review(
        log1.id, is_good=False, reason="Peace Pass is another term for Disruption Assistance"
    )
    assert guidance_id is not None
    project.get_draft_guidance(guidance_id)  # wait for guidance to be generated
    project.publish_guidance(guidance_id)

    agent3 = Agent()
    answer3, _ = agent3.chat(question2)
    disruption_assistance_judge = Judge(
        ["output includes an explanation of Frontier Airlines's Disruption Assistance program"]
    )
    disruption_assistance_judge.assert_judge(answer3)

    agent4 = Agent()
    answer4, _ = agent4.chat(question1)
    disruption_assistance_judge.assert_judge(answer4)


def test_additional_ai_guidance(project: Project) -> None:
    question1 = "can i bring a dog with me on a flight?"
    question2 = "can i bring my emotional support dog with me on a domestic flight?"

    agent1 = Agent()
    answer1, log_id1 = agent1.chat(question1)
    assert log_id1 is not None
    no_clarifying_judge = Judge(
        [
            "output does NOT ask a clarifying question about whether the user is asking about a domestic or international flight"
        ]
    )
    no_clarifying_judge.assert_judge(answer1)
    agent2 = Agent()
    answer2, _ = agent2.chat(question2)
    no_clarifying_judge.assert_judge(answer2)

    log1 = wait_and_get_final_log_for(project, log_id1)
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
    answer7, _ = agent5.chat(question2)
    no_clarifying_judge.assert_judge(answer7)
