# Airline Support Agent

This repo uses the [Hatch](https://hatch.pypa.io/) project manager ([installation instructions](https://hatch.pypa.io/latest/install/)).

## Setup API Keys

Before running the agent, you need to configure the following API keys either in a `.env` file or as environment variables.

- **OPENAI_API_KEY**: Your OpenAI API key for GPT model access
- **CODEX_API_KEY**: Your Cleanlab Codex API key  
- **CLEANLAB_PROJECT_ID**: Your Cleanlab project ID


## Usage

1. Fetch data (or get these files from someone):

    ```bash
    hatch run python src/airline_agent/data_preparation/fetch_pages.py --path data/kb.json
    ```

2. Create the vector DB:

    ```bash
    hatch run python src/airline_agent/preprocessing/create_vector_database.py --data-path data/kb.json --vector-db-path data/vector-db
    ```

3. Run the agent:

    ```bash
    hatch run python src/airline_agent/agent.py --kb-path data/kb.json --vector-db-path data/vector-db --validation-mode cleanlab
    ```

    **Note:** Use `--validation-mode` to control validation: `none` (default, no validation), `cleanlab` (standard validation), or `cleanlab_log_tools` (validation with post-chat-turn tool logging)

## Example queries

- What can I do to save money if I fly a lot?
- What is 1 + 1?
