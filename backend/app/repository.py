import csv
from pathlib import Path

from .models import CitySearchQuery, HotelStay


DATA_DIRECTORY = Path(__file__).resolve().parents[2] / "data"
HOTELS_FILE = DATA_DIRECTORY / "hotels.csv"
TRIPS_FILE = DATA_DIRECTORY / "trips.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as data_file:
        return list(csv.DictReader(data_file))


def search_hotels(query: CitySearchQuery) -> list[HotelStay]:
    hotels_by_id = {hotel["hotel_id"]: hotel for hotel in read_csv(HOTELS_FILE)}
    matching_stays = []

    for trip in read_csv(TRIPS_FILE):
        hotel = hotels_by_id.get(trip["hotel_id"])
        if hotel is None or query.city.casefold() not in hotel["city"].casefold():
            continue

        matching_stays.append(
            HotelStay(
                hotel_id=hotel["hotel_id"],
                name=hotel["hotel_name"],
                city=hotel["city"],
                state=hotel["state"],
                location=f'{hotel["city"]}, {hotel["state"]}',
                nightly_price=float(hotel["nightly_rate_usd"]),
                trip_id=trip["trip_id"],
                trip_name=trip["trip_name"],
                check_in=trip["check_in"],
                check_out=trip["check_out"],
            )
        )

    return matching_stays
