import pytest
from fastapi import HTTPException
from backend.app import database, controller
from backend.app.models import BookingCreate


@pytest.fixture
def db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, 'DATABASE', tmp_path / 'travel.sqlite3')
    database.initialize()


def test_search_hotel_name_and_city(db):
    assert len(controller.search('Inn')) == 4
    assert controller.search('Trail')[0]['name'] == 'Valley Trail Inn'
    assert len(controller.search('boston')) == 4
    assert controller.search('Aspen') == []


def test_crud_survives_reopen_and_reinitialization(db):
    initial = controller.history('U006')
    assert initial == []
    a = controller.create(BookingCreate(user_id='U006', trip_id='T008'))
    b = controller.create(BookingCreate(user_id='U006', trip_id='T008'))
    assert a['booking_id'] != b['booking_id']
    database.initialize()
    assert len(controller.history('U006')) == 2
    controller.cancel(a['booking_id'])
    database.initialize()
    records = {row['booking_id']: row for row in controller.history('U006')}
    assert records[a['booking_id']]['status'] == 'cancelled'
    controller.delete(b['booking_id'])
    database.initialize()
    assert [row['booking_id'] for row in controller.history('U006')] == [a['booking_id']]


def test_deleted_seed_does_not_return(db):
    controller.delete('B001')
    database.initialize()
    assert 'B001' not in [row['booking_id'] for row in controller.history('U001')]
    with database.connection() as conn:
        assert conn.execute('SELECT count(*) FROM hotels').fetchone()[0] == 8
        assert conn.execute('SELECT count(*) FROM bookings').fetchone()[0] == 5


def test_invalid_references_and_missing_records(db):
    with pytest.raises(HTTPException) as error:
        controller.create(BookingCreate(user_id='missing', trip_id='T008'))
    assert error.value.status_code == 404
    with pytest.raises(HTTPException):
        controller.cancel('missing')
    with pytest.raises(HTTPException):
        controller.delete('missing')


def test_seed_preserves_all_records_and_relationships(db):
    import csv

    with database.connection() as conn:
        for table in ('hotels', 'trips', 'users', 'bookings'):
            with (database.DATA / f'{table}.csv').open(encoding='utf-8-sig', newline='') as source:
                expected = list(csv.DictReader(source))
            actual = [dict(row) for row in conn.execute(f'SELECT * FROM {table}')]
            assert len(actual) == len(expected)
            key = next(iter(expected[0]))
            assert {row[key] for row in actual} == {row[key] for row in expected}
            for record in expected:
                saved = next(row for row in actual if row[key] == record[key])
                for column, value in record.items():
                    assert saved[column] == (float(value) if column == 'nightly_rate_usd' else value)
        assert conn.execute('PRAGMA foreign_key_check').fetchall() == []


def test_initialized_application_no_longer_reads_csv(db, monkeypatch, tmp_path):
    monkeypatch.setattr(database, 'DATA', tmp_path / 'absent-seed-files')
    database.initialize()
    assert len(controller.users()) == 6
    assert len(controller.search('Boston')) == 4
    booking = controller.create(BookingCreate(user_id='U006', trip_id='T008'))
    assert controller.history('U006')[0]['booking_id'] == booking['booking_id']
