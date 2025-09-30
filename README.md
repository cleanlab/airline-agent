# Airline Support Agent

## Setup

TODO provide `kb.json` directly for testers, but don't include in the repo, because it's Frontier Airlines's content.

1. Fetch raw FAQs:

    ```bash
    uv run src/airline_agent/data_preparation/fetch_faqs.py --path data/kb.json
    ```
