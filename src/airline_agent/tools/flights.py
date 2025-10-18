import logging
import sqlite3
from datetime import date, datetime
from pathlib import Path

from airline_agent.types.flights import FlightInfo

PRICE_COLUMNS = [
    "basic_price_standard",
    "economy_price_standard",
    "premium_price_standard",
    "business_price_standard",
    "basic_price_discount_den",
    "economy_price_discount_den",
    "premium_price_discount_den",
    "business_price_discount_den",
]

logger = logging.getLogger(__name__)


class Flights:
    def __init__(self, db_path: str):
        self.db_path = db_path

        if not Path(db_path).exists():
            msg = f"Database not found at {db_path}. " "Please run generate_flights.py first to create the database."
            raise FileNotFoundError(msg)

    def _wrap_sql_like(self, value: str | None) -> str:
        if not value:
            return "%"
        if "%" in value or "_" in value:
            return value  # already contains a SQL LIKE pattern
        return f"%{value}%"

    def search_flights(
        self,
        departure_location: str | None = None,
        arrival_location: str | None = None,
        start_time: str | date | datetime | None = None,
        end_time: str | date | datetime | None = None,
        budget: int | None = None,
    ) -> list[FlightInfo]:
        """
        Search for Frontier Airlines flights based on departure/arrival time, departure/arrival location, and budget.

        Args:
            departure_location: The departure location. Supports partial matching with LIKE patterns.
                Examples: "SFO", "San Francisco", "San Fran", "CA (SFO)", "San Francisco, CA (SFO)". Optional.
            arrival_location: The arrival location. Supports partial matching with LIKE patterns.
                Examples: "DEN", "Denver", "Denver, CO (DEN)", "CO (DEN)". Optional.
            start_time: The earliest departure time in ISO format (e.g., "2025-10-06T00:00:00+00:00"). Optional.
            end_time: The latest departure time in ISO format (e.g., "2025-10-12T23:59:59+00:00"). Optional.
            budget: The maximum budget for the flight search. Optional.

        Returns:
            A list of Frontier Airlines flights matching the search criteria. Each flight includes both
            standard pricing (available to all customers) and Discount Den pricing (available only to
            Frontier's \"Discount Den\" members).
        """

        logger.info(
            "searching for flights with parameters: "
            "Departure location=%s, Arrival location=%s, "
            "Start time=%s, End time=%s, Budget=%s",
            departure_location,
            arrival_location,
            start_time,
            end_time,
            budget,
        )

        query = (
            "SELECT * FROM flights WHERE "  # noqa: S608  # PRICE_COLUMNS is static
            "departure_location LIKE ? AND "
            "arrival_location LIKE ? AND "
            "scheduled_departure >= ? AND "
            "scheduled_departure <= ? AND "
            "(" + " OR ".join(f"{col} <= ?" for col in PRICE_COLUMNS) + ")"
        )

        params = [
            self._wrap_sql_like(departure_location),
            self._wrap_sql_like(arrival_location),
            start_time if start_time else "1900-01-01T00:00:00+00:00",
            end_time if end_time else "2100-12-31T23:59:59+00:00",
            *([budget if budget is not None else 999999] * len(PRICE_COLUMNS)),
        ]

        # Pydantic AI invokes tool calls in separate threads.
        # SQLite connection objects cannot be shared across threads,
        # so we open a new connection for each query to prevent threading errors.
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        flights = []
        for row in rows:
            flight = FlightInfo(
                flight_num=row[0],
                departure_location=row[1],
                arrival_location=row[2],
                scheduled_departure=datetime.fromisoformat(row[3]),
                scheduled_arrival=datetime.fromisoformat(row[4]),
                basic_price_standard=row[5],
                economy_price_standard=row[6],
                premium_price_standard=row[7],
                business_price_standard=row[8],
                basic_price_discount_den=row[9],
                economy_price_discount_den=row[10],
                premium_price_discount_den=row[11],
                business_price_discount_den=row[12],
            )
            flights.append(flight)

        return flights
