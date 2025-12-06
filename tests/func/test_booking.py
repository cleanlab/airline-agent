from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import patch

from codex.types.project_validate_response import ProjectValidateResponse
from pydantic_ai.messages import ModelMessage

from airline_agent.cleanlab_utils.validate_utils import run_cleanlab_validation_logging_tools
from airline_agent.util import TestAgent as Agent
from tests.judge import assert_judge


@contextmanager
def mock_cleanlab_validation_with_guardrail() -> Iterator[None]:
    """Context manager that mocks cleanlab validation to always set should_guardrail=True."""

    def mock_validation(*args: Any, **kwargs: Any) -> tuple[list[ModelMessage], str, ProjectValidateResponse]:
        updated_message_history, final_response, validation_result = run_cleanlab_validation_logging_tools(
            *args, **kwargs
        )
        validation_result.should_guardrail = True
        return updated_message_history, final_response, validation_result

    with patch(
        "airline_agent.backend.services.airline_chat.run_cleanlab_validation_logging_tools", side_effect=mock_validation
    ):
        yield


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


def test_book_flight_fallback() -> None:
    with mock_cleanlab_validation_with_guardrail():
        agent = Agent()
        answer, _ = agent.chat("book me the F9 707 flight from SFO to LGA on 11/11")
        assert (
            answer
            == "I've completed the following for you:\n\nBooking confirmed with booking ID BK-A3B1799D for a total price of USD $80.84.\n\nFlights:\n1. Flight F9-SFO-LGA-2025-11-11T17:00 (basic fare) (USD $80.84)"
        )


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


def test_add_service_to_booking_fallback() -> None:
    agent = Agent()
    agent.chat("book me the F9 707 flight from SFO to LGA on 11/11")
    with mock_cleanlab_validation_with_guardrail():
        answer, _ = agent.chat("Add a checked bag to my booking")
        assert (
            answer
            == "I've completed the following for you:\n\nAdded Checked Bag (USD $37.91) to flight F9-SFO-LGA-2025-11-11T17:00.\nYour add-ons for this flight are: Checked Bag"
        )


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


def test_check_in_fallback() -> None:
    agent = Agent()
    agent.chat("book me the F9 707 flight from SFO to LGA on 11/11")
    with mock_cleanlab_validation_with_guardrail():
        answer, _ = agent.chat("Check me in for my flight")
        assert (
            answer
            == "I've completed the following for you:\n\nChecked in for flight F9-SFO-LGA-2025-11-11T17:00. Your seat assignment is 19F."
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
