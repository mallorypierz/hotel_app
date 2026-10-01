"""Local persistence contracts, separate from the frozen discovery API."""
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from .discovery_models import Latitude, Longitude, SearchCenter

ProviderId = Annotated[str, Field(strict=True, min_length=1)]


class LocalHotel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    place_id: ProviderId
    name: str | None = None
    address: str | None = None
    latitude: Latitude
    longitude: Longitude


class SaveHotel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    hotel: LocalHotel
    center: SearchCenter


class DemoNight(BaseModel):
    stay_date: date
    nightly_rate_cents: int = Field(ge=0)
    rooms_available: int = Field(ge=0)


class SavedHotel(LocalHotel):
    nights: list[DemoNight]


class LocalResults(BaseModel):
    source: Literal['local'] = 'local'
    postcode: str
    center: SearchCenter | None
    radius_meters: Literal[5000] = 5000
    hotels: list[SavedHotel]
    count: int
    saved_ids: list[str]
