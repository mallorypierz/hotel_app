"""Local-only routes with safe database errors."""
import sqlite3
from typing import Annotated

from fastapi import HTTPException, Query, Response

from . import local_controller
from .local_models import LocalResults, SavedHotel, SaveHotel



def database_call(operation, *args):
    try:
        return operation(*args)
    except sqlite3.Error:
        raise HTTPException(503, 'Local hotel storage is unavailable. Please retry.') from None


def get_local_hotels(postcode: Annotated[str, Query(pattern=r'^[0-9]{5}$', min_length=5, max_length=5)]):
    return database_call(local_controller.search, postcode)


def save_local_hotel(payload: SaveHotel):
    return database_call(local_controller.save, payload)


def remove_local_hotel(hotel_id: Annotated[str, Query(min_length=1)]):
    database_call(local_controller.remove, hotel_id)
    return Response(status_code=204)


def register(app):
    app.add_api_route('/api/local-hotels', get_local_hotels, methods=['GET'], response_model=LocalResults)
    app.add_api_route('/api/local-hotels', save_local_hotel, methods=['POST'], response_model=SavedHotel)
    app.add_api_route('/api/local-hotels', remove_local_hotel, methods=['DELETE'], status_code=204)
