import json
import time
import urllib.parse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from airline_agent.types.flights import FlightInfo

FLIGHTS_URL = "https://flights.flyfrontier.com"
CITY_TO_CITY_SITEMAP_URL = "https://flights.flyfrontier.com/en/sitemap/city-to-city-flights/page-1"
FLIGHTS_FROM_CITY_SITEMAP_URL = "https://flights.flyfrontier.com/en/sitemap/flights-from-city/page-1"
SITEMAP_URLS = [CITY_TO_CITY_SITEMAP_URL, FLIGHTS_FROM_CITY_SITEMAP_URL]


class Flights:
    def __init__(self):
        self.city_to_city_urls = self._fetch_urls(CITY_TO_CITY_SITEMAP_URL)
        self.flights_from_city_urls = self._fetch_urls(FLIGHTS_FROM_CITY_SITEMAP_URL)

    def _rel_to_abs_url(self, rel_url: str) -> str:
        """Convert a relative URL to an absolute URL."""
        return urllib.parse.urljoin(FLIGHTS_URL, rel_url)

    def _fetch_html_with_js(self, url: str) -> str:
        """Fetch HTML from a URL using Selenium to render JavaScript.

        Args:
            url: The URL to fetch
            sleep_time: Time to wait for JavaScript to render (in seconds)

        Returns:
            str: The rendered HTML page source
        """
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(1)
        html = driver.page_source
        driver.quit()
        return html

    def _fetch_urls(self, url: str) -> list[str]:
        """Fetch sitemap URLs from a page using Selenium to render JavaScript."""
        html = self._fetch_html_with_js(url)
        soup = BeautifulSoup(html, "html5lib")
        main_div = soup.find("div", id="main")

        all_uls = main_div.find_all("ul")
        ul = all_uls[1]
        all_rel_urls = [
            str(li.find("a").attrs["href"]) for li in ul.find_all("li") if li.find("a") and "href" in li.find("a").attrs
        ]
        return [self._rel_to_abs_url(rel_url) for rel_url in all_rel_urls]

    def list_city_to_city_flights(self) -> list[str]:
        """List all city-to-city flight URLs e.g. https://flights.flyfrontier.com/en/flights-from-aguadilla-to-miami"""
        return self.city_to_city_urls

    def list_flights_from_city(self) -> list[str]:
        """List all flights from city URLs e.g. https://flights.flyfrontier.com/en/flights-from-aguadilla"""
        return self.flights_from_city_urls

    def search_flights(self, url: str) -> list[FlightInfo]:
        """Search for flights on the given URL and return a list of FlightInfo objects. Returns maximum 20 flights."""
        html = self._fetch_html_with_js(url)
        soup = BeautifulSoup(html, "html5lib")

        # Find the __NEXT_DATA__ script tag containing JSON data
        script_tag = soup.find("script", {"id": "__NEXT_DATA__", "type": "application/json"})
        if not script_tag:
            return []

        try:
            json_data = json.loads(script_tag.string)
        except json.JSONDecodeError:
            return []

        apollo_state = json_data.get("props", {}).get("pageProps", {}).get("apolloState", {})
        if not apollo_state or "data" not in apollo_state:
            return []

        data = apollo_state["data"]

        fares_data = None
        for key, value in data.items():
            if key.startswith("StandardFareModule:") and isinstance(value, dict) and "fares" in value:
                fares_data = value["fares"]
                break

        if not fares_data:
            return []

        flights = []
        for fare in fares_data:
            origin_city = fare.get("originCity", "")
            origin_code = fare.get("originAirportCode", "")
            origin = f"{origin_city} ({origin_code})" if origin_code else origin_city

            destination_city = fare.get("destinationCity", "")
            destination_code = fare.get("destinationAirportCode", "")
            destination = f"{destination_city} ({destination_code})" if destination_code else destination_city

            flight_type = fare.get("formattedFlightType", "")
            travel_class = fare.get("formattedTravelClass", "")
            fare_type = (
                f"{flight_type} / {travel_class}" if flight_type and travel_class else travel_class or flight_type
            )

            departure_date = fare.get("formattedDepartureDate", "")
            dates = f"Departing {departure_date}" if departure_date else ""

            starting_price = fare.get("formattedTotalPrice", "")

            price_last_seen = fare.get("priceLastSeen", {})
            if price_last_seen:
                value = price_last_seen.get("value", "")
                unit = price_last_seen.get("unit", "")
                last_seen = f"{value} {unit} ago" if value and unit else ""
            else:
                last_seen = ""

            if origin and destination and starting_price:
                flight_info = FlightInfo(
                    origin=origin,
                    destination=destination,
                    fare_type=fare_type,
                    dates=dates,
                    starting_price=starting_price,
                    last_seen=last_seen,
                )
                flights.append(flight_info)

        return flights
