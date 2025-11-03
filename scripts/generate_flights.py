#!/usr/bin/env python3
"""
Script to generate Frontier Airlines (F9) flight data for SF Bay Area to New York routes.
Includes direct flights and connecting flights with layovers through hub airports.
Comprehensive coverage for Halloween week 2025 (Oct 31 - Nov 7).
"""

import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Constants
SHORT_FLIGHT_THRESHOLD_HOURS = 2.0  # Threshold for short flights (hours)
DURATION_ADJUSTMENT = 0.1  # Adjustment for SJC/OAK flights (hours)
PROBABILITY_PREMIUM_ECONOMY = 0.3  # Probability of premium economy add-ons
PROBABILITY_BUSINESS = 0.2  # Probability of business add-ons
SF_BAY_AIRPORTS = {"SJC", "OAK"}  # SF Bay Area airports (excluding SFO)

# San Francisco Bay Area airports
SF_AIRPORTS = ["SFO", "SJC", "OAK"]

# Common hub airports for layovers between SF and NYC
HUB_AIRPORTS = ["DEN", "ORD", "ATL", "DFW", "LAS", "PHX", "SEA", "IAH", "MSP", "DTW"]

# New York airports
NYC_AIRPORTS = ["JFK", "EWR", "LGA"]

# Frontier Airlines only
CARRIER_CODE = "F9"
CARRIER_NAME = "Frontier"

# Cabin configurations and base prices (Frontier Airlines style)
CABIN_CONFIGS = {
    "economy": {"base_price": 120, "price_range": (80, 180)},
    "premium_economy": {"base_price": 200, "price_range": (150, 280)},
    "business": {"base_price": 350, "price_range": (280, 500)},
}

# Flight duration estimates (in hours)
# Base durations for SFO routes
BASE_DURATIONS = {
    ("SFO", "JFK"): 5.5,
    ("SFO", "EWR"): 5.3,
    ("SFO", "LGA"): 5.4,
    ("SFO", "DEN"): 2.5,
    ("SFO", "ORD"): 4.0,
    ("SFO", "ATL"): 4.5,
    ("SFO", "DFW"): 3.5,
    ("SFO", "LAS"): 1.5,
    ("SFO", "PHX"): 1.8,
    ("SFO", "SEA"): 2.0,
    ("SFO", "IAH"): 3.8,
    ("SFO", "MSP"): 3.5,
    ("SFO", "DTW"): 4.2,
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

# Hub to NYC routes
FLIGHT_DURATIONS.update(
    {
        ("DEN", "JFK"): 3.5,
        ("DEN", "EWR"): 3.3,
        ("DEN", "LGA"): 3.4,
        ("ORD", "JFK"): 2.0,
        ("ORD", "EWR"): 2.0,
        ("ORD", "LGA"): 2.0,
        ("ATL", "JFK"): 2.5,
        ("ATL", "EWR"): 2.3,
        ("ATL", "LGA"): 2.4,
        ("DFW", "JFK"): 3.5,
        ("DFW", "EWR"): 3.3,
        ("DFW", "LGA"): 3.4,
        ("LAS", "JFK"): 5.0,
        ("LAS", "EWR"): 4.8,
        ("LAS", "LGA"): 4.9,
        ("PHX", "JFK"): 4.5,
        ("PHX", "EWR"): 4.3,
        ("PHX", "LGA"): 4.4,
        ("SEA", "JFK"): 5.5,
        ("SEA", "EWR"): 5.3,
        ("SEA", "LGA"): 5.4,
        ("IAH", "JFK"): 3.0,
        ("IAH", "EWR"): 2.8,
        ("IAH", "LGA"): 2.9,
        ("MSP", "JFK"): 2.8,
        ("MSP", "EWR"): 2.6,
        ("MSP", "LGA"): 2.7,
        ("DTW", "JFK"): 1.8,
        ("DTW", "EWR"): 1.6,
        ("DTW", "LGA"): 1.7,
    }
)

# NYC to Hub routes (reverse of hub to NYC)
for (hub, nyc), duration in list(FLIGHT_DURATIONS.items()):
    if hub in HUB_AIRPORTS and nyc in NYC_AIRPORTS:
        FLIGHT_DURATIONS[(nyc, hub)] = duration

# NYC to SF routes (reverse of SF to NYC)
for (sf, nyc), duration in list(FLIGHT_DURATIONS.items()):
    if sf in SF_AIRPORTS and nyc in NYC_AIRPORTS:
        FLIGHT_DURATIONS[(nyc, sf)] = duration

# SF to Hub routes
for sf in SF_AIRPORTS:
    for hub in HUB_AIRPORTS:
        if (sf, hub) not in FLIGHT_DURATIONS:
            # Use SFO duration as base
            base_duration = FLIGHT_DURATIONS.get(("SFO", hub), 3.0)
            if sf in SF_BAY_AIRPORTS:
                if base_duration > SHORT_FLIGHT_THRESHOLD_HOURS:
                    FLIGHT_DURATIONS[(sf, hub)] = base_duration - DURATION_ADJUSTMENT
                else:
                    FLIGHT_DURATIONS[(sf, hub)] = base_duration
            else:
                FLIGHT_DURATIONS[(sf, hub)] = base_duration

# Hub to SF routes (reverse)
for (sf, hub), duration in list(FLIGHT_DURATIONS.items()):
    if sf in SF_AIRPORTS and hub in HUB_AIRPORTS:
        FLIGHT_DURATIONS[(hub, sf)] = duration

# Timezone offsets (PST/PDT for SF airports, EST/EDT for NYC)
SF_TZ_OFFSET = -8  # PST
NYC_TZ_OFFSET = -5  # EST

# Hub airport timezones
HUB_TZ_OFFSETS = {
    "DEN": -7,  # MST
    "ORD": -6,  # CST
    "ATL": -5,  # EST
    "DFW": -6,  # CST
    "LAS": -8,  # PST
    "PHX": -7,  # MST
    "SEA": -8,  # PST
    "IAH": -6,  # CST
    "MSP": -6,  # CST
    "DTW": -5,  # EST
}


def get_flight_duration(origin: str, destination: str) -> float:
    """Get flight duration in hours for a route."""
    route = (origin, destination)
    return FLIGHT_DURATIONS.get(route, 3.0)  # Default 3 hours if not found


def get_timezone_offset(airport: str) -> int:
    """Get timezone offset for an airport."""
    if airport in SF_AIRPORTS:
        return SF_TZ_OFFSET
    if airport in NYC_AIRPORTS:
        return NYC_TZ_OFFSET
    return HUB_TZ_OFFSETS.get(airport, -5)


def generate_fares() -> list[dict]:
    """Generate random fares for a flight with different fare types."""
    fares = []

    # Always include economy with multiple fare types
    economy_config = CABIN_CONFIGS["economy"]
    base_price = random.uniform(*economy_config["price_range"])  # noqa: S311

    # Basic fare: no bags included
    fares.append(
        {
            "cabin": "economy",
            "fare_type": "basic",
            "price_total": round(base_price, 2),
            "currency": "USD",
            "seats_available": random.randint(3, 12),  # noqa: S311
            "included_carry_on": False,
            "included_checked_bag": False,
        }
    )

    # Standard fare: includes carry-on (+$15-25 more than basic)
    standard_price = base_price + random.uniform(15, 25)  # noqa: S311
    fares.append(
        {
            "cabin": "economy",
            "fare_type": "standard",
            "price_total": round(standard_price, 2),
            "currency": "USD",
            "seats_available": random.randint(2, 10),  # noqa: S311
            "included_carry_on": True,
            "included_checked_bag": False,
        }
    )

    # Flexible fare: includes checked bag (+$30-45 more than basic)
    flexible_price = base_price + random.uniform(30, 45)  # noqa: S311
    fares.append(
        {
            "cabin": "economy",
            "fare_type": "flexible",
            "price_total": round(flexible_price, 2),
            "currency": "USD",
            "seats_available": random.randint(1, 8),  # noqa: S311
            "included_carry_on": True,
            "included_checked_bag": True,
        }
    )

    # Randomly add premium economy (30% chance - Frontier has limited premium options)
    if random.random() < PROBABILITY_PREMIUM_ECONOMY:  # noqa: S311
        premium_config = CABIN_CONFIGS["premium_economy"]
        premium_base = random.uniform(*premium_config["price_range"])  # noqa: S311

        # Premium economy basic
        fares.append(
            {
                "cabin": "premium_economy",
                "fare_type": "basic",
                "price_total": round(premium_base, 2),
                "currency": "USD",
                "seats_available": random.randint(2, 6),  # noqa: S311
                "included_carry_on": True,  # Premium always includes carry-on
                "included_checked_bag": False,
            }
        )

        # Premium economy flexible (with checked bag)
        fares.append(
            {
                "cabin": "premium_economy",
                "fare_type": "flexible",
                "price_total": round(premium_base + random.uniform(20, 35), 2),  # noqa: S311
                "currency": "USD",
                "seats_available": random.randint(1, 4),  # noqa: S311
                "included_carry_on": True,
                "included_checked_bag": True,
            }
        )

    # Randomly add business (20% chance - Frontier has limited business class)
    if random.random() < PROBABILITY_BUSINESS:  # noqa: S311
        business_config = CABIN_CONFIGS["business"]
        business_base = random.uniform(*business_config["price_range"])  # noqa: S311

        # Business class always includes everything
        fares.append(
            {
                "cabin": "business",
                "fare_type": "flexible",  # Business is always flexible
                "price_total": round(business_base, 2),
                "currency": "USD",
                "seats_available": random.randint(1, 4),  # noqa: S311
                "included_carry_on": True,
                "included_checked_bag": True,
            }
        )

    # No first class for Frontier Airlines

    return fares


def generate_add_ons() -> list[dict]:
    """Generate available add-on services for a flight."""
    return [
        {
            "service_type": "checked_bag",
            "price": round(random.uniform(30, 40), 2),  # noqa: S311
            "currency": "USD",
            "description": "One checked bag (up to 50 lbs, 62 linear inches)",
        },
        {
            "service_type": "carry_on",
            "price": round(random.uniform(20, 30), 2),  # noqa: S311
            "currency": "USD",
            "description": "One carry-on bag (personal item included)",
        },
        {
            "service_type": "seat_selection",
            "price": round(random.uniform(10, 25), 2),  # noqa: S311
            "currency": "USD",
            "description": "Select your seat in advance",
        },
        {
            "service_type": "priority_boarding",
            "price": round(random.uniform(8, 15), 2),  # noqa: S311
            "currency": "USD",
            "description": "Priority boarding (Zone 2)",
        },
        {
            "service_type": "travel_insurance",
            "price": round(random.uniform(15, 30), 2),  # noqa: S311
            "currency": "USD",
            "description": "Trip protection insurance",
        },
    ]


def generate_flight_id(origin: str, destination: str, departure: datetime, carrier: str) -> str:
    """Generate a unique flight ID."""
    date_str = departure.strftime("%Y-%m-%dT%H:%M")
    return f"{carrier}-{origin}-{destination}-{date_str}"


def generate_direct_flights(
    start_date: datetime,
    num_days: int = 8,
    origin_airports: list[str] | None = None,
    dest_airports: list[str] | None = None,
) -> list[dict]:
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
                num_flights = random.randint(3, 6)  # noqa: S311

                for _ in range(num_flights):
                    # Random departure time between 6 AM and 10 PM
                    hour = random.randint(6, 22)  # noqa: S311
                    minute = random.choice([0, 15, 30, 45])  # noqa: S311

                    carrier_code = CARRIER_CODE

                    departure_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)

                    # Calculate arrival time
                    duration = get_flight_duration(origin, destination)
                    arrival_time = departure_time + timedelta(hours=duration)

                    # Adjust for timezone
                    departure_offset = get_timezone_offset(origin)
                    arrival_offset = get_timezone_offset(destination)

                    departure_str = departure_time.strftime(f"%Y-%m-%dT%H:%M:00{departure_offset:+03d}:00")
                    arrival_str = arrival_time.strftime(f"%Y-%m-%dT%H:%M:00{arrival_offset:+03d}:00")

                    flight = {
                        "id": generate_flight_id(origin, destination, departure_time, carrier_code),
                        "origin": origin,
                        "destination": destination,
                        "departure": departure_str,
                        "arrival": arrival_str,
                        "flight_number": f"{carrier_code} {random.randint(100, 999)}",  # noqa: S311
                        "carrier": carrier_code,
                        "fares": generate_fares(),
                        "add_ons": generate_add_ons(),
                    }

                    flights.append(flight)

    return flights


def generate_connecting_flights(
    start_date: datetime,
    num_days: int = 8,
    origin_airports: list[str] | None = None,
    dest_airports: list[str] | None = None,
) -> list[dict]:
    """Generate connecting flights from origin airports to destination airports via hub airports."""
    if origin_airports is None:
        origin_airports = SF_AIRPORTS
    if dest_airports is None:
        dest_airports = NYC_AIRPORTS

    flights = []

    for day in range(num_days):
        date = start_date + timedelta(days=day)

        # Generate comprehensive connecting routes - all combinations
        for origin in origin_airports:
            for destination in dest_airports:
                # Generate multiple connecting routes through different hubs
                # Use all hubs to create many transfer options
                for hub in HUB_AIRPORTS:
                    # Generate 1-3 connecting flights per hub per origin-destination pair per day
                    num_routes = random.randint(1, 3)  # noqa: S311

                    for _ in range(num_routes):
                        carrier_code = CARRIER_CODE

                        # First leg: Origin -> Hub
                        hour1 = random.randint(6, 18)  # noqa: S311
                        minute1 = random.choice([0, 15, 30, 45])  # noqa: S311
                        departure_time_leg1 = date.replace(hour=hour1, minute=minute1, second=0, microsecond=0)

                        duration1 = get_flight_duration(origin, hub)
                        arrival_time_leg1 = departure_time_leg1 + timedelta(hours=duration1)

                        # Layover: 45 minutes to 3 hours
                        layover_hours = random.choice([0.75, 1.0, 1.5, 2.0, 2.5, 3.0])  # noqa: S311
                        departure_time_leg2 = arrival_time_leg1 + timedelta(hours=layover_hours)

                        # Second leg: Hub -> Destination
                        duration2 = get_flight_duration(hub, destination)
                        arrival_time_leg2 = departure_time_leg2 + timedelta(hours=duration2)

                        # First leg
                        departure_offset_leg1 = get_timezone_offset(origin)
                        arrival_offset_leg1 = get_timezone_offset(hub)

                        flight1 = {
                            "id": generate_flight_id(origin, hub, departure_time_leg1, carrier_code),
                            "origin": origin,
                            "destination": hub,
                            "departure": departure_time_leg1.strftime(
                                f"%Y-%m-%dT%H:%M:00{departure_offset_leg1:+03d}:00"
                            ),
                            "arrival": arrival_time_leg1.strftime(f"%Y-%m-%dT%H:%M:00{arrival_offset_leg1:+03d}:00"),
                            "flight_number": f"{carrier_code} {random.randint(100, 999)}",  # noqa: S311
                            "carrier": carrier_code,
                            "fares": generate_fares(),
                            "add_ons": generate_add_ons(),
                        }

                        # Second leg
                        departure_offset_leg2 = get_timezone_offset(hub)
                        arrival_offset_leg2 = get_timezone_offset(destination)

                        flight2 = {
                            "id": generate_flight_id(hub, destination, departure_time_leg2, carrier_code),
                            "origin": hub,
                            "destination": destination,
                            "departure": departure_time_leg2.strftime(
                                f"%Y-%m-%dT%H:%M:00{departure_offset_leg2:+03d}:00"
                            ),
                            "arrival": arrival_time_leg2.strftime(f"%Y-%m-%dT%H:%M:00{arrival_offset_leg2:+03d}:00"),
                            "flight_number": f"{carrier_code} {random.randint(100, 999)}",  # noqa: S311
                            "carrier": carrier_code,
                            "fares": generate_fares(),
                            "add_ons": generate_add_ons(),
                        }

                        flights.extend([flight1, flight2])

    return flights


def main():
    """Main function to generate and save flight data."""
    # Set random seed for reproducibility
    random.seed(42)

    # Start date: Halloween 2025 (October 31) + 1 week
    start_date = datetime(2025, 10, 31, tzinfo=UTC)
    num_days = 8  # Oct 31 - Nov 7

    print("Generating comprehensive flight data for Halloween week 2025 (Oct 31 - Nov 7)...")

    # Generate SF -> NYC flights (direct only)
    print("Generating direct flights (SF -> NYC)...")
    direct_flights_sf_to_nyc = generate_direct_flights(
        start_date, num_days=num_days, origin_airports=SF_AIRPORTS, dest_airports=NYC_AIRPORTS
    )
    print(f"Generated {len(direct_flights_sf_to_nyc)} direct flights from SF to NYC")

    # Generate NYC -> SF flights (direct only)
    print("Generating direct flights (NYC -> SF)...")
    direct_flights_nyc_to_sf = generate_direct_flights(
        start_date, num_days=num_days, origin_airports=NYC_AIRPORTS, dest_airports=SF_AIRPORTS
    )
    print(f"Generated {len(direct_flights_nyc_to_sf)} direct flights from NYC to SF")

    # Combine all flights (direct only, no transfers)
    all_flights = direct_flights_sf_to_nyc + direct_flights_nyc_to_sf

    # Get the project root (two levels up from scripts/)
    project_root = Path(__file__).parent.parent
    flights_file = project_root / "data" / "flights.json"

    # Sort by departure time
    all_flights.sort(key=lambda x: x["departure"])

    output_data = {"flights": all_flights}

    with open(flights_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✓ Successfully saved {len(all_flights)} total flights to {flights_file}")
    print(f"  - Direct flights SF->NYC: {len(direct_flights_sf_to_nyc)}")
    print(f"  - Direct flights NYC->SF: {len(direct_flights_nyc_to_sf)}")
    print("  - All flights are DIRECT flights for Halloween week 2025 (Oct 31 - Nov 7)")
    print("  - No connecting/transfer flights included")


if __name__ == "__main__":
    main()
