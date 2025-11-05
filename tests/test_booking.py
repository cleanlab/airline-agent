from tests.judge import assert_judge
from tests.util import Agent


def test_search_flights() -> None:
    """Test searching for flights between SF and NYC."""
    agent = Agent(cleanlab_enabled=False)
    answer, _ = agent.chat("I want to fly from SFO to JFK on November 12, 2025")
    assert_judge(
        [
            "output mentions or lists available flights from SFO to JFK",
            "output mentions departure times or flight options",
        ],
        answer,
    )


def test_get_fare_details() -> None:
    """Test getting fare bundle details for a flight."""
    agent = Agent(cleanlab_enabled=False)
    # First search for flights
    agent.chat("Show me flights from SFO to EWR on November 12, 2025")
    # Then ask about fare details
    answer, _ = agent.chat("What's included in the economy fare bundle for the first flight?")
    assert_judge(
        [
            "output mentions details about the economy fare bundle",
            "output mentions included services or benefits",
        ],
        answer,
    )


def test_book_single_flight() -> None:
    """Test booking a single flight."""
    agent = Agent(cleanlab_enabled=False)
    # Search and book
    agent.chat("I need a flight from SFO to JFK on November 12, 2025")
    answer, _ = agent.chat("Book the first available flight with basic fare")
    assert_judge(
        [
            "output confirms a booking was made",
            "output mentions a booking ID or confirmation number",
            "output mentions the total price",
        ],
        answer,
    )


def test_book_round_trip() -> None:
    """Test booking a round trip (outbound and return flights)."""
    agent = Agent(cleanlab_enabled=False)
    # Search for outbound
    agent.chat("Find flights from OAK to LGA on November 13, 2025")
    # Search for return
    agent.chat("Find return flights from LGA to OAK on November 15, 2025")
    # Book both
    answer, _ = agent.chat("Book the first flight for each leg with economy fare")
    assert_judge(
        [
            "output confirms booking of both flights (outbound and return)",
            "output mentions a booking ID",
            "output mentions the total price for both flights",
        ],
        answer,
    )


def test_retrieve_booking() -> None:
    """Test retrieving booking details by booking ID."""
    agent = Agent(cleanlab_enabled=False)
    # Create a booking first
    agent.chat("Find a flight from SJC to JFK on November 12, 2025")
    booking_response, _ = agent.chat("Book the first flight with basic fare")
    # Retrieve bookings
    answer, _ = agent.chat("Show me my bookings")
    assert_judge(
        [
            "output shows booking information",
            "output mentions flight details or booking status",
        ],
        answer,
    )


def test_add_service_to_booking() -> None:
    """Test adding a service (checked bag) to an existing booking."""
    agent = Agent(cleanlab_enabled=False)
    # Create a booking
    agent.chat("Show me flights from SFO to EWR on November 14, 2025")
    agent.chat("Book the first flight with basic fare")
    # Add a service
    answer, _ = agent.chat("Add a checked bag to my booking")
    assert_judge(
        [
            "output confirms the checked bag was added",
            "output mentions the additional cost or updated price",
        ],
        answer,
    )


def test_check_in() -> None:
    """Test checking in for a flight."""
    agent = Agent(cleanlab_enabled=False)
    # Create a booking
    agent.chat("Find flights from SFO to JFK on November 12, 2025")
    agent.chat("Book the first available flight")
    # Check in
    answer, _ = agent.chat("Check me in for my flight")
    assert_judge(
        [
            "output confirms check-in was successful",
            "output mentions a seat assignment or boarding information",
        ],
        answer,
    )


def test_flight_status() -> None:
    """Test getting flight status information."""
    agent = Agent(cleanlab_enabled=False)
    # Search for a flight first to get context
    agent.chat("Show me flights from OAK to LGA on November 12, 2025")
    # Ask for status
    answer, _ = agent.chat("What's the status of the first flight?")
    assert_judge(
        [
            "output provides flight status information",
            "output mentions status (on time, delayed, boarding, etc.) or gate information",
        ],
        answer,
    )


def test_flight_timings() -> None:
    """Test getting flight timing windows (check-in, boarding, etc.)."""
    agent = Agent(cleanlab_enabled=False)
    # Search for a flight
    agent.chat("Find flights from SJC to EWR on November 13, 2025")
    # Ask about timings
    answer, _ = agent.chat("When does check-in open for the first flight?")
    assert_judge(
        [
            "output provides timing information",
            "output mentions check-in times or boarding times",
        ],
        answer,
    )


def test_fare_comparison() -> None:
    """Test comparing different fare bundles."""
    agent = Agent(cleanlab_enabled=False)
    agent.chat("Show me flights from SFO to JFK on November 12, 2025")
    answer, _ = agent.chat("What's the difference between basic and premium fare for the first flight?")
    assert_judge(
        [
            "output compares basic and premium fares",
            "output mentions differences in price or included services",
        ],
        answer,
    )


def test_invalid_route() -> None:
    """Test handling of invalid or unavailable routes."""
    agent = Agent(cleanlab_enabled=False)
    answer, _ = agent.chat("Find flights from SFO to Tokyo on November 12, 2025")
    assert_judge(
        [
            "output indicates no flights are available or the route is not served",
            "output does NOT show flights from SFO to Tokyo",
        ],
        answer,
    )


def test_no_date_provided() -> None:
    """Test that agent asks for date when searching flights without one."""
    agent = Agent(cleanlab_enabled=False)
    answer, _ = agent.chat("I want to fly from SFO to JFK")
    assert_judge(
        [
            "output asks for the departure date",
            "output does NOT show a list of flights (because date is missing)",
        ],
        answer,
    )


def test_no_existing_bookings() -> None:
    """Test isolation: verify no bookings exist from previous tests."""
    agent = Agent(cleanlab_enabled=False)
    answer, _ = agent.chat("Show me my bookings")
    assert_judge(
        [
            "output indicates there are no bookings or no confirmed bookings",
            "output does NOT list any specific flight bookings",
        ],
        answer,
    )
