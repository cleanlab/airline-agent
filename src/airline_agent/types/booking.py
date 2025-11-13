from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Discriminator, Field, computed_field

FareType = Literal["basic", "economy", "premium", "business"]
ServiceType = Literal[
    "checked_bag",
    "carry_on",
    "standard_seat_selection",
    "premium_seat_selection",
    "upfront_plus_seating",
    "priority_boarding",
    "travel_insurance",
    "refundability",
    "change_cancel_fee_waived",
]
SeatServiceType = Literal["standard_seat_selection", "premium_seat_selection", "upfront_plus_seating"]
GenericServiceType = Literal[
    "checked_bag",
    "carry_on",
    "priority_boarding",
    "travel_insurance",
    "refundability",
    "change_cancel_fee_waived",
]
SeatType = Literal["standard", "stretch", "upfront_plus"]
FlightStatus = Literal[
    "scheduled",
    "on_time",
    "delayed",
    "boarding",
    "departed",
    "arrived",
    "cancelled",
]


class ServiceAddOnBase(BaseModel):
    """Base class for service add-ons with common fields."""

    price: float
    currency: str = "USD"
    added_at: datetime = Field(..., description="Timestamp when the add-on was added")


class SeatServiceAddOn(ServiceAddOnBase):
    """Seat selection service add-on with seat-specific fields."""

    service_type: SeatServiceType
    seat_preference: str | None = Field(
        default=None,
        description='Seat preference such as "window", "aisle", or "middle"',
    )
    seat_assignment: str | None = Field(
        default=None,
        description='Assigned seat identifier, for example "12A" or "15F"',
    )
    seat_type: SeatType = Field(
        ...,
        description='Type of seat selected: "standard", "stretch", or "upfront_plus"',
    )


class GenericServiceAddOn(ServiceAddOnBase):
    """Non-seat service add-on (bags, insurance, priority boarding, etc.)."""

    service_type: GenericServiceType


ServiceAddOn = Annotated[
    SeatServiceAddOn | GenericServiceAddOn,
    Discriminator("service_type"),
]


class Fare(BaseModel):
    """Frontier Airlines fare bundle. No separate cabin classes - all passengers in same cabin."""

    fare_type: FareType = Field(
        default="basic",
        description="Fare bundle purchased (basic, economy, premium, or business)",
    )
    price_total: float = Field(..., description="Per-passenger price of the fare")
    currency: str = "USD"
    seats_available: int
    included_services: list[str] = Field(
        default_factory=list,
        description=("Services included in this fare bundle, e.g. carry-on or seat selection"),
    )
    checked_bags_included: int = Field(
        default=0,
        description="Number of checked bags included (0, 1, or 2 for business)",
    )


class ServiceAddOnOption(BaseModel):
    """Available service add-on options for a flight."""

    service_type: ServiceType
    price: float
    currency: str = "USD"
    description: str = ""


class Flight(BaseModel):
    """Inventory and day-of-travel information for a specific flight."""

    id: str
    origin: str
    destination: str
    departure: datetime
    arrival: datetime
    flight_number: str
    carrier: str = "F9"
    fares: list[Fare]
    add_ons: list[ServiceAddOnOption] = Field(
        default_factory=list,
        description="Available add-ons that can be purchased for the flight",
    )
    departure_terminal: str | None = Field(
        default=None, description='Departure terminal, e.g. "Terminal 1" or "Terminal A"'
    )
    departure_gate: str | None = Field(default=None, description='Departure gate, e.g. "A15" or "B22"')
    arrival_terminal: str | None = Field(default=None, description='Arrival terminal, e.g. "Terminal 3"')
    arrival_gate: str | None = Field(default=None, description='Arrival gate, e.g. "C8"')
    status: FlightStatus = "scheduled"
    status_updated_at: datetime | None = None
    delay_minutes: int | None = Field(default=None, description="Minutes of delay when the flight is delayed")


class BookingStatus(BaseModel):
    """State and timestamps for a booking."""

    status: Literal["confirmed", "cancelled", "pending"]
    created_at: datetime
    updated_at: datetime


class FlightBooking(BaseModel):
    """Represents a single flight within a booking."""

    flight_id: str
    fare_type: FareType = Field(default="basic", description="Fare bundle purchased for the flight")
    base_price: float = Field(..., description="Price of the fare itself")
    currency: str = "USD"
    included_services: list[str] = Field(
        default_factory=list,
        description=("Services bundled with the fare, such as carry-on or standard seat selection"),
    )
    checked_bags_included: int = Field(
        default=0,
        description="Number of checked bags included (0, 1, or 2 for business)",
    )
    add_ons: list[ServiceAddOn] = Field(
        default_factory=list,
        description="Add-on services purchased separately from the base fare",
    )
    checked_in: bool = Field(default=False, description="Whether the passenger has completed check-in")
    checked_in_at: datetime | None = Field(default=None, description="Timestamp when check-in was completed")
    seat_assignment: str | None = Field(
        default=None,
        description='Final seat assignment, e.g. "12A" or "15F"',
    )

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
