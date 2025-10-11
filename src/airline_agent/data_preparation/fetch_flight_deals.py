"""Script to fetch flight data from all city-to-city URLs and save to SQLite database."""

import argparse
import json
import sqlite3
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

from airline_agent.types.flights import FlightInfo

# Constants
FLIGHTS_URL = "https://flights.flyfrontier.com"
CITY_TO_CITY_SITEMAP_URL = "https://flights.flyfrontier.com/en/sitemap/city-to-city-flights/page-1"


def _rel_to_abs_url(rel_url: str) -> str:
    """Convert a relative URL to an absolute URL."""
    return urllib.parse.urljoin(FLIGHTS_URL, rel_url)


def _fetch_html_with_js(url: str) -> str:
    """Fetch HTML from a URL using Selenium to render JavaScript.

    Args:
        url: The URL to fetch

    Returns:
        str: The rendered HTML page source
    """
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(1)
    html = driver.page_source
    driver.quit()
    return html


def fetch_city_to_city_urls() -> list[str]:
    """Fetch all city-to-city flight URLs from the sitemap."""
    html = _fetch_html_with_js(CITY_TO_CITY_SITEMAP_URL)
    soup = BeautifulSoup(html, "html5lib")
    main_div = soup.find("div", id="main")

    if not main_div:
        return []

    all_uls = main_div.find_all("ul")
    ul = all_uls[1]
    all_rel_urls = [str(a.attrs["href"]) for li in ul.find_all("li") if (a := li.find("a")) and "href" in a.attrs]
    return [_rel_to_abs_url(rel_url) for rel_url in all_rel_urls]


def search_flights(url: str) -> list[FlightInfo]:
    """Search for flights on the given URL and return a list of FlightInfo objects.

    Args:
        url: The URL to search for flights

    Returns:
        List of FlightInfo objects found on the page
    """
    html = _fetch_html_with_js(url)
    soup = BeautifulSoup(html, "html5lib")

    # Find the __NEXT_DATA__ script tag containing JSON data
    script_tag = soup.find("script", {"id": "__NEXT_DATA__", "type": "application/json"})
    if not script_tag or not script_tag.string:
        return []

    try:
        json_data = json.loads(script_tag.string)
    except json.JSONDecodeError:
        return []

    apollo_state = json_data.get("props", {}).get("pageProps", {}).get("apolloState", {})
    if not apollo_state or "data" not in apollo_state:
        return []

    data = apollo_state["data"]

    fares_data = None
    for key, value in data.items():
        if key.startswith("StandardFareModule:") and isinstance(value, dict) and "fares" in value:
            fares_data = value["fares"]
            break

    if not fares_data:
        return []

    flights = []
    for fare in fares_data:
        origin_city = fare.get("originCity", "")
        origin_code = fare.get("originAirportCode", "")
        origin = f"{origin_city} ({origin_code})" if origin_code else origin_city

        destination_city = fare.get("destinationCity", "")
        destination_code = fare.get("destinationAirportCode", "")
        destination = f"{destination_city} ({destination_code})" if destination_code else destination_city

        flight_type = fare.get("formattedFlightType", "")
        travel_class = fare.get("formattedTravelClass", "")
        fare_type = f"{flight_type} / {travel_class}" if flight_type and travel_class else travel_class or flight_type

        departure_date = fare.get("formattedDepartureDate", "")
        departure_date_string = f"Departing {departure_date}" if departure_date else ""

        starting_price = fare.get("formattedTotalPrice", "")

        price_last_seen = fare.get("priceLastSeen", {})
        if price_last_seen:
            value = price_last_seen.get("value", "")
            unit = price_last_seen.get("unit", "")
            last_seen = f"{value} {unit} ago" if value and unit else ""
        else:
            last_seen = ""

        if origin and destination and starting_price:
            flight_info = FlightInfo(
                origin=origin,
                destination=destination,
                fare_type=fare_type,
                departure_date=departure_date_string,
                starting_price=starting_price,
                last_seen=last_seen,
            )
            flights.append(flight_info)

    return flights


def create_database(db_path: str) -> sqlite3.Connection:
    """Create or connect to SQLite database and set up the flights table.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create flights table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            fare_type TEXT,
            departure_date TEXT,
            starting_price TEXT NOT NULL,
            last_seen TEXT,
            UNIQUE(origin, destination, fare_type, departure_date, starting_price)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_origin_dest ON flights(origin, destination)
    """)

    conn.commit()
    return conn


def save_flights(conn: sqlite3.Connection, flights: list[FlightInfo]) -> int:
    """Save flight information to the database.

    Args:
        conn: SQLite database connection
        flights: List of FlightInfo objects

    Returns:
        int: Number of flights inserted (not counting duplicates)
    """
    cursor = conn.cursor()
    inserted = 0

    for flight in flights:
        try:
            cursor.execute(
                """
                INSERT INTO flights (origin, destination, fare_type, departure_date, starting_price, last_seen)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    flight.origin,
                    flight.destination,
                    flight.fare_type,
                    flight.departure_date,
                    flight.starting_price,
                    flight.last_seen,
                ),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            # Skip duplicate entries
            pass

    conn.commit()
    return inserted


def process_url(url: str) -> tuple[str, list[FlightInfo] | None, str | None]:
    """Process a single URL and return the results.

    Args:
        url: URL to process

    Returns:
        Tuple of (url, flights or None, error message or None)
    """
    try:
        flights = search_flights(url)
    except (WebDriverException, AttributeError, TypeError, KeyError) as e:
        return (url, None, str(e))
    else:
        return (url, flights, None)


def fetch_and_save_all_flights(db_path: str) -> None:
    """Fetch flights from all city-to-city URLs and save to database using concurrent processing.

    Args:
        db_path: Path to save the SQLite database file
    """
    print("Fetching city-to-city flight URLs...")  # noqa: T201
    urls = fetch_city_to_city_urls()
    print(f"Found {len(urls)} city-to-city flight URLs to process")  # noqa: T201
    print("Using maximum available concurrent workers")  # noqa: T201

    print(f"Creating/connecting to database at {db_path}")  # noqa: T201
    conn = create_database(db_path)

    total_flights = 0
    total_inserted = 0
    failed_urls = []
    completed = 0

    db_lock = Lock()

    try:
        with ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(process_url, url): url for url in urls}

            for future in as_completed(future_to_url):
                url, flights, error = future.result()

                with db_lock:
                    completed += 1
                    print(f"Processing {completed}/{len(urls)}...", end="\r")  # noqa: T201

                    if error:
                        failed_urls.append((url, error))
                    elif flights:
                        inserted = save_flights(conn, flights)
                        total_flights += len(flights)
                        total_inserted += inserted

        print()  # noqa: T201 # New line after progress indicator

        print("\n" + "=" * 60)  # noqa: T201
        print("SUMMARY")  # noqa: T201
        print("=" * 60)  # noqa: T201
        print(f"Total URLs processed: {len(urls)}")  # noqa: T201
        print(f"Total flights found: {total_flights}")  # noqa: T201
        print(f"New records inserted: {total_inserted}")  # noqa: T201
        print(f"Failed URLs: {len(failed_urls)}")  # noqa: T201

        if failed_urls:
            print("\nFailed URLs:")  # noqa: T201
            for url, error in failed_urls:
                print(f"  - {url}")  # noqa: T201
                print(f"    Error: {error}")  # noqa: T201

        print(f"\nDatabase saved to: {db_path}")  # noqa: T201

    finally:
        conn.close()


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Fetch flight data from all city-to-city URLs and save to SQLite database"
    )
    parser.add_argument(
        "--path", type=str, default="data/flights.db", help="Path to save the SQLite database of flight data"
    )

    args = parser.parse_args()

    # Ensure the data directory exists
    db_path = Path(args.path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        fetch_and_save_all_flights(str(db_path))
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")  # noqa: T201
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print(f"\nError: {e}", file=sys.stderr)  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    main()
