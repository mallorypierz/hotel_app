"""SQLite model schema and atomic, one-time sample-data initialization."""
import csv
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'data'
DATABASE = DATA / 'wayfinder.sqlite3'


@contextmanager
def connection(path=None):
    db = sqlite3.connect(path or DATABASE, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize(path=None):
    with connection(path) as db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('CREATE TABLE IF NOT EXISTS metadata (version INTEGER PRIMARY KEY)')
        if db.execute('SELECT version FROM metadata').fetchone():
            return
        db.execute('CREATE TABLE hotels (hotel_id TEXT PRIMARY KEY, hotel_name TEXT NOT NULL, city TEXT NOT NULL, state TEXT NOT NULL, nightly_rate_usd REAL NOT NULL CHECK(nightly_rate_usd > 0))')
        db.execute('CREATE TABLE trips (trip_id TEXT PRIMARY KEY, hotel_id TEXT NOT NULL REFERENCES hotels, trip_name TEXT NOT NULL, check_in TEXT NOT NULL, check_out TEXT NOT NULL)')
        db.execute('CREATE TABLE users (user_id TEXT PRIMARY KEY, display_name TEXT NOT NULL)')
        db.execute("CREATE TABLE bookings (booking_id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users, trip_id TEXT NOT NULL REFERENCES trips, booked_on TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('confirmed', 'cancelled')))")
        for table in ('hotels', 'trips', 'users', 'bookings'):
            with (DATA / f'{table}.csv').open(encoding='utf-8-sig', newline='') as source:
                rows = csv.DictReader(source)
                for row in rows:
                    placeholders = ','.join('?' for _ in row)
                    db.execute(f'INSERT INTO {table} VALUES ({placeholders})', list(row.values()))
        db.execute('INSERT INTO metadata VALUES (1)')
