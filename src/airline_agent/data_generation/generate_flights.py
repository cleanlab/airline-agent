"""
Module to generate Frontier Airlines (F9) flight data for SF Bay Area to New York routes.
Includes direct flights only.
"""

import random
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from airline_agent.constants import FLIGHT_DATA_DATE, FLIGHT_DATA_NUM_DAYS
from airline_agent.types.booking import Fare, Flight, ServiceAddOnOption

# Constants
RNG_SEED = 42
SHORT_FLIGHT_THRESHOLD_HOURS = 2.0  # Threshold for short flights (hours)
DURATION_ADJUSTMENT = 0.1  # Adjustment for SJC/OAK flights (hours)
SF_BAY_AIRPORTS = {"SJC", "OAK"}  # SF Bay Area airports (excluding SFO)

# San Francisco Bay Area airports
SF_AIRPORTS = ["SFO", "SJC", "OAK"]

# New York airports
NYC_AIRPORTS = ["JFK", "EWR", "LGA"]

# Frontier Airlines only
CARRIER_CODE = "F9"
CARRIER_NAME = "Frontier"

# Fare bundle base prices (Frontier Airlines style - no separate cabin classes)
FARE_BASE_PRICES = {
    "basic": {"price_range": (80, 150)},
    "economy": {"price_range": (120, 200)},
    "premium": {"price_range": (200, 320)},
    "business": {"price_range": (350, 550)},
}

# Flight duration estimates (in hours)
# Base durations for SFO routes
BASE_DURATIONS = {
    ("SFO", "JFK"): 5.5,
    ("SFO", "EWR"): 5.3,
    ("SFO", "LGA"): 5.4,
}

# SJC and OAK are similar to SFO, with slight variations
FLIGHT_DURATIONS = dict(BASE_DURATIONS)
# SJC routes (slightly shorter than SFO)
for (orig, dest), duration in BASE_DURATIONS.items():
    if orig == "SFO":
        if duration > SHORT_FLIGHT_THRESHOLD_HOURS:
            FLIGHT_DURATIONS[("SJC", dest)] = duration - DURATION_ADJUSTMENT
        else:
            FLIGHT_DURATIONS[("SJC", dest)] = duration
    if dest == "SFO":
        if duration > SHORT_FLIGHT_THRESHOLD_HOURS:
            FLIGHT_DURATIONS[(orig, "SJC")] = duration - DURATION_ADJUSTMENT
        else:
            FLIGHT_DURATIONS[(orig, "SJC")] = duration
# OAK routes (slightly shorter than SFO)
for (orig, dest), duration in BASE_DURATIONS.items():
    if orig == "SFO":
        if duration > SHORT_FLIGHT_THRESHOLD_HOURS:
            FLIGHT_DURATIONS[("OAK", dest)] = duration - DURATION_ADJUSTMENT
        else:
            FLIGHT_DURATIONS[("OAK", dest)] = duration
    if dest == "SFO":
        if duration > SHORT_FLIGHT_THRESHOLD_HOURS:
            FLIGHT_DURATIONS[(orig, "OAK")] = duration - DURATION_ADJUSTMENT
        else:
            FLIGHT_DURATIONS[(orig, "OAK")] = duration

# NYC to SF routes (reverse of SF to NYC)
for (sf, nyc), duration in list(FLIGHT_DURATIONS.items()):
    if sf in SF_AIRPORTS and nyc in NYC_AIRPORTS:
        FLIGHT_DURATIONS[(nyc, sf)] = duration

# Timezone mappings for airports
AIRPORT_TIMEZONES = {
    # SF Bay Area
    "SFO": ZoneInfo("America/Los_Angeles"),
    "SJC": ZoneInfo("America/Los_Angeles"),
    "OAK": ZoneInfo("America/Los_Angeles"),
    # NYC
    "JFK": ZoneInfo("America/New_York"),
    "EWR": ZoneInfo("America/New_York"),
    "LGA": ZoneInfo("America/New_York"),
}


def get_flight_duration(origin: str, destination: str) -> float:
    """Get flight duration in hours for a route."""
    route = (origin, destination)
    return FLIGHT_DURATIONS.get(route, 3.0)  # Default 3 hours if not found


def get_airport_timezone(airport: str) -> ZoneInfo:
    """Get timezone for an airport."""
    if airport not in AIRPORT_TIMEZONES:
        msg = f"Unknown airport timezone: {airport}"
        raise ValueError(msg)
    return AIRPORT_TIMEZONES[airport]


def generate_fares(rng: random.Random) -> list[Fare]:
    """Generate random fares for a flight with different fare bundles (Frontier Airlines model)."""
    fares = []

    # Basic fare: no services included
    basic_price = rng.uniform(*FARE_BASE_PRICES["basic"]["price_range"])
    fares.append(
        Fare(
            fare_type="basic",
            price_total=round(basic_price, 2),
            currency="USD",
            seats_available=rng.randint(5, 15),
            included_services=[],
            checked_bags_included=0,
        )
    )

    # Economy bundle: Basic + Carry on, Standard seat selection, Refundability, Change/cancel fee waived
    economy_price = rng.uniform(*FARE_BASE_PRICES["economy"]["price_range"])
    fares.append(
        Fare(
            fare_type="economy",
            price_total=round(economy_price, 2),
            currency="USD",
            seats_available=rng.randint(3, 12),
            included_services=["carry_on", "standard_seat_selection", "refundability", "change_cancel_fee_waived"],
            checked_bags_included=0,
        )
    )

    # Premium bundle: Economy + Premium seat selection + Priority Boarding
    premium_price = rng.uniform(*FARE_BASE_PRICES["premium"]["price_range"])
    fares.append(
        Fare(
            fare_type="premium",
            price_total=round(premium_price, 2),
            currency="USD",
            seats_available=rng.randint(2, 8),
            included_services=[
                "carry_on",
                "standard_seat_selection",
                "refundability",
                "change_cancel_fee_waived",
                "premium_seat_selection",
                "priority_boarding",
            ],
            checked_bags_included=0,
        )
    )

    # Business bundle: Premium + 2 checked bags + UpFront Plus Seating
    business_price = rng.uniform(*FARE_BASE_PRICES["business"]["price_range"])
    fares.append(
        Fare(
            fare_type="business",
            price_total=round(business_price, 2),
            currency="USD",
            seats_available=rng.randint(1, 4),
            included_services=[
                "carry_on",
                "standard_seat_selection",
                "refundability",
                "change_cancel_fee_waived",
                "premium_seat_selection",
                "priority_boarding",
                "upfront_plus_seating",
            ],
            checked_bags_included=2,
        )
    )

    return fares


def generate_add_ons(rng: random.Random) -> list[ServiceAddOnOption]:
    """Generate available add-on services for a flight."""
    return [
        ServiceAddOnOption(
            service_type="checked_bag",
            price=round(rng.uniform(30, 40), 2),
            currency="USD",
            description="One checked bag (up to 50 lbs, 62 linear inches)",
        ),
        ServiceAddOnOption(
            service_type="carry_on",
            price=round(rng.uniform(20, 30), 2),
            currency="USD",
            description="One carry-on bag (personal item included)",
        ),
        ServiceAddOnOption(
            service_type="standard_seat_selection",
            price=round(rng.uniform(10, 25), 2),
            currency="USD",
            description="Select a standard seat in advance",
        ),
        ServiceAddOnOption(
            service_type="premium_seat_selection",
            price=round(rng.uniform(25, 45), 2),
            currency="USD",
            description="Select a stretch seat with extra legroom",
        ),
        ServiceAddOnOption(
            service_type="upfront_plus_seating",
            price=round(rng.uniform(50, 100), 2),
            currency="USD",
            description="UpFront Plus seating in first two rows with guaranteed empty middle seat",
        ),
        ServiceAddOnOption(
            service_type="priority_boarding",
            price=round(rng.uniform(8, 15), 2),
            currency="USD",
            description="Priority boarding with overhead bin space",
        ),
        ServiceAddOnOption(
            service_type="travel_insurance",
            price=round(rng.uniform(15, 30), 2),
            currency="USD",
            description="Trip protection insurance",
        ),
        ServiceAddOnOption(
            service_type="refundability",
            price=round(rng.uniform(30, 60), 2),
            currency="USD",
            description="Add refundability to your booking",
        ),
        ServiceAddOnOption(
            service_type="change_cancel_fee_waived",
            price=round(rng.uniform(20, 40), 2),
            currency="USD",
            description="Waive change and cancel fees",
        ),
    ]


def generate_flight_id(origin: str, destination: str, departure: datetime, carrier: str) -> str:
    """Generate a unique flight ID."""
    date_str = departure.strftime("%Y-%m-%dT%H:%M")
    return f"{carrier}-{origin}-{destination}-{date_str}"


def generate_direct_flights(
    rng: random.Random,
    start_date: datetime,
    num_days: int = 8,
    origin_airports: list[str] | None = None,
    dest_airports: list[str] | None = None,
) -> list[Flight]:
    """Generate direct flights from origin airports to destination airports."""
    if origin_airports is None:
        origin_airports = SF_AIRPORTS
    if dest_airports is None:
        dest_airports = NYC_AIRPORTS

    flights = []

    for day in range(num_days):
        date = start_date + timedelta(days=day)

        # Generate comprehensive flights - multiple per origin-destination pair
        for origin in origin_airports:
            for destination in dest_airports:
                # Generate 3-6 flights per origin-destination pair per day
                num_flights = rng.randint(3, 6)

                for _ in range(num_flights):
                    # Random departure time between 6 AM and 10 PM
                    hour = rng.randint(6, 22)
                    minute = rng.choice([0, 15, 30, 45])

                    carrier_code = CARRIER_CODE

                    # Create timezone-aware departure time
                    origin_tz = get_airport_timezone(origin)
                    departure_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0, tzinfo=origin_tz)

                    # Calculate arrival time
                    duration = get_flight_duration(origin, destination)
                    arrival_time_naive = departure_time + timedelta(hours=duration)

                    # Convert to destination timezone
                    dest_tz = get_airport_timezone(destination)
                    arrival_time = arrival_time_naive.astimezone(dest_tz)

                    flight = Flight(
                        id=generate_flight_id(origin, destination, departure_time, carrier_code),
                        origin=origin,
                        destination=destination,
                        departure=departure_time,
                        arrival=arrival_time,
                        flight_number=f"{carrier_code} {rng.randint(100, 999)}",
                        carrier=carrier_code,
                        fares=generate_fares(rng),
                        add_ons=generate_add_ons(rng),
                    )

                    flights.append(flight)

    return flights


def generate_flight_data() -> list[Flight]:
    """
    Generate direct flight data for SF Bay Area to New York routes.

    Returns:
        List of Flight objects
    """
    # Create seeded random number generator for reproducibility
    rng = random.Random(RNG_SEED)  # noqa: S311

    start_date = datetime.combine(FLIGHT_DATA_DATE, datetime.min.time(), tzinfo=UTC)

    # Generate SF -> NYC flights
    direct_flights_sf_to_nyc = generate_direct_flights(
        rng, start_date, num_days=FLIGHT_DATA_NUM_DAYS, origin_airports=SF_AIRPORTS, dest_airports=NYC_AIRPORTS
    )

    # Generate NYC -> SF flights
    direct_flights_nyc_to_sf = generate_direct_flights(
        rng, start_date, num_days=FLIGHT_DATA_NUM_DAYS, origin_airports=NYC_AIRPORTS, dest_airports=SF_AIRPORTS
    )

    # Combine all flights
    all_flights = direct_flights_sf_to_nyc + direct_flights_nyc_to_sf

    # Sort by departure time
    all_flights.sort(key=lambda x: x.departure)

    return all_flights
