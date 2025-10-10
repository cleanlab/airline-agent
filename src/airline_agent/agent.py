import argparse
import contextlib
import logging
import os
import uuid
from typing import TYPE_CHECKING, cast

from cleanlab_codex import Client, Project
from dotenv import load_dotenv
from pydantic_ai import Agent

from airline_agent.cleanlab_utils.validate_utils import run_cleanlab_validation, run_cleanlab_validation_logging_tools
from airline_agent.constants import AGENT_MODEL, AGENT_SYSTEM_PROMPT
from airline_agent.tools.flights import Flights
from airline_agent.tools.knowledge_base import KnowledgeBase

if TYPE_CHECKING:
    from pydantic_ai.messages import ModelMessage


def create_agent(kb: KnowledgeBase, flights: Flights) -> Agent:
    return Agent(
        model=AGENT_MODEL,
        system_prompt=AGENT_SYSTEM_PROMPT,
        tools=[
            kb.get_article,
            kb.search,
            kb.list_directory,
            flights.list_city_to_city_flights,
            flights.list_flights_from_city,
            flights.search_flights,
        ],
    )


def get_cleanlab_project() -> Project:
    cleanlab_project_id = os.getenv("CLEANLAB_PROJECT_ID")
    if not cleanlab_project_id:
        msg = "CLEANLAB_PROJECT_ID environment variable is not set"
        raise ValueError(msg)
    return Client().get_project(cleanlab_project_id)


def run_agent(agent: Agent, *, validation_mode: str) -> None:
    message_history: list[ModelMessage] = []
    project = None
    if validation_mode != "none":
        project = get_cleanlab_project()
    thread_id = str(uuid.uuid4())

    while True:
        user_input = input("\033[96mYou:\033[0m ").strip()
        if not user_input:
            continue

        result = agent.run_sync(user_input, message_history=message_history)

        if validation_mode == "cleanlab":
            message_history, final_response = run_cleanlab_validation(
                project=cast(Project, project),  # project cannot be None since get_cleanlab_project raises if not found
                query=user_input,
                result=result,
                message_history=message_history,
                thread_id=thread_id,
            )
        elif validation_mode == "cleanlab_log_tools":
            message_history, final_response = run_cleanlab_validation_logging_tools(
                project=cast(Project, project),  # project cannot be None since get_cleanlab_project raises if not found
                query=user_input,
                result=result,
                message_history=message_history,
                thread_id=thread_id,
            )
        else:  # validation_mode == "none"
            message_history.extend(result.new_messages())
            final_response = result.output

        print(f"\033[92mAgent:\033[0m {final_response}")  # noqa: T201


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
        choices=["none", "cleanlab", "cleanlab_log_tools"],
        default="none",
        help="Validation mode: 'none' (no validation), 'cleanlab' (run_cleanlab_validation), 'cleanlab_log_tools' (run_cleanlab_validation_logging_tools)",
    )

    args = parser.parse_args()

    kb = KnowledgeBase(args.kb_path, args.vector_db_path)
    flights = Flights()
    agent = create_agent(kb, flights)
    with contextlib.suppress(KeyboardInterrupt, EOFError):
        run_agent(agent, validation_mode=args.validation_mode)


if __name__ == "__main__":
    main()
