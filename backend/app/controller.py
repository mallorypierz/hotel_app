"""Database controller: all application reads and booking mutations use SQLite."""
from datetime import date
from uuid import uuid4

from fastapi import HTTPException

from .database import connection

STAYS = '''SELECT h.hotel_id, h.hotel_name AS name, h.city, h.state,
 h.city || ', ' || h.state AS location, h.nightly_rate_usd AS nightly_price,
 t.trip_id, t.trip_name, t.check_in, t.check_out
 FROM trips t JOIN hotels h ON h.hotel_id=t.hotel_id'''


def search(text, city_only=False):
    with connection() as db:
        clause = 'instr(lower(h.city), lower(?)) > 0'
        args = [text]
        if not city_only:
            clause += ' OR instr(lower(h.hotel_name), lower(?)) > 0'
            args.append(text)
        return [dict(row) for row in db.execute(STAYS + ' WHERE ' + clause + ' ORDER BY t.trip_id', args)]


def users():
    with connection() as db:
        return [dict(row) for row in db.execute('SELECT * FROM users ORDER BY user_id')]


def history(user_id):
    with connection() as db:
        return [dict(row) for row in db.execute('''SELECT b.*, u.display_name,
            h.hotel_name, h.city, h.state, h.nightly_rate_usd,
            t.trip_name, t.check_in, t.check_out
            FROM bookings b JOIN users u USING(user_id)
            JOIN trips t USING(trip_id) JOIN hotels h USING(hotel_id)
            WHERE b.user_id=? ORDER BY b.booked_on DESC, b.booking_id DESC''', (user_id,))]


def create(payload):
    with connection() as db:
        for table, key, value in [('users', 'user_id', payload.user_id), ('trips', 'trip_id', payload.trip_id)]:
            if not db.execute(f'SELECT 1 FROM {table} WHERE {key}=?', (value,)).fetchone():
                raise HTTPException(404, f'Unknown {key}')
        booking = dict(booking_id='B-' + uuid4().hex, user_id=payload.user_id,
                       trip_id=payload.trip_id, booked_on=date.today().isoformat(), status='confirmed')
        db.execute('INSERT INTO bookings VALUES (:booking_id,:user_id,:trip_id,:booked_on,:status)', booking)
        return booking


def cancel(booking_id):
    with connection() as db:
        if not db.execute("UPDATE bookings SET status='cancelled' WHERE booking_id=?", (booking_id,)).rowcount:
            raise HTTPException(404, 'Booking not found')
        return dict(db.execute('SELECT * FROM bookings WHERE booking_id=?', (booking_id,)).fetchone())


def delete(booking_id):
    with connection() as db:
        if not db.execute('DELETE FROM bookings WHERE booking_id=?', (booking_id,)).rowcount:
            raise HTTPException(404, 'Booking not found')
