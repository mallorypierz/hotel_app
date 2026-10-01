"""Additive schema changes, run inside the initialization transaction."""


def add_demo_hotel_tables(db):
    """Create empty Part 2 tables without changing Part 1 or sample records.

    Discovery response mapping: place_id -> hotel_id; name, address, latitude,
    and longitude keep their names. IDs use exact, case-sensitive TEXT keys.
    Rates and inventory are fictional defaults, never provider facts.
    """
    db.execute('''CREATE TABLE IF NOT EXISTS saved_hotels (
        hotel_id TEXT NOT NULL PRIMARY KEY COLLATE BINARY,
        name TEXT,
        address TEXT,
        latitude REAL NOT NULL CHECK (
            typeof(latitude) IN ('real', 'integer') AND latitude BETWEEN -90 AND 90
        ),
        longitude REAL NOT NULL CHECK (
            typeof(longitude) IN ('real', 'integer') AND longitude BETWEEN -180 AND 180
        )
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS demo_hotel_nights (
        hotel_id TEXT NOT NULL REFERENCES saved_hotels(hotel_id),
        stay_date TEXT NOT NULL CHECK (
            length(stay_date) = 10
            AND stay_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
            AND date(stay_date, '+0 days') IS NOT NULL
            AND date(stay_date, '+0 days') = stay_date
        ),
        nightly_rate_cents INTEGER NOT NULL DEFAULT 10000 CHECK (
            typeof(nightly_rate_cents) = 'integer' AND nightly_rate_cents >= 0
        ),
        rooms_available INTEGER NOT NULL DEFAULT 20 CHECK (
            typeof(rooms_available) = 'integer' AND rooms_available >= 0
        ),
        PRIMARY KEY (hotel_id, stay_date)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS saved_hotel_locations (
        hotel_id TEXT NOT NULL REFERENCES saved_hotels(hotel_id),
        postcode TEXT NOT NULL CHECK (
            length(postcode) = 5 AND postcode NOT GLOB '*[^0-9]*'
        ),
        country_code TEXT NOT NULL CHECK (country_code = 'us'),
        locality TEXT,
        latitude REAL NOT NULL CHECK (
            typeof(latitude) IN ('real', 'integer') AND latitude BETWEEN -90 AND 90
        ),
        longitude REAL NOT NULL CHECK (
            typeof(longitude) IN ('real', 'integer') AND longitude BETWEEN -180 AND 180
        ),
        PRIMARY KEY (hotel_id, postcode)
    )''')
    db.execute('CREATE INDEX IF NOT EXISTS saved_hotel_locations_postcode ON saved_hotel_locations(postcode)')
