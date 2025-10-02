# Airline Support Agent

1. Fetch raw FAQs (or get this file from someone):

    ```bash
    hatch run python src/airline_agent/data_preparation/fetch_faqs.py --path data/kb.json
    ```

2. Create the vector DB:

    ```bash
    hatch run python src/airline_agent/preprocessing/create_vector_database.py --data-path data/kb.json --vector-db-path data/vector-db
    ```

3. Query the agent:

    ```bash
    hatch run python src/airline_agent/agent.py --kb-path data/kb.json --vector-db-path data/vector-db --query "What can I do to save money if I fly a lot?"
    ```
