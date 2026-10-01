import sqlite3

import pytest
import asyncio
import json as json_module
from types import SimpleNamespace
from urllib.parse import urlencode, urlsplit

from backend.app import database
from backend.app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, 'DATABASE', tmp_path / 'local.sqlite3')
    database.initialize()
    return LocalClient()


class LocalClient:
    """Use the project's dependency-free ASGI test pattern."""
    def request(self, method, url, params=None, json=None):
        async def run():
            parts = urlsplit(url)
            messages = []
            async def receive():
                return {'type': 'http.request', 'body': json_module.dumps(json).encode() if json else b'', 'more_body': False}
            async def send(message):
                messages.append(message)
            await app({'type': 'http', 'asgi': {'version': '3.0'}, 'http_version': '1.1',
                       'method': method, 'scheme': 'http', 'path': parts.path,
                       'raw_path': parts.path.encode(), 'query_string': (urlencode(params) if params else parts.query).encode(),
                       'root_path': '', 'headers': [(b'content-type', b'application/json')],
                       'server': ('test', 80), 'client': ('test', 1234)}, receive, send)
            status = next(m['status'] for m in messages if m['type'] == 'http.response.start')
            body = b''.join(m.get('body', b'') for m in messages if m['type'] == 'http.response.body')
            return SimpleNamespace(status_code=status, text=body.decode(), json=lambda: json_module.loads(body))
        return asyncio.run(run())

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)


def payload(id='Provider/001-AbC ', zip='02108'):
    return dict(hotel=dict(place_id=id, name=None, address=None, latitude=42.36, longitude=-71.06),
                center=dict(postcode=zip, country_code='us', locality='Boston', latitude=42.357, longitude=-71.065))


def snapshot():
    with database.connection() as db:
        return {table: [tuple(r) for r in db.execute(f'SELECT * FROM {table} ORDER BY 1')]
                for table in ['hotels', 'trips', 'users', 'bookings', 'metadata']}


def test_save_multiple_zips_defaults_repeat_and_remove(client):
    before = snapshot()
    assert client.get('/api/local-hotels?postcode=02108').json()['hotels'] == []
    first = client.post('/api/local-hotels', json=payload())
    assert first.status_code == 200
    hotel = first.json()
    assert hotel['place_id'] == 'Provider/001-AbC '
    assert hotel['name'] is None
    assert hotel['nights'] == [dict(stay_date=f'2026-10-{d}', nightly_rate_cents=10000, rooms_available=20) for d in range(10, 15)]
    with database.connection() as db:
        db.execute('UPDATE demo_hotel_nights SET nightly_rate_cents=12345, rooms_available=3 WHERE stay_date=?', ('2026-10-10',))
    assert client.post('/api/local-hotels', json=payload()).status_code == 200
    assert client.post('/api/local-hotels', json=payload(zip='02109')).status_code == 200
    assert client.post('/api/local-hotels', json=payload('unrelated')).status_code == 200
    database.initialize()
    local = client.get('/api/local-hotels?postcode=02109').json()
    assert local['center'] == payload(zip='02109')['center']
    assert local['count'] == 1
    assert local['hotels'][0]['nights'][0]['nightly_rate_cents'] == 12345
    assert local['hotels'][0]['nights'][0]['rooms_available'] == 3
    assert len(local['hotels'][0]['nights']) == 5
    # Global provider-ID status is available even for a different searched ZIP.
    empty = client.get('/api/local-hotels?postcode=00001').json()
    assert empty['count'] == 0 and empty['center'] is None
    assert set(empty['saved_ids']) == {'Provider/001-AbC ', 'unrelated'}
    assert client.delete('/api/local-hotels', params={'hotel_id': 'Provider/001-AbC '}).status_code == 204
    assert client.delete('/api/local-hotels', params={'hotel_id': 'Provider/001-AbC '}).status_code == 204
    database.initialize()
    assert client.get('/api/local-hotels?postcode=02109').json()['count'] == 0
    remaining = client.get('/api/local-hotels?postcode=02108').json()
    assert remaining['saved_ids'] == ['unrelated'] and remaining['count'] == 1
    with database.connection() as db:
        for table in ['saved_hotels', 'saved_hotel_locations', 'demo_hotel_nights']:
            assert db.execute(f'SELECT count(*) FROM {table} WHERE hotel_id=?', ('Provider/001-AbC ',)).fetchone()[0] == 0
        assert db.execute('PRAGMA foreign_key_check').fetchall() == []
    assert snapshot() == before


def test_save_and_delete_are_atomic_and_errors_safe(client):
    with database.connection() as db:
        db.execute("CREATE TRIGGER fail_night BEFORE INSERT ON demo_hotel_nights BEGIN SELECT RAISE(ABORT, 'private detail'); END")
    r = client.post('/api/local-hotels', json=payload())
    assert r.status_code == 503 and 'private detail' not in r.text
    assert client.get('/api/local-hotels?postcode=02108').json()['count'] == 0
    with database.connection() as db:
        assert db.execute('SELECT count(*) FROM saved_hotels').fetchone()[0] == 0
        db.execute('DROP TRIGGER fail_night')
    client.post('/api/local-hotels', json=payload())
    before = client.get('/api/local-hotels?postcode=02108').json()
    with database.connection() as db:
        db.execute("CREATE TRIGGER fail_remove BEFORE DELETE ON saved_hotels BEGIN SELECT RAISE(ABORT, 'private detail'); END")
    r = client.delete('/api/local-hotels', params={'hotel_id': 'Provider/001-AbC '})
    assert r.status_code == 503 and 'private detail' not in r.text
    assert client.get('/api/local-hotels?postcode=02108').json() == before


@pytest.mark.parametrize('zip', ['2108', '123456', 'abcde', '１２３４５'])
def test_invalid_zip(client, zip):
    assert client.get('/api/local-hotels', params={'postcode': zip}).status_code == 422
    assert client.post('/api/local-hotels', json=payload(zip=zip)).status_code == 422


def test_invalid_hotel_and_failed_local_read(client, monkeypatch):
    bad = payload()
    bad['hotel']['latitude'] = 91
    assert client.post('/api/local-hotels', json=bad).status_code == 422
    bad = payload()
    bad['hotel']['place_id'] = ''
    assert client.post('/api/local-hotels', json=bad).status_code == 422
    from backend.app import local_controller
    def fail(_):
        raise sqlite3.OperationalError('private detail')
    monkeypatch.setattr(local_controller, 'search', fail)
    r = client.get('/api/local-hotels?postcode=02108')
    assert r.status_code == 503 and 'private detail' not in r.text
