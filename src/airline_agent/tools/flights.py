"""Tools for querying flight data from the SQLite database."""

import logging
import sqlite3
from pathlib import Path

from airline_agent.types.flights import FlightInfo

logger = logging.getLogger(__name__)


class Flights:
    """Tool for querying flight information from the database."""

    def __init__(self, db_path: str = "data/flights.db") -> None:
        """Initialize the Flights tool with a database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path

        # Check if database exists
        if not Path(db_path).exists():
            msg = f"Database not found at {db_path}. Please run fetch_flights.py first to populate the database."
            raise FileNotFoundError(msg)

    def search_flights(
        self,
        origin: str | None = None,
        destination: str | None = None,
        departure_date: str | None = None,
    ) -> list[FlightInfo]:
        """Search for available flights matching the given criteria.

        Args:
            origin: Filter by origin city/airport
            destination: Filter by destination city/airport
            departure_date: Filter by departure date

        Returns:
            List of FlightInfo objects matching the criteria
        """
        query = "SELECT * FROM flights WHERE 1=1"
        params = []

        if origin:
            query += " AND origin LIKE ?"
            params.append(f"%{origin}%")

        if destination:
            query += " AND destination LIKE ?"
            params.append(f"%{destination}%")

        if departure_date:
            query += " AND departure_date LIKE ?"
            params.append(f"%{departure_date}%")

        # Create a new connection for each query to avoid threading issues
        logger.info("searching for flights with params: %r", params)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            flights = []
            for row in rows:
                flight = FlightInfo(
                    origin=row["origin"],
                    destination=row["destination"],
                    fare_type=row["fare_type"] or "",
                    departure_date=row["departure_date"] or "",
                    starting_price=row["starting_price"],
                    last_seen=row["last_seen"] or "",
                )
                flights.append(flight)

            return flights
        finally:
            conn.close()
