"""Compatibility entry point for the preserved Part 1 city-search interface."""
from .database import DATA
from .controller import search
from .models import CitySearchQuery, HotelStay

HOTELS_FILE = DATA / 'hotels.csv'
TRIPS_FILE = DATA / 'trips.csv'


def search_hotels(query: CitySearchQuery) -> list[HotelStay]:
    return [HotelStay(**row) for row in search(query.city, city_only=True)]
