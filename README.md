# Airline Support Agent

This repo uses the [Hatch](https://hatch.pypa.io/) project manager ([installation instructions](https://hatch.pypa.io/latest/install/)).

1. Fetch raw FAQs (or get this file from someone):

    ```bash
    hatch run python src/airline_agent/data_preparation/fetch_faqs.py --path data/kb.json
    ```

2. Create the vector DB:

    ```bash
    hatch run python src/airline_agent/preprocessing/create_vector_database.py --data-path data/kb.json --vector-db-path data/vector-db
    ```

3. Run the agent:

    ```bash
    hatch run python src/airline_agent/agent.py --kb-path data/kb.json --vector-db-path data/vector-db
    ```

## Example queries

- What can I do to save money if I fly a lot?
- What is 1 + 1?
