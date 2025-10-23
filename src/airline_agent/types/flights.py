from datetime import datetime

from pydantic import BaseModel, Field


class FlightInfo(BaseModel, frozen=True):
    """Flight information data structure for Frontier Airlines flights.

    Includes both standard pricing (available to all customers) and \"Discount Den\" pricing
    (available only to Frontier's \"Discount Den\" members).
    """

    flight_num: str = Field(..., description="Frontier Airlines flight number")
    departure_location: str = Field(..., description="Departure location e.g. San Francisco, CA (SFO)")
    arrival_location: str = Field(..., description="Arrival location e.g. San Francisco, CA (SFO)")
    scheduled_departure: datetime = Field(
        ..., description="Scheduled departure time (in local timezone, in ISO 8601 format)"
    )
    scheduled_arrival: datetime = Field(
        ..., description="Scheduled arrival time (in local timezone, in ISO 8601 format)"
    )
    basic_price_standard: int = Field(..., description="Basic fare standard price (in USD)")
    economy_price_standard: int = Field(..., description="Economy bundle standard price (in USD)")
    premium_price_standard: int = Field(..., description="Premium bundle standard price (in USD)")
    business_price_standard: int = Field(..., description="Business bundle standard price (in USD)")
    basic_price_discount_den: int = Field(
        ..., description='Basic fare price for Frontier\'s "Discount Den" members only (in USD)'
    )
    economy_price_discount_den: int = Field(
        ..., description='Economy bundle price for Frontier\'s "Discount Den" members only (in USD)'
    )
    premium_price_discount_den: int = Field(
        ..., description='Premium bundle price for Frontier\'s "Discount Den" members only (in USD)'
    )
    business_price_discount_den: int = Field(
        ..., description='Business bundle price for Frontier\'s "Discount Den" members only (in USD)'
    )
