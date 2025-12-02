import pytest

from airline_agent.util import TestAgent as Agent
from tests.judge import assert_judge


def test_search_flights() -> None:
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
    agent = Agent(cleanlab_enabled=False)
    agent.chat("Show me flights from SFO to EWR on November 12, 2025")
    answer, _ = agent.chat("What's included in the economy fare bundle for the first flight?")
    assert_judge(
        [
            "output mentions details about the economy fare bundle",
            "output mentions included services or benefits",
        ],
        answer,
    )


@pytest.mark.skip(reason="book_flights tool disabled")
def test_book_single_flight() -> None:
    agent = Agent(cleanlab_enabled=False)
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


@pytest.mark.skip(reason="book_flights tool disabled")
def test_book_round_trip() -> None:
    agent = Agent(cleanlab_enabled=False)
    agent.chat("Find flights from OAK to LGA on November 13, 2025")
    agent.chat("Find return flights from LGA to OAK on November 15, 2025")
    answer, _ = agent.chat("Book the first flight for each leg with economy fare")
    assert_judge(
        [
            "output confirms booking of both flights (outbound and return)",
            "output mentions a booking ID",
            "output mentions the total price for both flights",
        ],
        answer,
    )


@pytest.mark.skip(reason="book_flights and get_my_bookings tools disabled")
def test_retrieve_booking() -> None:
    agent = Agent(cleanlab_enabled=False)
    agent.chat("Find a flight from SJC to JFK on November 12, 2025")
    agent.chat("Book the first flight with basic fare")
    answer, _ = agent.chat("Show me my bookings")
    assert_judge(
        [
            "output shows booking information",
            "output mentions flight details or booking status",
        ],
        answer,
    )


@pytest.mark.skip(reason="book_flights and add_service_to_booking tools disabled")
def test_add_service_to_booking() -> None:
    agent = Agent(cleanlab_enabled=False)
    agent.chat("Show me flights from SFO to EWR on November 14, 2025")
    agent.chat("Book the first flight with basic fare")
    answer, _ = agent.chat("Add a checked bag to my booking")
    assert_judge(
        [
            "output confirms the checked bag was added",
            "output mentions the additional cost or updated price",
        ],
        answer,
    )


@pytest.mark.skip(reason="book_flights and check_in tools disabled")
def test_check_in() -> None:
    agent = Agent(cleanlab_enabled=False)
    agent.chat("Find flights from SFO to JFK on November 12, 2025")
    agent.chat("Book the first available flight")
    answer, _ = agent.chat("Check me in for my flight")
    assert_judge(
        [
            "output confirms check-in was successful",
            "output mentions a seat assignment or boarding information",
        ],
        answer,
    )


def test_flight_status() -> None:
    agent = Agent(cleanlab_enabled=False)
    agent.chat("Show me flights from OAK to LGA on November 12, 2025")
    answer, _ = agent.chat("What's the status of the first flight?")
    assert_judge(
        [
            "output provides flight status information",
            "output mentions status (on time, delayed, boarding, etc.) or gate information",
        ],
        answer,
    )


def test_flight_timings() -> None:
    agent = Agent(cleanlab_enabled=False)
    agent.chat("Find flights from SJC to EWR on November 13, 2025")
    answer, _ = agent.chat("When does check-in open for the first flight?")
    assert_judge(
        [
            "output provides timing information",
            "output mentions check-in times or boarding times",
        ],
        answer,
    )


def test_fare_comparison() -> None:
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
    agent = Agent(cleanlab_enabled=False)
    answer, _ = agent.chat("I want to fly from SFO to JFK")
    assert_judge(
        [
            "output asks for the departure date",
            "output does NOT show a list of flights (because date is missing)",
        ],
        answer,
    )


@pytest.mark.skip(reason="get_my_bookings tool disabled")
def test_no_existing_bookings() -> None:
    agent = Agent(cleanlab_enabled=False)
    answer, _ = agent.chat("Show me my bookings")
    assert_judge(
        [
            "output indicates there are no bookings or no confirmed bookings",
            "output does NOT list any specific flight bookings",
        ],
        answer,
    )
