"""Tools for finding the cheapest flight on available routes from the SQLite database."""

import logging
import sqlite3
from pathlib import Path

from airline_agent.types.flight_deals import FlightDealInfo

logger = logging.getLogger(__name__)


class FlightDeals:
    """Tool for finding cheapest fare on available routes from the database."""

    def __init__(self, db_path: str) -> None:
        """Initialize the FlightDeals tool with a database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path

        # Check if database exists
        if not Path(db_path).exists():
            msg = (
                f"Database not found at {db_path}. " "Please run fetch_flight_deals.py first to populate the database."
            )
            raise FileNotFoundError(msg)

    def find_flight_deals(
        self,
        origin: str | None = None,
        destination: str | None = None,
    ) -> list[FlightDealInfo]:
        """Search flight deals database for the cheapest fares based on origin and/or destination filters.

        The database contains the single cheapest flight between each origin/destination pair.
        Filters use SQL-style LIKE matching, so partial matches are supported.

        At least one parameter must be provided. Depending on what you provide:
        - If only origin is provided: Returns the cheapest fare from that origin to EACH possible destination
        - If only destination is provided: Returns the cheapest fare from EACH possible origin to that destination
        - If both are provided: Returns the cheapest fare for routes matching those cities (may include multiple airports per city)

        Examples:
            origin: "Atlanta, GA"
            destination: "New York City, NY"
            Returns:
            - Atlanta, GA (ATL) → New York City, NY (LGA) One-way / Discount Den Basic Fare Departing Jan 13, 2026 $55
            - Atlanta, GA (ATL) → New York City, NY (JFK) One-way / Discount Den Basic Fare Departing Jan 24, 2026 $55

            origin: "Atlanta, GA"
            destination: "New York City, NY (LGA)"
            Returns:
            - Atlanta, GA (ATL) → New York City, NY (LGA) One-way / Discount Den Basic Fare Departing Jan 13, 2026 $55

        Args:
            origin: Optional filter by origin city/airport (partial matches supported via SQL LIKE)
            destination: Optional filter by destination city/airport (partial matches supported via SQL LIKE)

        Returns:
            List of FlightDealInfo objects, one for each matching route with the cheapest fare

        Raises:
            ValueError: If neither origin nor destination is provided
        """
        if not origin and not destination:
            msg = "At least one of origin or destination must be provided"
            raise ValueError(msg)

        query = "SELECT * FROM flights WHERE origin LIKE ? AND destination LIKE ?"
        origin_param = f"%{origin}%" if origin else "%"
        destination_param = f"%{destination}%" if destination else "%"
        params = [origin_param, destination_param]

        # Pydantic AI invokes tool calls in separate threads.
        # SQLite connection objects cannot be shared across threads,
        # so we open a new connection for each query to prevent threading errors.
        logger.info("Searching for flights with params: %r", params)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [
                FlightDealInfo(
                    origin=row["origin"],
                    destination=row["destination"],
                    fare_type=row["fare_type"] or "",
                    departure_date=row["departure_date"],
                    starting_price=row["starting_price"],
                    last_seen=row["last_seen"] or "",
                )
                for row in rows
            ]
        finally:
            conn.close()
