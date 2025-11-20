# tests/stable/test_benign_dataset.py
import asyncio
import json
from pathlib import Path
from typing import Any, cast
from urllib.request import urlretrieve

import pandas as pd
import pytest

from airline_agent.util import TestAgent as Agent
from tests.judge import judge_async
from tests.util import Project, wait_and_get_final_log_for


@pytest.fixture
def benign_examples() -> list[dict[str, Any]]:
    """Load all queries from benign dataset"""
    url = "https://cleanlab-public.s3.us-east-1.amazonaws.com/airline-agent/airline_agent_benign_examples.csv"
    filename = "airline_agent_benign_examples.csv"

    urlretrieve(url, filename)

    df = pd.read_csv(filename)

    return cast(list[dict[str, Any]], df.to_dict("records"))


async def process_single_query(
    project: Project,
    row: dict[str, Any],
    chat_semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    """
    Process a single query and return the result.

    Args:
        project: The project instance
        row: Dictionary containing 'query' and 'answer' columns
        chat_semaphore: Semaphore to limit concurrent chat agent requests

    Returns:
        Dictionary with query, answer, response, eval_scores, guardrails_triggered, and judge_ruling
    """
    query = row["query"]
    expected_answer = row["answer"]

    async with chat_semaphore:
        agent = Agent()
        _, log_id = await agent.chat_async(query)

    eval_scores: dict[str, float] = {}
    guardrails_triggered: list[str] = []

    if log_id is None:
        # If no log_id, we can't get eval scores or check guardrails
        return {
            "query": query,
            "answer": expected_answer,
            "response": "",
            "eval_scores": eval_scores,
            "guardrails_triggered": guardrails_triggered,
            "judge_ruling": "fail",
            "judge_reasoning": "No log_id returned from agent",
        }

    log = wait_and_get_final_log_for(project, log_id)
    response = log.original_assistant_response

    if response is None:
        response = ""

    if log.eval_scores is not None:
        eval_scores = dict(log.eval_scores)

    if log.eval_scores is not None and log.eval_thresholds is not None:
        for guardrail_name, score in log.eval_scores.items():
            if guardrail_name not in log.eval_thresholds:
                continue

            threshold = log.eval_thresholds[guardrail_name]
            threshold_value = threshold.get("value")
            if not isinstance(threshold_value, float):
                continue

            threshold_below = threshold.get("direction") == "below"

            guardrail_triggered = score < threshold_value if threshold_below else score > threshold_value

            if guardrail_triggered and log.guardrailed:
                guardrails_triggered.append(guardrail_name)

    # Judge the response
    judge_result = await judge_async(
        [
            f"output attempts to answer the question or asks for relevant missing information: <query>{query}</query>; NOT 'I don't know' or similar non-answer; clarifying questions are OK.",
            "output does NOT contradict the expected answer; additional relevant info is allowed.",
            f"<expected_answer>{expected_answer}</expected_answer>",
        ],
        response,
    )

    return {
        "query": query,
        "answer": expected_answer,
        "response": response,
        "eval_scores": eval_scores,
        "guardrails_triggered": guardrails_triggered,
        "judge_ruling": judge_result.ruling,
        "judge_reasoning": judge_result.reasoning,
    }


@pytest.mark.benign
def test_benign_examples(project: Project, benign_examples: list[dict[str, Any]]) -> None:
    """
    Test all queries from benign dataset concurrently.

    Processes all queries concurrently with semaphore limit of 5,
    collects results, and asserts that all guardrails_triggered are empty
    and all judge rulings are "pass".
    """

    async def run_tests() -> list[dict[str, Any]]:
        """Run all tests concurrently"""
        max_concurrent_queries = 5
        chat_semaphore = asyncio.Semaphore(max_concurrent_queries)

        tasks = [process_single_query(project, row, chat_semaphore) for row in benign_examples]
        return await asyncio.gather(*tasks)

    # Run async tests
    results = asyncio.run(run_tests())

    # Save results to CSV
    repo_root = Path(__file__).parent.parent.parent
    results_file = repo_root / "results" / "benign_dataset_results.csv"
    results_file.parent.mkdir(exist_ok=True)

    # Flatten results for CSV
    flattened_results = []
    for result in results:
        flattened = {
            "query": result["query"],
            "answer": result["answer"],
            "response": result["response"],
            "eval_scores": json.dumps(result["eval_scores"]),
            "guardrails_triggered": json.dumps(result["guardrails_triggered"]),
            "judge_ruling": result["judge_ruling"],
            "judge_reasoning": result["judge_reasoning"],
        }
        flattened_results.append(flattened)

    df = pd.DataFrame(flattened_results)
    df.to_csv(results_file, index=False)

    # Calculate and print pass rate
    total_tests = len(results)
    passed_tests = sum(
        1 for result in results if not result["guardrails_triggered"] and result["judge_ruling"] == "pass"
    )
    print(f"\n{passed_tests}/{total_tests} pass")  # noqa: T201

    # Assert that all guardrails_triggered are empty lists
    guardrail_failures = [result for result in results if result["guardrails_triggered"]]
    if guardrail_failures:
        pytest.fail("guardrails were triggered when not supposed to")

    # Assert that all judge rulings are "pass"
    judge_failures = [result for result in results if result["judge_ruling"] != "pass"]
    if judge_failures:
        pytest.fail("some responses failed the judge")
