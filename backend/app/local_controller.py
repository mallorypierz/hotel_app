"""Transactional local hotel storage; never calls the discovery provider."""
from .database import connection

DEMO_DATES = tuple(f'2026-10-{day:02d}' for day in range(10, 15))


def _hotel(db, row):
    hotel = dict(row)
    hotel['place_id'] = hotel.pop('hotel_id')
    hotel['nights'] = [dict(night) for night in db.execute(
        'SELECT stay_date, nightly_rate_cents, rooms_available FROM demo_hotel_nights '
        'WHERE hotel_id=? ORDER BY stay_date', (hotel['place_id'],))]
    return hotel


def save(payload):
    hotel, center = payload.hotel, payload.center
    with connection() as db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('''INSERT INTO saved_hotels VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(hotel_id) DO NOTHING''',
                   (hotel.place_id, hotel.name, hotel.address, hotel.latitude, hotel.longitude))
        db.execute('''INSERT INTO saved_hotel_locations VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(hotel_id, postcode) DO NOTHING''',
                   (hotel.place_id, center.postcode, center.country_code, center.locality,
                    center.latitude, center.longitude))
        db.executemany('''INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)
            ON CONFLICT(hotel_id, stay_date) DO NOTHING''',
                       [(hotel.place_id, day) for day in DEMO_DATES])
        return _hotel(db, db.execute('SELECT * FROM saved_hotels WHERE hotel_id=?',
                                    (hotel.place_id,)).fetchone())


def search(postcode):
    with connection() as db:
        db.execute('BEGIN')  # A consistent snapshot of hotels, nights, and saved IDs.
        rows = db.execute('''SELECT h.* FROM saved_hotels h
            JOIN saved_hotel_locations l USING(hotel_id)
            WHERE l.postcode=? ORDER BY h.hotel_id''', (postcode,)).fetchall()
        center = db.execute('''SELECT postcode, country_code, locality, latitude, longitude
            FROM saved_hotel_locations WHERE postcode=? ORDER BY hotel_id LIMIT 1''',
                            (postcode,)).fetchone()
        return dict(postcode=postcode, center=dict(center) if center else None,
                    hotels=[_hotel(db, row) for row in rows], count=len(rows),
                    saved_ids=[row[0] for row in db.execute('SELECT hotel_id FROM saved_hotels ORDER BY hotel_id')])


def remove(hotel_id):
    with connection() as db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('DELETE FROM demo_hotel_nights WHERE hotel_id=?', (hotel_id,))
        db.execute('DELETE FROM saved_hotel_locations WHERE hotel_id=?', (hotel_id,))
        db.execute('DELETE FROM saved_hotels WHERE hotel_id=?', (hotel_id,))
