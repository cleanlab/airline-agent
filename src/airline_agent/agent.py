import argparse
import logging

from pydantic_ai import Agent

from airline_agent.constants import AGENT_MODEL, AGENT_SYSTEM_PROMPT
from airline_agent.tools.knowledge_base import KnowledgeBase


def create_agent(kb: KnowledgeBase) -> Agent:
    return Agent(
        model=AGENT_MODEL, system_prompt=AGENT_SYSTEM_PROMPT, tools=[kb.get_entry, kb.search, kb.list_directory]
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("llama_index.core.indices.loading").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description="Run the airline support agent.")
    parser.add_argument("--query", type=str, required=True, help="The user query to ask the agent.")
    parser.add_argument("--kb-path", type=str, required=True, help="Path to the knowledge base JSON file.")
    parser.add_argument("--vector-db-path", type=str, required=True, help="Path to the vector database directory.")
    args = parser.parse_args()

    kb = KnowledgeBase(args.kb_path, args.vector_db_path)
    agent = create_agent(kb)
    result = agent.run_sync(args.query)
    print(result.output)  # noqa: T201


if __name__ == "__main__":
    main()
