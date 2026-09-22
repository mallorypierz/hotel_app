from typing import Annotated

from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException, Response

from .models import HotelSearchResponse, BookingCreate, Booking, BookingHistory, DemoUser
from .database import initialize
from . import controller


@asynccontextmanager
async def lifespan(app):
    initialize()
    yield


app = FastAPI(title="Wayfinder Hotels API", version="0.2.0", lifespan=lifespan)


@app.get("/api/hotels", response_model=HotelSearchResponse)
def get_hotels(city: str | None = None, q: str | None = None):
    text = (q if q is not None else city or '').strip()
    if not text or len(text) > 80:
        raise HTTPException(422, 'Enter a hotel name or city (1–80 characters).')
    hotels = controller.search(text, city_only=q is None)
    return HotelSearchResponse(hotels=hotels, count=len(hotels))


@app.get('/api/users', response_model=list[DemoUser])
def get_users():
    return controller.users()


@app.get('/api/bookings', response_model=list[BookingHistory])
def get_bookings(user_id: Annotated[str, Query(min_length=1, max_length=80)]):
    return controller.history(user_id)


@app.post('/api/bookings', response_model=Booking, status_code=201)
def create_booking(payload: BookingCreate):
    return controller.create(payload)


@app.patch('/api/bookings/{booking_id}/cancel', response_model=Booking)
def cancel_booking(booking_id: str):
    return controller.cancel(booking_id)


@app.delete('/api/bookings/{booking_id}', status_code=204)
def delete_booking(booking_id: str):
    controller.delete(booking_id)
    return Response(status_code=204)
