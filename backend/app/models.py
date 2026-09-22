from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class HotelStay(BaseModel):
    hotel_id: str
    name: str
    city: str
    state: str
    location: str
    nightly_price: float = Field(gt=0)
    trip_id: str
    trip_name: str
    check_in: str
    check_out: str


class CitySearchQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1, max_length=80)

    @field_validator("city")
    @classmethod
    def city_must_have_text(cls, value: str) -> str:
        city = value.strip()
        if not city:
            raise ValueError("city must not be blank")
        return city


class HotelSearchResponse(BaseModel):
    hotels: list[HotelStay]
    count: int


class BookingCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    user_id: str = Field(min_length=1, max_length=80)
    trip_id: str = Field(min_length=1, max_length=80)


class Booking(BaseModel):
    booking_id: str
    user_id: str
    trip_id: str
    booked_on: str
    status: Literal['confirmed', 'cancelled']


class DemoUser(BaseModel):
    user_id: str
    display_name: str


class BookingHistory(Booking):
    display_name: str
    hotel_name: str
    city: str
    state: str
    nightly_rate_usd: float
    trip_name: str
    check_in: str
    check_out: str
