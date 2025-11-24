import os

import httpx
from cleanlab_codex import Client
from openai.types.chat import ChatCompletionMessageParam
from pydantic import TypeAdapter
from pydantic_ai import ModelMessage

from airline_agent.cleanlab_utils.conversion_utils import convert_to_openai_messages

GuidanceResults = TypeAdapter(list[str])


def _consult(query: str, message_history: list[ChatCompletionMessageParam]) -> list[str]:
    api_key = os.getenv("CODEX_API_KEY")
    if not api_key:
        raise ValueError("CODEX_API_KEY environment variable is not set")  # noqa
    client = Client(api_key=api_key)
    base_url = client._client.base_url  # noqa: SLF001
    project_id = os.getenv("CLEANLAB_PROJECT_ID")
    if not project_id:
        raise ValueError("CLEANLAB_PROJECT_ID environment variable is not set")  # noqa
    response = httpx.post(
        base_url.join(f"api/projects/{project_id}/consult"),
        json={"query": query, "message_history": message_history},
        headers={"X-API-Key": api_key},
    )
    res = response.json()["guidance"]
    return GuidanceResults.validate_python(res)


def consult_cleanlab(query: str, message_history: list[ModelMessage]) -> list[str]:
    """Consult Cleanlab for a response to the query."""
    openai_messages = convert_to_openai_messages(message_history)
    return _consult(query, openai_messages)


def update_prompt_with_guidance(prompt: str, guidance: list[str]) -> str:
    """Update the prompt with the guidance."""
    if guidance:
        preamble = "You are provided the following pieces of guidance that may be helpful to answer the above query. You MUST follow closely the guidance that is applicable to the current situation and IGNORE any guidance that is not relevant."
        numbered_guidance = "\n".join(f"{i}. {item}" for i, item in enumerate(guidance, start=1))
        return f"Query: {prompt}\n\n{preamble}\n\n{numbered_guidance}\n\n"
    return prompt
