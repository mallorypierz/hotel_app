import io
import json
import traceback
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

import pytest

from backend.app import geocoding


@pytest.fixture(autouse=True)
def fake_provider(monkeypatch):
    monkeypatch.setattr(geocoding.config, 'GEOAPIFY_API_KEY', 'fake-test-secret')
    def unexpected_request(*args, **kwargs):
        pytest.fail('Unexpected provider request')
    monkeypatch.setattr(geocoding, 'urlopen', unexpected_request)


def mock_response(monkeypatch, payload, status=200):
    def open_response(url, timeout):
        parts = urlsplit(url)
        assert parts.scheme == 'https'
        assert parts.netloc == 'api.geoapify.com'
        assert parts.path == '/v1/geocode/search'
        assert parse_qs(parts.query) == {
            'postcode': ['16802'], 'type': ['postcode'],
            'filter': ['countrycode:us'], 'format': ['json'],
            'apiKey': ['fake-test-secret'],
        }
        assert timeout == 10
        response = io.BytesIO(payload if isinstance(payload, bytes) else json.dumps(payload).encode())
        response.status = status
        return response
    monkeypatch.setattr(geocoding, 'urlopen', open_response)


def location(**changes):
    return dict({'postcode': '16802', 'country_code': 'us',
                 'lat': 40.8, 'lon': -77.86, 'city': 'University Park'}, **changes)


def test_success(monkeypatch):
    mock_response(monkeypatch, {'results': [location(postcode='99999'), location()]})
    assert geocoding.lookup_zip('16802').model_dump() == {
        'postcode': '16802', 'country_code': 'us', 'latitude': 40.8,
        'longitude': -77.86, 'locality': 'University Park',
    }


def test_optional_locality(monkeypatch):
    mock_response(monkeypatch, {'results': [location(city=None)]})
    assert geocoding.lookup_zip('16802').locality is None


@pytest.mark.parametrize('results', [
    [], [location(postcode='16801')], [location(country_code='ca')],
    [location(lat=None)], [location(lat=91)], [location(lon=-181)],
    [location(lat=float('nan'))], [location(lon=float('inf'))],
    [location(lat=True)], [location(lat='40.8')],
])
def test_unresolved(monkeypatch, results):
    mock_response(monkeypatch, {'results': results})
    assert geocoding.lookup_zip('16802') is None


@pytest.mark.parametrize('payload', [b'not json', {}, [], {'results': None}, {'results': [None]}])
def test_malformed_response(monkeypatch, payload):
    mock_response(monkeypatch, payload)
    with pytest.raises(geocoding.ProviderRequestError):
        geocoding.lookup_zip('16802')


@pytest.mark.parametrize('error', [
    URLError('https://example.test/?apiKey=fake-test-secret'),
    HTTPError('https://example.test/?apiKey=fake-test-secret', 403, 'fake-test-secret', {}, None),
    TimeoutError('fake-test-secret'),
])
def test_request_failure_is_sanitized(monkeypatch, capsys, error):
    def fail(*args, **kwargs):
        raise error
    monkeypatch.setattr(geocoding, 'urlopen', fail)
    with pytest.raises(geocoding.ProviderRequestError) as caught:
        geocoding.lookup_zip('16802')
    rendered = ''.join(traceback.format_exception(caught.value))
    assert 'fake-test-secret' not in rendered
    assert 'https://' not in rendered
    assert str(caught.value) == 'Geocoding provider request failed.'
    assert capsys.readouterr() == ('', '')


def test_http_failure(monkeypatch):
    mock_response(monkeypatch, {'results': []}, status=503)
    with pytest.raises(geocoding.ProviderRequestError):
        geocoding.lookup_zip('16802')


def test_missing_key(monkeypatch):
    monkeypatch.setattr(geocoding.config, 'GEOAPIFY_API_KEY', '')
    with pytest.raises(geocoding.ProviderRequestError, match='not configured'):
        geocoding.lookup_zip('16802')


@pytest.mark.parametrize('postcode', [16802, '', '1680', '168021', ' 16802', 'abcde'])
def test_invalid_input(postcode):
    with pytest.raises(ValueError):
        geocoding.lookup_zip(postcode)
