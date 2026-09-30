import asyncio
import json

import pytest

from backend.app import geocoding
from backend.app.main import app


def request_demo(query=b''):
    """Exercise FastAPI routing and serialization without another HTTP package."""
    async def request():
        messages = []

        async def receive():
            return {'type': 'http.request', 'body': b'', 'more_body': False}

        async def send(message):
            messages.append(message)

        await app({'type': 'http', 'asgi': {'version': '3.0'},
                   'http_version': '1.1', 'method': 'GET', 'scheme': 'http',
                   'path': '/api/demo/zip-location', 'raw_path': b'/api/demo/zip-location',
                   'query_string': query, 'root_path': '', 'headers': [],
                   'server': ('test', 80), 'client': ('test', 1234)}, receive, send)
        status = next(m['status'] for m in messages if m['type'] == 'http.response.start')
        body = b''.join(m.get('body', b'') for m in messages if m['type'] == 'http.response.body')
        return status, json.loads(body)

    return asyncio.run(request())


def test_demo_success(monkeypatch):
    expected = dict(postcode='16802', country_code='us', latitude=40.8,
                    longitude=-77.86, locality='University Park')
    calls = []

    def lookup(postcode):
        calls.append(postcode)
        return geocoding.ZipLocation(**expected)

    monkeypatch.setattr(geocoding, 'lookup_zip', lookup)
    assert request_demo() == (200, expected)
    assert calls == ['16802']


@pytest.mark.parametrize('outcome, status, detail', [
    (None, 404, 'ZIP 16802 could not be resolved.'),
    (geocoding.MissingConfigurationError('private'), 503, 'Geocoding key is not configured.'),
    (geocoding.ProviderRequestError('https://example.test/?apiKey=private'),
     502, 'Geocoding provider request failed.'),
])
def test_demo_errors(monkeypatch, outcome, status, detail):
    def lookup(postcode):
        assert postcode == '16802'
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(geocoding, 'lookup_zip', lookup)
    assert request_demo() == (status, {'detail': detail})


def test_entered_zip_preserves_leading_zero(monkeypatch):
    def lookup(postcode):
        assert postcode == '02108'
        return geocoding.ZipLocation(postcode=postcode, country_code='us',
                                     latitude=42.36, longitude=-71.06, locality='Boston')

    monkeypatch.setattr(geocoding, 'lookup_zip', lookup)
    status, body = request_demo(b'postcode=02108')
    assert status == 200
    assert body['postcode'] == '02108'


@pytest.mark.parametrize('query', [
    b'postcode=', b'postcode=1234', b'postcode=123456', b'postcode=abcde',
    b'postcode=16802%0A',
])
def test_invalid_zip_never_calls_provider(monkeypatch, query):
    def lookup(postcode):
        pytest.fail('Invalid input must not reach the provider')

    monkeypatch.setattr(geocoding, 'lookup_zip', lookup)
    assert request_demo(query)[0] == 422


def test_unresolved_entered_zip(monkeypatch):
    monkeypatch.setattr(geocoding, 'lookup_zip', lambda postcode: None)
    assert request_demo(b'postcode=00000') == (
        404, {'detail': 'ZIP 00000 could not be resolved.'})
