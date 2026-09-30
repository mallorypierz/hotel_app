"""External places are discovery data, separate from sample bookable stays."""
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, model_validator

Latitude = Annotated[float, Field(strict=True, ge=-90, le=90, allow_inf_nan=False)]
Longitude = Annotated[float, Field(strict=True, ge=-180, le=180, allow_inf_nan=False)]
ProviderText = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1)]


class SearchCenter(BaseModel):
    postcode: str = Field(strict=True, pattern=r'^[0-9]{5}$', min_length=5, max_length=5)
    country_code: Literal['us'] = 'us'
    locality: ProviderText | None = None
    latitude: Latitude
    longitude: Longitude


class ExternalHotel(BaseModel):
    place_id: ProviderText
    name: ProviderText | None = None
    address: ProviderText | None = None
    latitude: Latitude
    longitude: Longitude


class HotelDiscoveryResponse(BaseModel):
    provider: Literal['geoapify'] = 'geoapify'
    center: SearchCenter
    radius_meters: Literal[5000] = 5000
    hotels: list[ExternalHotel] = Field(max_length=20)
    count: int = Field(ge=0, le=20)
    limit: Literal[20] = 20
    limit_reached: bool
    omitted_count: int = Field(ge=0)
    duplicates_removed: int = Field(ge=0)

    @model_validator(mode='after')
    def consistent_counts(self):
        if self.count != len(self.hotels) or len({h.place_id for h in self.hotels}) != self.count:
            raise ValueError('Hotel count and unique IDs must agree.')
        return self
