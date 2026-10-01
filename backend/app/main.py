from typing import Annotated

from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException, Response

from .models import HotelSearchResponse, BookingCreate, Booking, BookingHistory, DemoUser
from .database import initialize
from . import config, controller, geocoding, discovery
from .discovery_models import HotelDiscoveryResponse
from .provider import ProviderLimitedError
from .local_routes import register as register_local_routes


@asynccontextmanager
async def lifespan(app):
    initialize()
    yield


app = FastAPI(title="Wayfinder Hotels API", version="0.2.0", lifespan=lifespan)
register_local_routes(app)


@app.get('/api/health')
def get_health():
    return {
        'status': 'ok',
        'geoapify': 'key is configured' if config.GEOAPIFY_API_KEY else 'key is not configured',
    }


@app.get('/api/demo/zip-location', response_model=geocoding.ZipLocation)
def get_demo_zip_location(
    postcode: Annotated[str, Query(pattern=r"^[0-9]{5}$", min_length=5, max_length=5)] = "16802",
):
    try:
        location = geocoding.lookup_zip(postcode)
    except geocoding.MissingConfigurationError:
        raise HTTPException(503, 'Geocoding key is not configured.') from None
    except geocoding.ProviderRequestError:
        raise HTTPException(502, 'Geocoding provider request failed.') from None
    if location is None:
        raise HTTPException(404, f'ZIP {postcode} could not be resolved.')
    return location


@app.get('/api/discovery/hotels', response_model=HotelDiscoveryResponse)
def get_discovery_hotels(
    postcode: Annotated[str, Query(pattern=r"^[0-9]{5}$", min_length=5, max_length=5)],
):
    try:
        return discovery.search_hotels(postcode)
    except geocoding.MissingConfigurationError:
        raise HTTPException(503, {'code': 'service_unconfigured',
                                  'message': 'Hotel search is not configured.'}) from None
    except discovery.ZipUnresolvedError:
        raise HTTPException(404, {'code': 'zip_unresolved',
                                  'message': 'The requested U.S. ZIP could not be located.'}) from None
    except ProviderLimitedError as error:
        headers = {'Retry-After': error.retry_after} if error.retry_after else None
        raise HTTPException(503, {'code': 'provider_limited',
                                  'message': 'Hotel search is temporarily limited. Try again later.'},
                            headers=headers) from None
    except geocoding.ProviderRequestError:
        raise HTTPException(502, {'code': 'provider_error',
                                  'message': 'Hotel search could not be completed.'}) from None


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
