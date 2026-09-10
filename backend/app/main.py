from typing import Annotated

from fastapi import FastAPI, Query

from .models import CitySearchQuery, HotelSearchResponse
from .repository import search_hotels


app = FastAPI(title="Hotel Search API", version="0.1.0")


@app.get("/api/hotels", response_model=HotelSearchResponse)
def get_hotels(query: Annotated[CitySearchQuery, Query()]):
    hotels = search_hotels(query)
    return HotelSearchResponse(hotels=hotels, count=len(hotels))
