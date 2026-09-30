"""Resolve an exact postcode before fetching one bounded hotel page."""
from math import asin, cos, radians, sin, sqrt
from urllib.parse import urlencode
from urllib.request import urlopen

from pydantic import ValidationError

from . import config, geocoding
from .discovery_models import ExternalHotel, HotelDiscoveryResponse, SearchCenter
from .provider import ProviderRequestError, request_json

RADIUS_METERS = 5000
RESULT_LIMIT = 20


class ZipUnresolvedError(Exception):
    pass


def provider_text(value):
    return value.strip() if isinstance(value, str) and value.strip() else None


def distance_meters(center, hotel):
    lat1, lat2 = radians(center.latitude), radians(hotel.latitude)
    dlat = lat2 - lat1
    dlon = radians(hotel.longitude - center.longitude)
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371008.8 * 2 * asin(sqrt(min(1, max(0, a))))


def parse_hotel(feature):
    if not isinstance(feature, dict) or not isinstance(feature.get('properties'), dict):
        raise ValueError('Invalid feature.')
    props = feature['properties']
    # Geoapify supplies lat/lon properties. Never replace them with the ZIP center.
    address = provider_text(props.get('formatted'))
    if address is None:
        address = ', '.join(text for key in ('address_line1', 'address_line2')
                            if (text := provider_text(props.get(key)))) or None
    return ExternalHotel(place_id=props.get('place_id'), name=provider_text(props.get('name')),
                         address=address, latitude=props.get('lat'), longitude=props.get('lon'))


def search_hotels(postcode: str) -> HotelDiscoveryResponse:
    location = geocoding.lookup_zip(postcode, strict=True)
    if location is None:
        raise ZipUnresolvedError()
    center = SearchCenter(**location.model_dump())
    point = f'{center.longitude},{center.latitude}'
    query = urlencode({'categories': 'accommodation.hotel',
                       'filter': f'circle:{point},{RADIUS_METERS}',
                       'bias': f'proximity:{point}', 'limit': RESULT_LIMIT,
                       'apiKey': config.GEOAPIFY_API_KEY})
    url = 'https://api.geoapify.com/v2/places?' + query
    payload = request_json(url, urlopen)
    if not isinstance(payload, dict) or not isinstance(payload.get('features'), list):
        raise ProviderRequestError('Invalid hotel provider response.')
    features = payload['features']
    if len(features) > RESULT_LIMIT:
        raise ProviderRequestError('Invalid hotel provider page size.')
    hotels, seen = [], set()
    omitted = duplicates = 0
    for feature in features:
        try:
            hotel = parse_hotel(feature)
            if distance_meters(center, hotel) > RADIUS_METERS:
                raise ValueError('Hotel is outside the requested radius.')
        except (ValidationError, ValueError):
            omitted += 1
            continue
        if hotel.place_id in seen:
            duplicates += 1
            continue
        seen.add(hotel.place_id)
        hotels.append(hotel)
    if features and not hotels:
        raise ProviderRequestError('No usable hotel provider records.')
    return HotelDiscoveryResponse(center=center, hotels=hotels, count=len(hotels),
                                  limit_reached=len(features) == RESULT_LIMIT,
                                  omitted_count=omitted, duplicates_removed=duplicates)
