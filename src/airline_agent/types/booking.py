from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, computed_field

Cabin = Literal["economy", "premium_economy", "business", "first"]
FareType = Literal["basic", "standard", "flexible"]
ServiceType = Literal["checked_bag", "carry_on", "seat_selection", "priority_boarding", "travel_insurance"]
FlightStatus = Literal[
    "scheduled",
    "on_time",
    "delayed",
    "boarding",
    "departed",
    "arrived",
    "cancelled",
]


class ServiceAddOn(BaseModel):
    """A service add-on purchased for a flight."""

    service_type: ServiceType
    price: float
    currency: str = "USD"
    added_at: datetime  # When was this add-on added
    # Seat selection specific fields
    seat_preference: str | None = None  # e.g., "window", "aisle", "middle"
    seat_assignment: str | None = None  # e.g., "12A", "15F" - actual assigned seat


class Fare(BaseModel):
    cabin: Cabin
    fare_type: FareType = "basic"  # Which fare bundle (basic, standard, flexible)
    price_total: float  # per passenger
    currency: str = "USD"
    seats_available: int
    included_carry_on: bool = False  # Does this fare include carry-on?
    included_checked_bag: bool = False  # Does this fare include checked bag?


class ServiceAddOnOption(BaseModel):
    """Available service add-on options for a flight."""

    service_type: ServiceType
    price: float
    currency: str = "USD"
    description: str = ""


class Flight(BaseModel):
    id: str
    origin: str
    destination: str
    departure: datetime
    arrival: datetime
    flight_number: str
    carrier: str = "F9"
    fares: list[Fare]
    add_ons: list[ServiceAddOnOption] = []  # Available add-ons for this flight

    # Day-of travel information (enriched closer to departure)
    departure_terminal: str | None = None  # e.g., "Terminal 1", "Terminal A"
    departure_gate: str | None = None  # e.g., "A15", "B22"
    arrival_terminal: str | None = None  # e.g., "Terminal 3"
    arrival_gate: str | None = None  # e.g., "C8"

    # Flight status tracking
    status: FlightStatus = "scheduled"
    status_updated_at: datetime | None = None
    delay_minutes: int | None = None  # If delayed, minutes of delay


class BookingStatus(BaseModel):
    status: Literal["confirmed", "cancelled", "pending"]
    created_at: datetime
    updated_at: datetime


class FlightBooking(BaseModel):
    """Represents a single flight within a booking."""

    flight_id: str
    cabin: Cabin
    fare_type: FareType = "basic"  # Which fare bundle was purchased

    # Base fare pricing
    base_price: float  # Price of the fare itself
    currency: str = "USD"

    # Services included in the fare (e.g., "carry_on" for standard, "checked_bag" for flexible)
    included_services: list[str] = []  # e.g., ["carry_on"] or ["checked_bag"]

    # Add-on services purchased separately
    add_ons: list[ServiceAddOn] = []

    # Check-in information
    checked_in: bool = False
    checked_in_at: datetime | None = None  # When check-in was completed

    # Final seat assignment (may differ from seat_selection preference/addon)
    # This is the actual assigned seat after check-in
    seat_assignment: str | None = None  # e.g., "12A", "15F"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def price_total(self) -> float:
        """Calculate total price including base fare + add-ons."""
        return self.base_price + sum(addon.price for addon in self.add_ons)


class Booking(BaseModel):
    """Represents a complete booking containing one or more flights."""

    booking_id: str
    flights: list[FlightBooking]
    currency: str = "USD"
    status: BookingStatus

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_price(self) -> float:
        """Calculate total price across all flights."""
        return sum(flight.price_total for flight in self.flights)
