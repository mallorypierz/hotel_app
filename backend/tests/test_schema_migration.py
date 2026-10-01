"""Exercise migration compatibility and constraints on isolated databases."""
import sqlite3

import pytest

from backend.app import database


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / 'schema.sqlite3'
    database.initialize(path)
    return path


def legacy_snapshot(db):
    tables = ('hotels', 'trips', 'users', 'bookings', 'metadata')
    return {
        table: (
            db.execute('SELECT sql FROM sqlite_master WHERE name=?', (table,)).fetchone()[0],
            [tuple(row) for row in db.execute(f'SELECT * FROM {table} ORDER BY 1')],
        ) for table in tables
    }


def insert_hotel(db, hotel_id='Provider/001-AbC ', latitude=42.36, longitude=-71.06):
    db.execute('INSERT INTO saved_hotels (hotel_id, latitude, longitude) VALUES (?, ?, ?)',
               (hotel_id, latitude, longitude))


def test_existing_database_migrates_without_reseed(db_path, monkeypatch, tmp_path):
    with database.connection(db_path) as db:
        # Recreate the pre-migration schema with a user-edited booking record.
        db.execute('DROP TABLE demo_hotel_nights')
        db.execute('DROP TABLE saved_hotels')
        db.execute("UPDATE bookings SET status='cancelled' WHERE booking_id='B001'")
        db.execute("DELETE FROM bookings WHERE booking_id='B002'")
        before = legacy_snapshot(db)
    monkeypatch.setattr(database, 'DATA', tmp_path / 'no-csv-files')
    database.initialize(db_path)
    database.initialize(db_path)
    with database.connection(db_path) as db:
        assert legacy_snapshot(db) == before
        assert db.execute('SELECT count(*) FROM saved_hotels').fetchone()[0] == 0
        assert db.execute('SELECT count(*) FROM demo_hotel_nights').fetchone()[0] == 0


def test_fresh_database_defaults_ids_and_persistence(db_path):
    provider_id = 'Provider/001-AbC '
    with database.connection(db_path) as db:
        before = legacy_snapshot(db)
        insert_hotel(db, provider_id)
        insert_hotel(db, provider_id.lower())  # Exact case-sensitive identity.
        hotel = dict(db.execute('SELECT * FROM saved_hotels WHERE hotel_id=?', (provider_id,)).fetchone())
        assert hotel == dict(hotel_id=provider_id, name=None, address=None,
                             latitude=42.36, longitude=-71.06)
        with pytest.raises(sqlite3.IntegrityError):
            insert_hotel(db, provider_id)
        db.execute('INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)',
                   (provider_id, '2028-02-29'))
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)',
                       (provider_id, '2028-02-29'))
        db.execute('INSERT INTO demo_hotel_nights VALUES (?, ?, 0, 0)',
                   (provider_id, '2028-03-01'))
    database.initialize(db_path)
    with database.connection(db_path) as db:
        assert legacy_snapshot(db) == before
        rows = [tuple(row) for row in db.execute('SELECT * FROM demo_hotel_nights ORDER BY stay_date')]
        assert rows == [(provider_id, '2028-02-29', 10000, 20),
                        (provider_id, '2028-03-01', 0, 0)]
        assert db.execute('PRAGMA foreign_keys').fetchone()[0] == 1
        assert db.execute('PRAGMA foreign_key_check').fetchall() == []
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES ('missing', '2026-10-01')")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('DELETE FROM saved_hotels WHERE hotel_id=?', (provider_id,))


@pytest.mark.parametrize('column,value', [
    ('hotel_id', None), ('latitude', None), ('longitude', None),
    ('latitude', -90.1), ('latitude', 90.1), ('longitude', -180.1), ('longitude', 180.1),
    ('latitude', float('inf')), ('longitude', float('-inf')), ('latitude', float('nan')),
    ('latitude', 'invalid'), ('longitude', b'12'),
])
def test_invalid_hotel_rejected(db_path, column, value):
    values = dict(hotel_id='id', latitude=0, longitude=0)
    values[column] = value
    with database.connection(db_path) as db, pytest.raises(sqlite3.IntegrityError):
        db.execute('INSERT INTO saved_hotels (hotel_id, latitude, longitude) VALUES (:hotel_id, :latitude, :longitude)', values)


@pytest.mark.parametrize('stay_date', [None, '', '2026-2-01', '2026-02-30', '2025-02-29',
                                       '2026-13-01', '2026-00-01', '2026-01-00',
                                       '2026-01-32', '2026-10-01T12:00:00', 'abcdefghij'])
def test_invalid_date_rejected(db_path, stay_date):
    with database.connection(db_path) as db:
        insert_hotel(db, 'id')
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)',
                       ('id', stay_date))


@pytest.mark.parametrize('column', ['nightly_rate_cents', 'rooms_available'])
@pytest.mark.parametrize('value', [-1, 1.5, None, 'invalid', b'20'])
def test_invalid_demo_values_rejected(db_path, column, value):
    with database.connection(db_path) as db:
        insert_hotel(db, 'id')
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(f'INSERT INTO demo_hotel_nights (hotel_id, stay_date, {column}) VALUES (?, ?, ?)',
                       ('id', '2026-10-01', value))
