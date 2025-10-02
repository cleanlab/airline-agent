# Airline Support Agent

## Setup

TODO provide `kb.json` directly for testers, but don't include in the repo, because it's Frontier Airlines's content.

1. Fetch raw FAQs:

    ```bash
    hatch run python src/airline_agent/data_preparation/fetch_faqs.py --path data/kb.json
    ```

2. Create the vector DB:

    ```bash
    hatch run python src/airline_agent/preprocessing/create_vector_database.py --data-path data/kb.json --vector-db-path data/vector-db
    ```
