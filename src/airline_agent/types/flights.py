from pydantic import BaseModel, Field


class FlightDealInfo(BaseModel, frozen=True):
    """Flight information extracted from the website."""

    origin: str = Field(..., description="Origin city and airport code (e.g., 'Denver, CO (DEN)')")
    destination: str = Field(..., description="Destination city and airport code (e.g., 'Las Vegas, NV (LAS)')")
    fare_type: str = Field(..., description="Type of fare (e.g., 'One-way / Discount Den Basic Fare')")
    departure_date: str = Field(..., description="Departure date information (e.g., 'Departing Feb 3, 2026')")
    starting_price: str = Field(..., description="Starting price for the flight (e.g., '$19')")
    last_seen: str = Field(..., description="When the price was last seen (e.g., '15 hours ago')")
