"""Controlled transport plus actual ASGI routing; no network or persistent DB."""
import asyncio
import io
import json
import traceback
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

import pytest

from backend.app import config, discovery, geocoding
from backend.app.main import app
from backend.app.provider import ProviderRequestError


def center(**changes):
    return dict({'postcode': '02108', 'country_code': 'us', 'result_type': 'postcode',
                 'lat': 42.36, 'lon': -71.06, 'city': 'Boston'}, **changes)


def hotel(**changes):
    return {'type': 'Feature', 'properties': dict({
        'place_id': 'provider-id-1', 'name': 'Provider Hotel',
        'formatted': 'Provider address', 'lat': 42.361, 'lon': -71.061,
    }, **changes)}


@pytest.fixture(autouse=True)
def prevent_network(monkeypatch):
    monkeypatch.setattr(config, 'GEOAPIFY_API_KEY', 'fake-test-secret')
    def forbidden(*args, **kwargs):
        pytest.fail('Unexpected provider call')
    monkeypatch.setattr(geocoding, 'urlopen', forbidden)
    monkeypatch.setattr(discovery, 'urlopen', forbidden)


def wire(monkeypatch, geo=None, places=None, failure_stage=None, error=None):
    calls = []
    def opener(url, timeout):
        parts = urlsplit(url)
        assert parts.scheme == 'https' and parts.netloc == 'api.geoapify.com'
        assert timeout == 10
        stage = 'geo' if parts.path == '/v1/geocode/search' else 'places'
        assert parts.path in ('/v1/geocode/search', '/v2/places')
        calls.append((stage, parse_qs(parts.query)))
        if stage == failure_stage:
            raise error
        payload = (geo if geo is not None else {'results': [center()]}) if stage == 'geo' else (
            places if places is not None else {'features': [hotel()]})
        response = io.BytesIO(payload if isinstance(payload, bytes) else json.dumps(payload).encode())
        response.status = 200
        return response
    monkeypatch.setattr(geocoding, 'urlopen', opener)
    monkeypatch.setattr(discovery, 'urlopen', opener)
    return calls


def request(query=b'postcode=02108'):
    async def run():
        messages = []
        async def receive():
            return {'type': 'http.request', 'body': b'', 'more_body': False}
        async def send(message):
            messages.append(message)
        await app({'type': 'http', 'asgi': {'version': '3.0'}, 'http_version': '1.1',
                   'method': 'GET', 'scheme': 'http', 'path': '/api/discovery/hotels',
                   'raw_path': b'/api/discovery/hotels', 'query_string': query,
                   'root_path': '', 'headers': [], 'server': ('test', 80),
                   'client': ('test', 1234)}, receive, send)
        start = next(m for m in messages if m['type'] == 'http.response.start')
        body = b''.join(m.get('body', b'') for m in messages if m['type'] == 'http.response.body')
        return start['status'], json.loads(body), dict(start['headers'])
    return asyncio.run(run())


def test_populated_and_request_contract(monkeypatch):
    calls = wire(monkeypatch)
    status, body, _ = request()
    assert status == 200
    assert body == dict(provider='geoapify', center=dict(postcode='02108', country_code='us',
        locality='Boston', latitude=42.36, longitude=-71.06), radius_meters=5000,
        hotels=[dict(place_id='provider-id-1', name='Provider Hotel', address='Provider address',
                     latitude=42.361, longitude=-71.061)], count=1, limit=20,
        limit_reached=False, omitted_count=0, duplicates_removed=0)
    assert calls == [('geo', {'postcode': ['02108'], 'type': ['postcode'],
        'filter': ['countrycode:us'], 'format': ['json'], 'limit': ['5'],
        'apiKey': ['fake-test-secret']}), ('places', {'categories': ['accommodation.hotel'],
        'filter': ['circle:-71.06,42.36,5000'], 'bias': ['proximity:-71.06,42.36'],
        'limit': ['20'], 'apiKey': ['fake-test-secret']})]


@pytest.mark.parametrize('query', [b'', b'postcode=', b'postcode=2108', b'postcode=002108',
    b'postcode=abcde', b'postcode=%2002108', b'postcode=02108%0A',
    b'postcode=%EF%BC%90%EF%BC%92%EF%BC%91%EF%BC%90%EF%BC%98'])
def test_invalid_input_no_provider(query):
    assert request(query)[0] == 422


@pytest.mark.parametrize('results', [[], [center(postcode='02109')], [center(country_code='ca')],
    [center(result_type='city')], [center(result_type=None)]])
def test_unresolved_never_searches_places(monkeypatch, results):
    calls = wire(monkeypatch, geo={'results': results})
    status, body, _ = request()
    assert status == 404 and body['detail']['code'] == 'zip_unresolved'
    assert len(calls) == 1


@pytest.mark.parametrize('payload', [{}, [], {'results': None}, {'results': [None]}, b'invalid',
    *[{'results': [center(lat=v)]} for v in [None, True, '42.36', 91, float('nan')]],
    {'results': [center(lon=float('inf'))]}, {'results': [center(lon=-181)]}])
def test_invalid_geocoding_is_failure(monkeypatch, payload):
    calls = wire(monkeypatch, geo=payload)
    assert request()[0] == 502
    assert len(calls) == 1


def test_skips_mismatch_then_uses_exact_returned_center(monkeypatch):
    calls = wire(monkeypatch, geo={'results': [center(postcode='10001'), center(lat=40, lon=-70)]},
                 places={'features': []})
    assert request()[1]['center']['latitude'] == 40
    assert calls[1][1]['filter'] == ['circle:-70.0,40.0,5000']


def test_true_empty(monkeypatch):
    wire(monkeypatch, places={'features': []})
    status, body, _ = request()
    assert status == 200 and body['hotels'] == [] and body['count'] == 0
    assert body['center']['postcode'] == '02108'
    assert body['omitted_count'] == body['duplicates_removed'] == 0
    assert body['limit_reached'] is False


@pytest.mark.parametrize('props, expected', [
    ({'name': None, 'formatted': None}, None),
    ({'name': ' ', 'formatted': ' ', 'address_line1': ' 10 Main St ', 'address_line2': 'Boston'}, '10 Main St, Boston'),
    ({'name': 7, 'formatted': None, 'address_line2': 'Boston'}, 'Boston'),
])
def test_missing_optional_fields(monkeypatch, props, expected):
    wire(monkeypatch, places={'features': [hotel(**props)]})
    status, body, _ = request()
    assert status == 200
    assert body['hotels'][0]['name'] is None
    assert body['hotels'][0]['address'] == expected
    assert 'nightly_price' not in body['hotels'][0]


@pytest.mark.parametrize('bad', [None, {}, {'properties': []}, hotel(place_id=None),
    hotel(place_id=' '), hotel(place_id=42), hotel(lat=True), hotel(lat='42.36'),
    hotel(lat=None), hotel(lat=91), hotel(lon=-181), hotel(lon=float('nan')),
    hotel(lat=float('inf')), hotel(lat=43)])
def test_unusable_records_partial_and_all_bad(monkeypatch, bad):
    wire(monkeypatch, places={'features': [bad, hotel()]})
    status, body, _ = request()
    assert status == 200 and body['count'] == 1 and body['omitted_count'] == 1
    wire(monkeypatch, places={'features': [bad]})
    assert request()[0] == 502


def test_cap_dedup_and_first_valid_order(monkeypatch):
    features = [hotel(lat=None), hotel(name='first valid'), hotel(name='duplicate')]
    features += [hotel(place_id=f'id-{n}') for n in range(17)]
    wire(monkeypatch, places={'features': features})
    status, body, _ = request()
    assert status == 200 and body['limit_reached'] is True
    assert body['count'] == 18 and body['omitted_count'] == body['duplicates_removed'] == 1
    assert body['hotels'][0]['name'] == 'first valid'
    assert [h['place_id'] for h in body['hotels'][1:]] == [f'id-{n}' for n in range(17)]


@pytest.mark.parametrize('payload', [{}, [], {'features': None}, {'features': {}},
    {'features': [hotel()] * 21}, b'not json', {'error': 'quota exceeded'}])
def test_invalid_places_response(monkeypatch, payload):
    wire(monkeypatch, places=payload)
    assert request()[0] == 502


def test_missing_configuration():
    config_value = config.GEOAPIFY_API_KEY
    try:
        config.GEOAPIFY_API_KEY = ''
        status, body, _ = request()
        assert status == 503 and body['detail']['code'] == 'service_unconfigured'
    finally:
        config.GEOAPIFY_API_KEY = config_value


@pytest.mark.parametrize('stage', ['geo', 'places'])
@pytest.mark.parametrize('kind', ['timeout', 'network', 'credentials', 'server', 'rate', 'quota', 'unsafe_retry'])
def test_failures_safe_and_distinct(monkeypatch, capsys, stage, kind):
    secret_url = 'https://example.test/?apiKey=fake-test-secret'
    if kind == 'timeout':
        error = TimeoutError(secret_url)
    elif kind == 'network':
        error = URLError(secret_url)
    else:
        status = {'credentials': 403, 'server': 500, 'rate': 429, 'quota': 403, 'unsafe_retry': 429}[kind]
        message = 'quota exceeded' if kind == 'quota' else 'fake-test-secret'
        headers = {'Retry-After': '12' if kind != 'unsafe_retry' else 'fake-test-secret\r\nBad: value'}
        error = HTTPError(secret_url, status, 'fake-test-secret', headers,
                          io.BytesIO(json.dumps({'message': message}).encode()))
    calls = wire(monkeypatch, failure_stage=stage, error=error)
    status, body, headers = request()
    limited = kind in ('rate', 'quota', 'unsafe_retry')
    assert status == (503 if limited else 502)
    assert body['detail']['code'] == ('provider_limited' if limited else 'provider_error')
    assert headers.get(b'retry-after') == (b'12' if kind in ('rate', 'quota') else None)
    assert len(calls) == (1 if stage == 'geo' else 2)
    assert 'fake-test-secret' not in json.dumps(body) and 'https://' not in json.dumps(body)
    assert capsys.readouterr() == ('', '')


def test_transport_traceback_sanitized(monkeypatch):
    wire(monkeypatch, failure_stage='places', error=URLError('fake-test-secret'))
    with pytest.raises(ProviderRequestError) as caught:
        discovery.search_hotels('02108')
    assert 'fake-test-secret' not in ''.join(traceback.format_exception(caught.value))
