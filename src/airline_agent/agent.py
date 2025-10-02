import argparse
import contextlib
import logging
from typing import TYPE_CHECKING

from pydantic_ai import Agent

from airline_agent.constants import AGENT_MODEL, AGENT_SYSTEM_PROMPT
from airline_agent.tools.knowledge_base import KnowledgeBase

if TYPE_CHECKING:
    from pydantic_ai.messages import ModelMessage


def create_agent(kb: KnowledgeBase) -> Agent:
    return Agent(
        model=AGENT_MODEL, system_prompt=AGENT_SYSTEM_PROMPT, tools=[kb.get_article, kb.search, kb.list_directory]
    )


def run_agent(agent: Agent) -> None:
    message_history: list[ModelMessage] = []
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        result = agent.run_sync(user_input, message_history=message_history)
        print(f"Agent: {result.output}\n")  # noqa: T201

        message_history.extend(result.new_messages())


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="\033[93m%(asctime)s - %(name)s - %(levelname)s - %(message)s\033[0m",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("llama_index.core.indices.loading").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description="Run the airline support agent.")
    parser.add_argument("--kb-path", type=str, required=True, help="Path to the knowledge base JSON file.")
    parser.add_argument("--vector-db-path", type=str, required=True, help="Path to the vector database directory.")
    args = parser.parse_args()

    kb = KnowledgeBase(args.kb_path, args.vector_db_path)
    agent = create_agent(kb)
    with contextlib.suppress(KeyboardInterrupt):
        run_agent(agent)


if __name__ == "__main__":
    main()
