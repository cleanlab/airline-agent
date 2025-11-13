from textwrap import dedent
from typing import Literal

from pydantic import BaseModel
from pydantic_ai import Agent

from tests.constants import ERROR_MESSAGE

JUDGE_MODEL = "openai:gpt-5-mini"


class Verdict(BaseModel):
    reasoning: str
    ruling: Literal["pass", "fail"]


class Judge:
    _INSTRUCTION_TEMPLATE = dedent("""
    <role>
    You are an LLM judge evaluating an output of an AI agent under test to determine if it meets a specified criteria.
    </role>

    <criteria>
    {criteria}
    </criteria>

    <rules>
    - Make your ruling based solely on the provided criteria, returning "pass" if the output meets ALL criteria, otherwise "fail".
    - Provide a clear and concise reasoning for your ruling.
    </rules>
    """)

    _PROMPT_TEMPLATE = dedent("""
    <agent_output>
    {output}
    </agent_output>
    """)

    def __init__(self, criteria: list[str]) -> None:
        self._criteria = criteria
        criteria_str = "\n".join(f"- {c}" for c in self._criteria)
        instructions = self._INSTRUCTION_TEMPLATE.format(criteria=criteria_str)
        self._agent = Agent(model=JUDGE_MODEL, output_type=Verdict, instructions=instructions)

    def judge(self, output: str, /) -> Verdict:
        """
        Judges the output against the criteria and returns a Verdict.
        """
        prompt = self._PROMPT_TEMPLATE.format(output=output)
        result = self._agent.run_sync(prompt)
        return result.output

    def assert_judge(self, output: str, /) -> None:
        """
        Raises an AssertionError if the output fails to meet the criteria.
        """
        verdict = self.judge(output)
        if verdict.ruling == "fail":
            msg = ERROR_MESSAGE.format(output, verdict.reasoning)
            raise AssertionError(msg)


def judge(criteria: list[str], output: str, /) -> Verdict:
    """
    Judges the output against the criteria and returns a Verdict.
    """
    return Judge(criteria).judge(output)


def assert_judge(criteria: list[str], output: str | None, /) -> None:
    """
    Raises an AssertionError if the output fails to meet the criteria.
    """
    assert output is not None
    Judge(criteria).assert_judge(output)
