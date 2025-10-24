import os
import httpx
from openai.types.chat import ChatCompletionMessageParam
from pydantic_ai import ModelMessage
from cleanlab_codex import Client

from airline_agent.cleanlab_utils.conversion_utils import convert_to_openai_messages


def _consult(query: str, message_history: list[ChatCompletionMessageParam]) -> str:
    api_key = os.getenv("CODEX_API_KEY")
    if not api_key:
        raise ValueError("CODEX_API_KEY environment variable is not set")
    client = Client(api_key=api_key)
    base_url = client._client.base_url
    project_id = os.getenv("CLEANLAB_PROJECT_ID")
    if not project_id:
        raise ValueError("CLEANLAB_PROJECT_ID environment variable is not set")
    response = httpx.post(
        f"{base_url}/api/projects/{project_id}/consult",
        json={"query": query, "message_history": message_history},
        headers={"X-API-Key": api_key},
    )
    return response.json()["guidance"]


def consult_cleanlab(query: str, message_history: list[ModelMessage]) -> str | None:
    """Consult Cleanlab for a response to the query."""
    openai_messages = convert_to_openai_messages(message_history)
    guidance = _consult(query, openai_messages)
    return guidance


def update_prompt_with_guidance(prompt: str, guidance: str | None) -> str:
    """Update the prompt with the guidance."""
    if guidance:
        return (
            f"{prompt}\n\n<advice_to_consider>\n{guidance}\n</advice_to_consider>\n\n"
        )
    return prompt


def consult_cleanlab_and_update_prompt(
    prompt: str, message_history: list[ModelMessage]
) -> str:
    """Consult Cleanlab for a response to the query and update the prompt with the guidance."""
    guidance = consult_cleanlab(prompt, message_history)
    return update_prompt_with_guidance(prompt, guidance)
