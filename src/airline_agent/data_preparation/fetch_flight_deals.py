"""Script to fetch flight data from all city-to-city URLs and save to SQLite database."""

import argparse
import json
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed

from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException

from airline_agent.data_preparation.utils import cleanup_driver, fetch_html_with_js, rel_to_abs_url
from airline_agent.types.flights import FlightDealInfo

# Constants
FLIGHTS_URL = "https://flights.flyfrontier.com"
CITY_TO_CITY_SITEMAP_URL = "https://flights.flyfrontier.com/en/sitemap/city-to-city-flights/page-1"


def fetch_city_to_city_urls() -> list[str]:
    """Fetch all city-to-city flight URLs from the sitemap."""
    html = fetch_html_with_js(CITY_TO_CITY_SITEMAP_URL)
    soup = BeautifulSoup(html, "html5lib")
    main_div = soup.find("div", id="main")

    if not main_div:
        return []

    all_uls = main_div.find_all("ul")
    ul = all_uls[1]
    all_rel_urls = [str(a.attrs["href"]) for li in ul.find_all("li") if (a := li.find("a")) and "href" in a.attrs]
    return [rel_to_abs_url(rel_url, FLIGHTS_URL) for rel_url in all_rel_urls]


def search_flights(url: str) -> list[FlightDealInfo]:
    """Search for flights on the given URL and return a list of FlightDealInfo objects.

    Args:
        url: The URL to search for flights

    Returns:
        List of FlightDealInfo objects found on the page
    """
    html = fetch_html_with_js(url)
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

        starting_price_string = fare.get("formattedTotalPrice", "")
        starting_price = int(starting_price_string[1:])  # Remove $ and convert to int

        price_last_seen = fare.get("priceLastSeen", {})
        if price_last_seen:
            value = price_last_seen.get("value", "")
            unit = price_last_seen.get("unit", "")
            last_seen = f"{value} {unit} ago" if value and unit else ""
        else:
            last_seen = ""

        if origin and destination:
            flight_info = FlightDealInfo(
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
    # Delete existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)

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
            starting_price INTEGER NOT NULL,
            last_seen TEXT,
            UNIQUE(origin, destination, fare_type, departure_date, starting_price)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_origin_dest ON flights(origin, destination)
    """)

    conn.commit()
    return conn


def save_flights_to_db(conn: sqlite3.Connection, flights: list[FlightDealInfo]) -> None:
    """Save flight information to the database.

    Args:
        conn: SQLite database connection
        flights: List of FlightDealInfo objects
    """
    cursor = conn.cursor()

    for flight in flights:
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

    conn.commit()


def process_url(url: str) -> tuple[str, list[FlightDealInfo] | None, str | None]:
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

    print(f"Creating/connecting to database at {db_path}")  # noqa: T201
    conn = create_database(db_path)

    total_flights = 0
    failed_urls = []
    completed = 0

    all_flights = []
    try:
        num_workers = min(32, (os.cpu_count() or 1) + 4)
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_url = {executor.submit(process_url, url): url for url in urls}

            for future in as_completed(future_to_url):
                url, flights, error = future.result()

                completed += 1
                print(f"Processing {completed}/{len(urls)}...", end="\r")  # noqa: T201

                if flights:
                    all_flights.extend(flights)
                    total_flights += len(flights)
                elif error:
                    failed_urls.append((url, error))

        # Clean up drivers
        with ThreadPoolExecutor(max_workers=num_workers) as cleanup_executor:
            for _ in range(num_workers):
                cleanup_executor.submit(cleanup_driver)

        # Save all flights to database
        save_flights_to_db(conn, all_flights)

        print()  # noqa: T201 # New line after progress indicator

        print("\n" + "=" * 60)  # noqa: T201
        print("SUMMARY")  # noqa: T201
        print("=" * 60)  # noqa: T201
        print(f"Total URLs processed: {len(urls)}")  # noqa: T201
        print(f"Total flights found: {total_flights}")  # noqa: T201
        print(f"Failed URLs: {len(failed_urls)}")  # noqa: T201

        if failed_urls:
            print("\nFailed URLs:")  # noqa: T201
            for url, error in failed_urls:
                print(f"  - {url}")  # noqa: T201
                print(f"    Error: {error}")  # noqa: T201

    finally:
        conn.close()


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Fetch flight data from all city-to-city URLs and save to SQLite database"
    )
    parser.add_argument("--path", type=str, help="Path to save the SQLite database of flight data", required=True)

    args = parser.parse_args()

    fetch_and_save_all_flights(args.path)


if __name__ == "__main__":
    main()
