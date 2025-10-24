import os
import pathlib
import random
import re
import sqlite3
from datetime import datetime, timedelta
from math import asin, cos, radians, sin, sqrt
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytz
from timezonefinder import TimezoneFinder
from tqdm import tqdm

from airline_agent.constants import DAY, HOUR, MINUTE, MONTH, SECOND, TIMEZONE, YEAR

SIX_MONTHS_IN_DAYS = 182
FLIGHTS_PER_ROUTE = 60
AVG_SPEED_KMH = 850.0
OVERHEAD_MIN = 30.0
OFFSET_MINUTES_STD = 10.0
OFFSET_MINUTES_CLAMP = 20.0
SEED = 42

random.seed(SEED)
np.random.seed(SEED)

tf = TimezoneFinder(in_memory=True)


def main() -> None:

    project_root = pathlib.Path(__file__).resolve().parents[3]
    output_path = project_root / "data" / "flights.db"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    airports_path = project_root / "static" / "airports.csv"
    routes_path = project_root / "static" / "routes.csv"

    airports = pd.read_csv(airports_path)
    airports_coords = airports.astype({"latitude": float, "longitude": float})
    airports_coords_dict: dict[str, dict[str, float]] = (
        airports_coords.set_index("airport")[["latitude", "longitude"]]
        .apply(lambda row: {"lat": row["latitude"], "lng": row["longitude"]}, axis=1)
        .to_dict()
    )

    routes = pd.read_csv(routes_path)
    routes = routes[["departure", "arrival"]].dropna()
    routes_list: list[tuple[str, str]] = list(routes.itertuples(index=False, name=None))

    start_datetime = datetime(YEAR, MONTH, DAY, HOUR, MINUTE, SECOND, tzinfo=ZoneInfo(TIMEZONE))
    end_datetime = start_datetime + timedelta(days=SIX_MONTHS_IN_DAYS)
    rows = []

    for dep_airport, arr_airport in tqdm(routes_list, desc="Generating flights"):
        dep_code = parse_airport_code(dep_airport)
        arr_code = parse_airport_code(arr_airport)

        dep_coords = airports_coords_dict[dep_code]
        arr_coords = airports_coords_dict[arr_code]

        distance_km = calculate_distance(dep_coords["lat"], dep_coords["lng"], arr_coords["lat"], arr_coords["lng"])
        flight_time_minutes = generate_flight_time(distance_km)

        for _ in range(FLIGHTS_PER_ROUTE):
            # Generate flight number, departure and arrival times
            flight_num = generate_flight_num()
            dep_dt = generate_random_datetime(start_datetime, end_datetime)
            arr_dt = dep_dt + timedelta(minutes=flight_time_minutes)

            # Convert timezones based on airport coordinates
            dep_dt_local = convert_to_local_timezone(dep_dt, dep_coords["lat"], dep_coords["lng"])
            arr_dt_local = convert_to_local_timezone(arr_dt, arr_coords["lat"], arr_coords["lng"])

            # Generate prices
            basic = generate_basic_price(distance_km)
            basic, econ, prem, biz = generate_bundled_prices(basic)
            basic_dd, econ_dd, prem_dd, biz_dd = apply_den_discount(basic, econ, prem, biz)

            rows.append(
                {
                    "flight_num": flight_num,
                    "departure_location": dep_airport,
                    "arrival_location": arr_airport,
                    "scheduled_departure_utc": dep_dt.isoformat(),
                    "scheduled_arrival_utc": arr_dt.isoformat(),
                    "scheduled_departure_local": dep_dt_local.isoformat(),
                    "scheduled_arrival_local": arr_dt_local.isoformat(),
                    "basic_price_standard": basic,
                    "economy_price_standard": econ,
                    "premium_price_standard": prem,
                    "business_price_standard": biz,
                    "basic_price_discount_den": basic_dd,
                    "economy_price_discount_den": econ_dd,
                    "premium_price_discount_den": prem_dd,
                    "business_price_discount_den": biz_dd,
                }
            )

    schema_sql = """
    CREATE TABLE flights (
        flight_num TEXT,
        departure_location TEXT,
        arrival_location TEXT,
        scheduled_departure_utc DATETIME,
        scheduled_arrival_utc DATETIME,
        scheduled_departure_local DATETIME,
        scheduled_arrival_local DATETIME,
        basic_price_standard INTEGER,
        economy_price_standard INTEGER,
        premium_price_standard INTEGER,
        business_price_standard INTEGER,
        basic_price_discount_den INTEGER,
        economy_price_discount_den INTEGER,
        premium_price_discount_den INTEGER,
        business_price_discount_den INTEGER
    );
    """

    if os.path.exists(output_path):
        os.remove(output_path)

    conn = sqlite3.connect(output_path)
    cur = conn.cursor()
    cur.execute(schema_sql)

    insert_sql = """
    INSERT INTO flights (
        flight_num, departure_location, arrival_location, 
        scheduled_departure_utc, scheduled_arrival_utc, scheduled_departure_local, scheduled_arrival_local,
        basic_price_standard, economy_price_standard, premium_price_standard, business_price_standard,
        basic_price_discount_den, economy_price_discount_den, premium_price_discount_den, business_price_discount_den
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cur.executemany(
        insert_sql,
        [
            (
                r["flight_num"],
                r["departure_location"],
                r["arrival_location"],
                r["scheduled_departure_utc"],
                r["scheduled_arrival_utc"],
                r["scheduled_departure_local"],
                r["scheduled_arrival_local"],
                r["basic_price_standard"],
                r["economy_price_standard"],
                r["premium_price_standard"],
                r["business_price_standard"],
                r["basic_price_discount_den"],
                r["economy_price_discount_den"],
                r["premium_price_discount_den"],
                r["business_price_discount_den"],
            )
            for r in rows
        ],
    )

    conn.commit()
    conn.close()


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate the distance between two points on the Earth's surface using the Haversine formula."""
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * asin(sqrt(a))


def generate_flight_time(distance_km: float) -> int:
    """Generate the flight time in minutes based on the distance and speed, with random offset."""
    hours = distance_km / AVG_SPEED_KMH
    base_time = hours * 60 + OVERHEAD_MIN
    offset_minutes = np.clip(np.random.normal(0, OFFSET_MINUTES_STD), -OFFSET_MINUTES_CLAMP, OFFSET_MINUTES_CLAMP)
    return int(base_time + offset_minutes)


def generate_bundled_prices(basic: int) -> tuple[int, int, int, int]:
    """Generate 3 higher tiers: 10-20% more expensive than the previous."""
    bump_factor = 1.0 + random.uniform(0.10, 0.20)  # noqa: S311
    econ = int(basic * bump_factor)
    premium = int(econ * bump_factor)
    business = int(premium * bump_factor)
    return basic, econ, premium, business


def generate_basic_price(distance_km: float) -> int:
    """Simple distance-based basic fare."""
    per_km = 0.09 + random.uniform(-0.01, 0.02)  # noqa: S311
    raw = distance_km * per_km + random.uniform(0, 25)  # noqa: S311
    return int(raw)


def apply_den_discount(basic: int, econ: int, prem: int, biz: int) -> tuple[int, int, int, int]:
    """
    Apply a single 10-50% discount factor for all tiers of the same flight.
    """
    discount_factor = 1.0 - random.uniform(0.10, 0.50)  # noqa: S311
    basic_dd = int(basic * discount_factor)
    econ_dd = int(econ * discount_factor)
    prem_dd = int(prem * discount_factor)
    biz_dd = int(biz * discount_factor)
    return basic_dd, econ_dd, prem_dd, biz_dd


def generate_flight_num() -> str:
    """Generate a random flight number like F9###."""
    return f"F9{random.randint(100, 999)}"  # noqa: S311


def generate_random_datetime(start_dt: datetime, end_dt: datetime) -> datetime:
    """Generate a random datetime between start_dt and end_dt."""
    delta = end_dt - start_dt
    seconds = random.randint(0, int(delta.total_seconds()))  # noqa: S311
    return start_dt + timedelta(seconds=seconds)


def convert_to_local_timezone(utc_dt: datetime, lat: float, lng: float) -> datetime:
    """Convert UTC datetime to local airport timezone."""

    timezone_str = tf.timezone_at(lat=lat, lng=lng)
    if timezone_str is None:
        timezone_str = "UTC"
    local_tz = pytz.timezone(timezone_str)

    return utc_dt.astimezone(local_tz)


def parse_airport_code(text: str) -> str:
    """
    Extract the 3-letter airport code from a string like 'Atlanta, GA (ATL)'.
    Raises ValueError if no airport code is found.
    """
    match = re.search(r"\(([A-Za-z]{3})\)", text)
    if match is None:
        msg = f"No airport code found in text: {text}"
        raise ValueError(msg)
    return match.group(1).upper()


if __name__ == "__main__":
    main()
