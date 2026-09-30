"""ZIP lookup controller; independent of hotel and database data."""
import re
from urllib.parse import urlencode
from urllib.request import urlopen

from pydantic import BaseModel, Field, ValidationError

from . import config
from .provider import MissingConfigurationError, ProviderRequestError, request_json


class ZipLocation(BaseModel):
    postcode: str
    country_code: str
    latitude: float = Field(strict=True, ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(strict=True, ge=-180, le=180, allow_inf_nan=False)
    locality: str | None = None


def lookup_zip(postcode: str, *, strict: bool = False) -> ZipLocation | None:
    """Return a matching U.S. location, None if unresolved, or a safe error."""
    if not isinstance(postcode, str) or not re.fullmatch(r'[0-9]{5}', postcode):
        raise ValueError('ZIP must be a five-digit string.')
    if not config.GEOAPIFY_API_KEY:
        raise MissingConfigurationError('Geocoding key is not configured.')
    query = urlencode({
        'postcode': postcode, 'type': 'postcode',
        'filter': 'countrycode:us', 'format': 'json',
        'apiKey': config.GEOAPIFY_API_KEY,
        **({'limit': 5} if strict else {}),
    })
    url = 'https://api.geoapify.com/v1/geocode/search?' + query
    payload = request_json(url, urlopen)
    if not isinstance(payload, dict) or not isinstance(payload.get('results'), list):
        raise ProviderRequestError('Geocoding provider returned an invalid response.')
    for result in payload['results']:
        if not isinstance(result, dict):
            raise ProviderRequestError('Geocoding provider returned an invalid response.')
        if result.get('postcode') != postcode or result.get('country_code') != 'us':
            continue
        if strict and result.get('result_type') != 'postcode':
            continue
        locality = next((result[field].strip() for field in ('city', 'town', 'village', 'locality')
                         if isinstance(result.get(field), str) and result[field].strip()), None)
        try:
            return ZipLocation(postcode=postcode, country_code='us',
                               latitude=result.get('lat'), longitude=result.get('lon'),
                               locality=locality)
        except ValidationError:
            if strict:
                raise ProviderRequestError('Geocoding provider returned invalid coordinates.') from None
            continue
    return None
