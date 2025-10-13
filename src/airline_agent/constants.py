import functools
import logging

logger = logging.getLogger(__name__)

RAG_EMBED_MODEL = "text-embedding-3-small"
RAG_EMBED_BATCH_SIZE = 100
RAG_CHUNK_SIZE = 1024
RAG_CHUNK_OVERLAP = 200
CONTEXT_RETRIEVAL_TOOLS = ["search", "get_article", "list_directory"]
AGENT_MODEL = "openai:gpt-4o"
YEAR, MONTH, DAY, HOUR, MINUTE, SECOND, TIMEZONE = 2025, 10, 1, 9, 0, 0, "UTC"
AGENT_INSTRUCTIONS = (
    """You are an AI customer support agent for Frontier Airlines. You can use tools to access to a knowledge base of articles and
documents about the airline's services, policies, and procedures.

## You have access to the following tools:
- search — find candidate articles by query (keep top-k small, ≤5), returns title/snippet/path.
- get_article — get the full article by its path.
- list_directory — list directory structure to make more informed searches.

## Tool Use Guidelines:
- Keep it tight: aim for 1-2 calls per turn (hard cap 4).
- Answer only from retrieved content.
- If a missing detail blocks tool use, ask one short clarifying question. If not blocking, proceed and state your assumption.
- Don't dump raw tool output—summarize clearly.

## Response Guidelines:
- Answer questions based on information you look up in the knowledge base, not based on your own knowledge.
- If you think that you need more time to investigate, update the user with your latest findings and open questions. You can proceed if the user confirms.
- Discuss any airline-related topics with the user.
- If the user asks about anything unrelated to the airline, politely inform them that you can only assist with airline-related inquiries.

The current date and time is {YEAR}-{MONTH}-{DAY} {HOUR}:{MINUTE}:{SECOND} {TIMEZONE}.
""".strip()
    .replace("\n", " ")
    .replace("  ", " ")
)

FALLBACK_RESPONSE = "I'm sorry, but I don't have the information you're looking for. Please rephrase the question or contact Frontier Airlines customer support for further assistance."


@functools.cache
def get_perfect_eval_scores() -> dict[str, float]:
    """Get perfect eval scores, cached after first call."""
    import os

    from codex import Codex
    from dotenv import load_dotenv

    load_dotenv()  # Ensure .env is loaded before accessing environment variables
    api_key = os.getenv("CODEX_API_KEY")
    project_id = os.getenv("CLEANLAB_PROJECT_ID")

    if not api_key or not project_id:
        logger.warning("CODEX_API_KEY or CLEANLAB_PROJECT_ID environment variable is not set")
        return {}

    client = Codex(api_key=api_key)
    project = client.projects.retrieve(project_id)
    eval_config = project.config.eval_config

    if not eval_config:
        logger.warning("No eval_config found in project")
        return {}

    eval_keys = []

    # Add default evals if they exist
    if eval_config.default_evals:
        default_evals_dump = eval_config.default_evals.model_dump()
        if default_evals_dump:
            eval_keys.extend([evaluation["eval_key"] for evaluation in default_evals_dump.values()])

    # Add custom evals if they exist
    if eval_config.custom_evals and eval_config.custom_evals.evals:
        eval_keys.extend([evaluation.eval_key for evaluation in eval_config.custom_evals.evals.values()])

    logger.info("Retrieved evals: %s", eval_keys)
    return {eval_key: 1.0 for eval_key in eval_keys}
