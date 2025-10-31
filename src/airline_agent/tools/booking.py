from __future__ import annotations

import json
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, cast

from airline_agent.types.booking import (
    Booking,
    BookingStatus,
    Cabin,
    FareType,
    Flight,
    FlightBooking,
    ServiceAddOn,
    ServiceType,
)


class BookingTools:
    def __init__(self, flights_path: str, reservations_path: str | None = None):
        with open(flights_path) as f:
            raw = json.load(f)
        self._flights: dict[str, Flight] = {x["id"]: Flight(**x) for x in raw["flights"]}

        # Initialize reservations storage
        self._reservations_path = reservations_path
        self._reservations: dict[str, Booking] = {}
        if reservations_path:
            self._load_reservations()

    def _load_reservations(self) -> None:
        """Load reservations from JSON file."""
        if not self._reservations_path:
            return
        try:
            reservations_file = Path(self._reservations_path)
            if reservations_file.exists():
                with open(reservations_file) as f:
                    data = json.load(f)
                    self._reservations = {bid: Booking(**booking_data) for bid, booking_data in data.items()}
            else:
                # Create empty file if it doesn't exist
                reservations_file.parent.mkdir(parents=True, exist_ok=True)
                self._save_reservations()
        except (FileNotFoundError, json.JSONDecodeError):
            self._reservations = {}

    def _save_reservations(self) -> None:
        """Save reservations to JSON file."""
        if not self._reservations_path:
            return
        data = {bid: booking.model_dump(mode="json") for bid, booking in self._reservations.items()}
        with open(self._reservations_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def search_flights(self, origin: str, destination: str, departure_date: str) -> list[Flight]:
        """
        Search available flights by route and date.

        Args:
            origin: IATA airport code (e.g., "SFO", "JFK")
            destination: IATA airport code (e.g., "SFO", "JFK")
            departure_date: Date in YYYY-MM-DD format

        Returns:
            List of available flights matching the route and date
        """
        try:
            dep = date.fromisoformat(departure_date)
        except Exception as e:
            raise ValueError(f"Invalid departure_date: {departure_date}") from e

        return [
            fl
            for fl in self._flights.values()
            if fl.origin == origin
            and fl.destination == destination
            and fl.departure.date().isoformat() == dep.isoformat()
        ]

    def get_fare_details(self, flight_id: str, cabin: str, fare_type: str = "basic") -> dict[str, Any]:
        """
        Get detailed fare information including what's included and available add-ons.

        Args:
            flight_id: The flight ID
            cabin: Cabin class (economy, premium_economy, business, first)
            fare_type: Fare type (basic, standard, flexible)

        Returns:
            Dictionary with fare details including included services and available add-ons
        """
        if flight_id not in self._flights:
            raise ValueError(f"Flight not found: {flight_id}")

        flight = self._flights[flight_id]

        # Find the fare for the requested cabin and fare type
        fare = next((f for f in flight.fares if f.cabin == cabin and f.fare_type == fare_type), None)
        if not fare:
            available_fares = [(f.cabin, f.fare_type) for f in flight.fares]
            raise ValueError(
                f"Fare '{fare_type}' in '{cabin}' cabin not available for flight {flight_id}. "
                f"Available fares: {available_fares}"
            )

        included_services = []
        if fare.included_carry_on:
            included_services.append("carry_on")
        if fare.included_checked_bag:
            included_services.append("checked_bag")

        return {
            "flight_id": flight_id,
            "cabin": cabin,
            "fare_type": fare_type,
            "price": fare.price_total,
            "currency": fare.currency,
            "seats_available": fare.seats_available,
            "included_services": included_services,
            "available_add_ons": [
                {
                    "service_type": addon.service_type,
                    "price": addon.price,
                    "currency": addon.currency,
                    "description": addon.description,
                }
                for addon in flight.add_ons
            ],
        }

    def book_flights(
        self,
        flight_ids: list[str],
        cabin: str = "economy",
        fare_type: str = "basic",
    ) -> Booking:
        """
        Book one or more flights for the current user.

        Args:
            flight_ids: List of flight IDs to book
            cabin: Cabin class (economy, premium_economy, business, first)
            fare_type: Fare type (basic, standard, flexible). Defaults to "basic".

        Returns:
            The created booking with booking ID and total price
        """
        if not flight_ids:
            raise ValueError("At least one flight ID must be provided")

        now = datetime.now()
        booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"

        flight_bookings: list[FlightBooking] = []
        currency = "USD"

        for flight_id in flight_ids:
            if flight_id not in self._flights:
                raise ValueError(f"Flight not found: {flight_id}")

            flight = self._flights[flight_id]

            # Find the fare for the requested cabin and fare type
            fare = next((f for f in flight.fares if f.cabin == cabin and f.fare_type == fare_type), None)
            if not fare:
                available_fares = [(f.cabin, f.fare_type) for f in flight.fares]
                raise ValueError(
                    f"Fare '{fare_type}' in '{cabin}' cabin not available for flight {flight_id}. "
                    f"Available fares: {available_fares}"
                )

            if fare.seats_available <= 0:
                raise ValueError(f"No seats available for fare '{fare_type}' in {cabin} cabin for flight {flight_id}")

            # Determine included services
            included_services = []
            if fare.included_carry_on:
                included_services.append("carry_on")
            if fare.included_checked_bag:
                included_services.append("checked_bag")

            flight_bookings.append(
                FlightBooking(
                    flight_id=flight_id,
                    cabin=cast(Cabin, cabin),
                    fare_type=cast(FareType, fare_type),
                    base_price=fare.price_total,
                    currency=fare.currency,
                    included_services=included_services,
                    add_ons=[],
                )
            )
            currency = fare.currency  # Use currency from last flight

        booking = Booking(
            booking_id=booking_id,
            flights=flight_bookings,
            currency=currency,
            status=BookingStatus(
                status="confirmed",
                created_at=now,
                updated_at=now,
            ),
        )

        self._reservations[booking_id] = booking
        self._save_reservations()

        return booking

    def get_booking(self, booking_id: str) -> Booking:
        """
        Retrieve a booking by its booking ID.

        Args:
            booking_id: The booking ID (e.g., "BK-12345678")

        Returns:
            The booking details
        """
        if booking_id not in self._reservations:
            raise ValueError(f"Booking not found: {booking_id}")
        return self._reservations[booking_id]

    def get_my_bookings(self) -> list[Booking]:
        """
        Retrieve all confirmed bookings for the current user.

        Returns:
            List of all confirmed bookings
        """
        return [booking for booking in self._reservations.values() if booking.status.status == "confirmed"]

    def add_service_to_booking(
        self,
        booking_id: str,
        flight_id: str,
        service_type: str,
        seat_preference: str | None = None,
        seat_assignment: str | None = None,
    ) -> Booking:
        """
        Add a service (e.g., checked bag, carry-on, seat selection) to an existing booking.
        Updates the booking's total price and updated_at timestamp.

        Args:
            booking_id: The booking ID (e.g., "BK-12345678")
            flight_id: The flight ID within the booking to add the service to
            service_type: Type of service to add (checked_bag, carry_on, seat_selection, etc.)
            seat_preference: For seat_selection, preference like "window", "aisle", "middle" (optional)
            seat_assignment: For seat_selection, actual assigned seat like "12A", "15F" (optional)

        Returns:
            The updated booking with the new service added
        """
        if booking_id not in self._reservations:
            raise ValueError(f"Booking not found: {booking_id}")

        booking = self._reservations[booking_id]

        # Find the flight in the booking
        flight_booking = next((fb for fb in booking.flights if fb.flight_id == flight_id), None)
        if not flight_booking:
            available_flights = [fb.flight_id for fb in booking.flights]
            raise ValueError(
                f"Flight {flight_id} not found in booking {booking_id}. " f"Available flights: {available_flights}"
            )

        # Get the flight to check available add-ons
        if flight_id not in self._flights:
            raise ValueError(f"Flight not found: {flight_id}")

        flight = self._flights[flight_id]

        # Find the add-on option
        addon_option = next((ao for ao in flight.add_ons if ao.service_type == service_type), None)
        if not addon_option:
            available_addons = [ao.service_type for ao in flight.add_ons]
            raise ValueError(
                f"Service '{service_type}' not available for flight {flight_id}. "
                f"Available add-ons: {available_addons}"
            )

        # Check if service is already included in the fare
        if service_type in flight_booking.included_services:
            raise ValueError(
                f"Service '{service_type}' is already included in the {flight_booking.fare_type} fare "
                f"for flight {flight_id}"
            )

        # Check if add-on already exists
        existing_addon = next((ao for ao in flight_booking.add_ons if ao.service_type == service_type), None)
        if existing_addon:
            raise ValueError(f"Service '{service_type}' has already been added to flight {flight_id} in this booking")

        # Add the service add-on
        now = datetime.now()

        # For seat selection, validate that preferences/assignments are only set for seat_selection
        if service_type != "seat_selection" and (seat_preference or seat_assignment):
            raise ValueError("seat_preference and seat_assignment can only be set for seat_selection service type")

        flight_booking.add_ons.append(
            ServiceAddOn(
                service_type=cast(ServiceType, service_type),
                price=addon_option.price,
                currency=addon_option.currency,
                added_at=now,
                seat_preference=seat_preference,
                seat_assignment=seat_assignment,
            )
        )

        # Update booking timestamp
        booking.status.updated_at = now

        # Save the updated booking
        self._reservations[booking_id] = booking
        self._save_reservations()

        return booking

    def get_current_date(self) -> dict[str, str]:
        """
        Get the current date and time.

        Returns:
            Dictionary with current date in YYYY-MM-DD format and ISO timestamp
        """
        now = datetime.now()
        return {
            "date": now.date().isoformat(),  # YYYY-MM-DD format
            "datetime": now.isoformat(),  # Full ISO timestamp with timezone
        }
