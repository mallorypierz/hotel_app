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
