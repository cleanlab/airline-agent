from __future__ import annotations

import json
import random
import uuid
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from airline_agent.types.booking import (
    Booking,
    BookingStatus,
    FareType,
    Flight,
    FlightBooking,
    ServiceAddOn,
    ServiceType,
)

# Constants for flight status timing (in seconds)
DEPARTURE_PAST_THRESHOLD = -900  # 15 minutes past departure
BOARDING_START_THRESHOLD = 900  # 15 minutes until departure
ON_TIME_THRESHOLD = 1800  # 30 minutes until departure


class BookingTools:
    def __init__(self, flights_path: str, reservations_path: str | None = None):
        self._flights_path = flights_path
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

    def _save_flights(self) -> None:
        """Save flights to JSON file."""
        data = {"flights": [flight.model_dump(mode="json") for flight in self._flights.values()]}
        with open(self._flights_path, "w") as f:
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
            msg = f"Invalid departure_date: {departure_date}"
            raise ValueError(msg) from e

        return [
            fl
            for fl in self._flights.values()
            if fl.origin == origin
            and fl.destination == destination
            and fl.departure.date().isoformat() == dep.isoformat()
        ]

    def get_fare_details(self, flight_id: str, fare_type: str = "basic") -> dict[str, Any]:
        """
        Get detailed fare information including what's included and available add-ons.

        Args:
            flight_id: The flight ID
            fare_type: Fare bundle type (basic, economy, premium, business)

        Returns:
            Dictionary with fare details including included services and available add-ons
        """
        if flight_id not in self._flights:
            msg = f"Flight not found: {flight_id}"
            raise ValueError(msg)

        flight = self._flights[flight_id]

        # Find the fare for the requested fare type (no cabin classes in Frontier model)
        fare = next((f for f in flight.fares if f.fare_type == fare_type), None)
        if not fare:
            available_fares = [f.fare_type for f in flight.fares]
            msg = f"Fare '{fare_type}' not available for flight {flight_id}. " f"Available fares: {available_fares}"
            raise ValueError(msg)

        return {
            "flight_id": flight_id,
            "fare_type": fare_type,
            "price": fare.price_total,
            "currency": fare.currency,
            "seats_available": fare.seats_available,
            "included_services": fare.included_services,
            "checked_bags_included": fare.checked_bags_included,
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
        fare_type: FareType = "basic",
    ) -> Booking:
        """
        Book one or more flights for the current user.

        Args:
            flight_ids: List of flight IDs to book
            fare_type: Fare bundle type (basic, economy, premium, business). Defaults to "basic".

        Returns:
            The created booking with booking ID and total price
        """
        if not flight_ids:
            msg = "At least one flight ID must be provided"
            raise ValueError(msg)

        now = datetime.now(UTC)
        booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"

        flight_bookings: list[FlightBooking] = []
        currency = "USD"

        for flight_id in flight_ids:
            if flight_id not in self._flights:
                msg = f"Flight not found: {flight_id}"
                raise ValueError(msg)

            flight = self._flights[flight_id]

            # Find the fare for the requested fare type (no cabin classes in Frontier model)
            fare = next((f for f in flight.fares if f.fare_type == fare_type), None)
            if not fare:
                available_fares = [f.fare_type for f in flight.fares]
                msg = f"Fare '{fare_type}' not available for flight {flight_id}. " f"Available fares: {available_fares}"
                raise ValueError(msg)

            if fare.seats_available <= 0:
                msg = f"No seats available for fare '{fare_type}' for flight {flight_id}"
                raise ValueError(msg)

            flight_bookings.append(
                FlightBooking(
                    flight_id=flight_id,
                    fare_type=fare_type,
                    base_price=fare.price_total,
                    currency=fare.currency,
                    included_services=fare.included_services.copy(),
                    checked_bags_included=fare.checked_bags_included,
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
            msg = f"Booking not found: {booking_id}"
            raise ValueError(msg)
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
        service_type: ServiceType,
        seat_preference: str | None = None,
        seat_assignment: str | None = None,
    ) -> Booking:
        """
        Add a service (e.g., checked bag, carry-on, seat selection) to an existing booking.
        Updates the booking's total price and updated_at timestamp.

        Args:
            booking_id: The booking ID (e.g., "BK-12345678")
            flight_id: The flight ID within the booking to add the service to
            service_type: Type of service to add (checked_bag, carry_on, standard_seat_selection, etc.)
            seat_preference: For seat selection services, preference like "window", "aisle", "middle" (optional)
            seat_assignment: For seat selection services, actual assigned seat like "12A", "15F" (optional)

        Returns:
            The updated booking with the new service added
        """
        if booking_id not in self._reservations:
            msg = f"Booking not found: {booking_id}"
            raise ValueError(msg)

        booking = self._reservations[booking_id]

        # Find the flight in the booking
        flight_booking = next((fb for fb in booking.flights if fb.flight_id == flight_id), None)
        if not flight_booking:
            available_flights = [fb.flight_id for fb in booking.flights]
            msg = f"Flight {flight_id} not found in booking {booking_id}. Available flights: {available_flights}"
            raise ValueError(msg)

        # Get the flight to check available add-ons
        if flight_id not in self._flights:
            msg = f"Flight not found: {flight_id}"
            raise ValueError(msg)

        flight = self._flights[flight_id]

        # Find the add-on option
        addon_option = next((ao for ao in flight.add_ons if ao.service_type == service_type), None)
        if not addon_option:
            available_addons = [ao.service_type for ao in flight.add_ons]
            msg = (
                f"Service '{service_type}' not available for flight {flight_id}. Available add-ons: {available_addons}"
            )
            raise ValueError(msg)

        # Check if service is already included in the fare
        # Special handling for checked_bag (tracked via count, not in included_services)
        if service_type == "checked_bag":
            if flight_booking.checked_bags_included > 0:
                msg = (
                    f"Checked bag(s) are already included in the {flight_booking.fare_type} fare "
                    f"for flight {flight_id} ({flight_booking.checked_bags_included} bag(s) included)"
                )
                raise ValueError(msg)
        elif service_type in flight_booking.included_services:
            msg = (
                f"Service '{service_type}' is already included in the {flight_booking.fare_type} fare "
                f"for flight {flight_id}"
            )
            raise ValueError(msg)

        # Check if add-on already exists
        existing_addon = next((ao for ao in flight_booking.add_ons if ao.service_type == service_type), None)
        if existing_addon:
            msg = f"Service '{service_type}' has already been added to flight {flight_id} in this booking"
            raise ValueError(msg)

        # Add the service add-on
        now = datetime.now(UTC)

        # For seat selection services, validate that preferences/assignments are only set for seat selection
        seat_selection_types = ["standard_seat_selection", "premium_seat_selection", "upfront_plus_seating"]
        if service_type not in seat_selection_types and (seat_preference or seat_assignment):
            msg = "seat_preference and seat_assignment can only be set for seat selection service types"
            raise ValueError(msg)

        # Determine seat type based on service type
        seat_type = None
        if service_type == "standard_seat_selection":
            seat_type = "standard"
        elif service_type == "premium_seat_selection":
            seat_type = "stretch"
        elif service_type == "upfront_plus_seating":
            seat_type = "upfront_plus"

        flight_booking.add_ons.append(
            ServiceAddOn(
                service_type=service_type,
                price=addon_option.price,
                currency=addon_option.currency,
                added_at=now,
                seat_preference=seat_preference,
                seat_assignment=seat_assignment,
                seat_type=seat_type,
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
        now = datetime.now(UTC)
        return {
            "date": now.date().isoformat(),  # YYYY-MM-DD format
            "datetime": now.isoformat(),  # Full ISO timestamp with timezone
        }

    def _assign_seat(self, flight_booking: FlightBooking, _flight_id: str) -> str:
        """Assign a seat to a flight booking based on preferences, fare type, or randomly."""
        # Check if any seat selection add-on exists with an assignment
        seat_selection_types = ["standard_seat_selection", "premium_seat_selection", "upfront_plus_seating"]
        seat_addon = next(
            (addon for addon in flight_booking.add_ons if addon.service_type in seat_selection_types),
            None,
        )
        if seat_addon and seat_addon.seat_assignment:
            return seat_addon.seat_assignment

        # If seat selection exists with preference, try to honor it
        preference = seat_addon.seat_preference if seat_addon else None
        seat_type = seat_addon.seat_type if seat_addon else None

        # Generate random seat assignment based on fare type and seat selection
        # UpFront Plus: rows 1-2 (first two rows)
        # Stretch: rows 3-15 (premium seating area)
        # Standard: rows 16-40 (standard seating area)

        if seat_type == "upfront_plus":
            row_min, row_max = (1, 2)
        elif seat_type == "stretch":
            row_min, row_max = (3, 15)
        elif flight_booking.fare_type == "business":
            # Business fare includes UpFront Plus seating
            row_min, row_max = (1, 2)
        elif seat_type == "standard":
            row_min, row_max = (16, 40)
        else:
            # Default to standard seating area
            row_min, row_max = (16, 40)

        row = random.randint(row_min, row_max)  # noqa: S311

        # Seat letters (typical 3-3 configuration: A, B, C, D, E, F)
        seat_letters = ["A", "B", "C", "D", "E", "F"]
        window_seats = ["A", "F"]
        aisle_seats = ["C", "D"]

        if preference == "window":
            seat_letter = random.choice(window_seats)  # noqa: S311
        elif preference == "aisle":
            seat_letter = random.choice(aisle_seats)  # noqa: S311
        else:
            seat_letter = random.choice(seat_letters)  # noqa: S311

        return f"{row}{seat_letter}"

    def _assign_gates_and_terminals(self, flight: Flight) -> None:
        """Assign gates and terminals to a flight if not already assigned."""
        # Assign departure terminal and gate if not already assigned
        if not flight.departure_terminal:
            terminals = ["Terminal 1", "Terminal 2", "Terminal 3", "Terminal A", "Terminal B"]
            flight.departure_terminal = random.choice(terminals)  # noqa: S311

        if not flight.departure_gate:
            # Generate a gate like "A15", "B22", "C8"
            gate_letters = ["A", "B", "C", "D"]
            gate_letter = random.choice(gate_letters)  # noqa: S311
            gate_number = random.randint(1, 50)  # noqa: S311
            flight.departure_gate = f"{gate_letter}{gate_number}"

        # Assign arrival terminal and gate if not already assigned
        if not flight.arrival_terminal:
            terminals = ["Terminal 1", "Terminal 2", "Terminal 3", "Terminal A", "Terminal B"]
            flight.arrival_terminal = random.choice(terminals)  # noqa: S311

        if not flight.arrival_gate:
            gate_letters = ["A", "B", "C", "D", "E"]
            gate_letter = random.choice(gate_letters)  # noqa: S311
            gate_number = random.randint(1, 60)  # noqa: S311
            flight.arrival_gate = f"{gate_letter}{gate_number}"

    def _calculate_check_in_timings(self, departure: datetime) -> dict[str, datetime]:
        """Calculate check-in and boarding timing windows."""
        check_in_opens = departure - timedelta(days=1)  # 24 hours before
        check_in_closes = departure - timedelta(minutes=45)  # 45 minutes before
        boarding_starts = departure - timedelta(minutes=30)  # 30 minutes before
        doors_close = departure - timedelta(minutes=15)  # 15 minutes before

        return {
            "check_in_opens_at": check_in_opens,
            "check_in_closes_at": check_in_closes,
            "boarding_starts_at": boarding_starts,
            "doors_close_at": doors_close,
        }

    def check_in(self, booking_id: str, flight_id: str) -> Booking:
        """
        Check in for a specific flight in a booking.

        Args:
            booking_id: The booking ID (e.g., "BK-12345678")
            flight_id: The flight ID within the booking to check in for

        Returns:
            The updated booking with check-in information
        """
        if booking_id not in self._reservations:
            msg = f"Booking not found: {booking_id}"
            raise ValueError(msg)

        booking = self._reservations[booking_id]
        if booking.status.status != "confirmed":
            msg = f"Cannot check in for booking {booking_id}: booking status is {booking.status.status}"
            raise ValueError(msg)

        # Find the flight in the booking
        flight_booking = next((fb for fb in booking.flights if fb.flight_id == flight_id), None)
        if not flight_booking:
            available_flights = [fb.flight_id for fb in booking.flights]
            msg = f"Flight {flight_id} not found in booking {booking_id}. Available flights: {available_flights}"
            raise ValueError(msg)

        if flight_booking.checked_in:
            msg = f"Already checked in for flight {flight_id} in booking {booking_id}"
            raise ValueError(msg)

        # Get the flight details
        if flight_id not in self._flights:
            msg = f"Flight not found: {flight_id}"
            raise ValueError(msg)

        flight = self._flights[flight_id]
        now = datetime.now(flight.departure.tzinfo) if flight.departure.tzinfo else datetime.now(UTC)

        # Assign gates and terminals if needed
        self._assign_gates_and_terminals(flight)

        # Assign seat if not already assigned
        if not flight_booking.seat_assignment:
            flight_booking.seat_assignment = self._assign_seat(flight_booking, flight_id)

        # Update check-in status
        flight_booking.checked_in = True
        flight_booking.checked_in_at = now

        # Update booking timestamp
        booking.status.updated_at = now

        # Save changes
        self._reservations[booking_id] = booking
        self._save_reservations()
        self._save_flights()

        return booking

    def get_flight_timings(self, flight_id: str) -> dict[str, Any]:
        """
        Get all timing windows for a flight (check-in, boarding, doors close, etc.).

        Args:
            flight_id: The flight ID

        Returns:
            Dictionary with all timing windows and estimated times
        """
        if flight_id not in self._flights:
            msg = f"Flight not found: {flight_id}"
            raise ValueError(msg)

        flight = self._flights[flight_id]
        timings = self._calculate_check_in_timings(flight.departure)

        return {
            "flight_id": flight_id,
            "flight_number": flight.flight_number,
            "origin": flight.origin,
            "destination": flight.destination,
            "check_in_opens_at": timings["check_in_opens_at"].isoformat(),
            "check_in_closes_at": timings["check_in_closes_at"].isoformat(),
            "boarding_starts_at": timings["boarding_starts_at"].isoformat(),
            "doors_close_at": timings["doors_close_at"].isoformat(),
            "scheduled_departure": flight.departure.isoformat(),
            "scheduled_arrival": flight.arrival.isoformat(),
            "estimated_departure": (
                (flight.departure + timedelta(minutes=flight.delay_minutes or 0)).isoformat()
                if flight.delay_minutes
                else None
            ),
            "estimated_arrival": (
                (flight.arrival + timedelta(minutes=flight.delay_minutes or 0)).isoformat()
                if flight.delay_minutes
                else None
            ),
        }

    def get_flight_status(self, flight_id: str) -> dict[str, Any]:
        """
        Get current flight status including gates, terminals, delays, etc.

        Args:
            flight_id: The flight ID

        Returns:
            Dictionary with current flight status and operational information
        """
        if flight_id not in self._flights:
            msg = f"Flight not found: {flight_id}"
            raise ValueError(msg)

        flight = self._flights[flight_id]

        # Auto-update gates/terminals if check-in window is open
        self._assign_gates_and_terminals(flight)

        # Update flight status based on current time
        now = datetime.now(flight.departure.tzinfo) if flight.departure.tzinfo else datetime.now(UTC)
        time_until_departure = flight.departure - now

        # Update status based on current time vs scheduled departure
        if flight.status in ("scheduled", "on_time", "boarding"):
            if time_until_departure.total_seconds() < 0:  # Past departure time
                flight.status = "departed"
            elif time_until_departure.total_seconds() < BOARDING_START_THRESHOLD:
                flight.status = "boarding"
            elif time_until_departure.total_seconds() < ON_TIME_THRESHOLD:
                flight.status = "on_time"
            else:
                flight.status = "on_time"
            flight.status_updated_at = now

        return {
            "flight_id": flight_id,
            "flight_number": flight.flight_number,
            "origin": flight.origin,
            "destination": flight.destination,
            "status": flight.status,
            "status_updated_at": flight.status_updated_at.isoformat() if flight.status_updated_at else None,
            "delay_minutes": flight.delay_minutes,
            "departure_terminal": flight.departure_terminal,
            "departure_gate": flight.departure_gate,
            "arrival_terminal": flight.arrival_terminal,
            "arrival_gate": flight.arrival_gate,
            "scheduled_departure": flight.departure.isoformat(),
            "scheduled_arrival": flight.arrival.isoformat(),
            "carrier": flight.carrier,
        }
