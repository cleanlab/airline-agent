import argparse
import logging
import os
import uuid

from cleanlab_codex import Client, Project
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.agent import AbstractAgent

from airline_agent.cleanlab_utils.cleanlab_agent import CleanlabAgent
from airline_agent.constants import AGENT_INSTRUCTIONS, AGENT_MODEL
from airline_agent.tools.knowledge_base import KnowledgeBase


def create_agent(kb: KnowledgeBase) -> AbstractAgent:
    return Agent(
        model=AGENT_MODEL, instructions=AGENT_INSTRUCTIONS, tools=[kb.get_article, kb.search, kb.list_directory]
    )


def get_cleanlab_project() -> Project:
    cleanlab_project_id = os.getenv("CLEANLAB_PROJECT_ID")
    if not cleanlab_project_id:
        msg = "CLEANLAB_PROJECT_ID environment variable is not set"
        raise ValueError(msg)
    return Client().get_project(cleanlab_project_id)


def prepare_agent(agent: AbstractAgent) -> AbstractAgent:
    project = None
    thread_id = str(uuid.uuid4())

    project = get_cleanlab_project()
    return CleanlabAgent(
        wrapped=agent,
        cleanlab_project=project,
        context_retrieval_tools=["search", "get_article"],
        thread_id=thread_id,
    )


def main() -> None:
    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format="\033[93m%(asctime)s - %(name)s - %(levelname)s - %(message)s\033[0m",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("llama_index.core.indices.loading").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description="Run the airline support agent.")
    parser.add_argument("--kb-path", type=str, required=True, help="Path to the knowledge base JSON file.")
    parser.add_argument("--vector-db-path", type=str, required=True, help="Path to the vector database directory.")
    parser.add_argument(
        "--validation-mode",
        choices=["none", "cleanlab", "cleanlab_log_tools", "agent"],
        default="none",
        help="Validation mode: 'none' (no validation), 'cleanlab' (run_cleanlab_validation), 'cleanlab_log_tools' (run_cleanlab_validation_logging_tools), 'agent' (use CleanlabAgent wrapper)",
    )

    args = parser.parse_args()

    kb = KnowledgeBase(args.kb_path, args.vector_db_path)
    agent = create_agent(kb)
    if args.validation_mode == "agent":
        agent = prepare_agent(agent)
    import uvicorn

    uvicorn.run(agent.to_ag_ui(), host="localhost", port=8000)


if __name__ == "__main__":
    main()
