import pytest
from pydantic import ValidationError

from backend.app.main import app, get_hotels
from backend.app.models import CitySearchQuery
from backend.app.repository import HOTELS_FILE, TRIPS_FILE


def test_search_returns_matching_hotel():
    response = get_hotels(CitySearchQuery(city="Boston"))

    assert response.count == 4
    assert response.hotels[0].name == "Harbor Lantern Hotel"
    assert response.hotels[0].trip_name == "Boston Harbor Weekend"
    assert response.hotels[0].location == "Boston, MA"


def test_search_returns_empty_result():
    response = get_hotels(CitySearchQuery(city="Aspen"))

    assert response.count == 0
    assert response.hotels == []


@pytest.mark.parametrize("city", ["", "   "])
def test_search_rejects_blank_city(city):
    with pytest.raises(ValidationError):
        CitySearchQuery(city=city)


def test_search_data_sources_exist():
    assert HOTELS_FILE.name == "hotels.csv"
    assert TRIPS_FILE.name == "trips.csv"
    assert HOTELS_FILE.is_file()
    assert TRIPS_FILE.is_file()


def test_search_route_is_registered():
    assert "/api/hotels" in {route.path for route in app.routes}
