# Assignment 2 Part 2: storage schema

Database: `/Users/mallorypierz/Documents/hotel_app/data/wayfinder.sqlite3`.
The instructor's `backend/db/expedia.sqlite3` is not this project's database path.

## Mapping from the existing discovery response

| `hotels[]` response field | `saved_hotels` column | Rule |
| --- | --- | --- |
| `place_id` | `hotel_id` | Required TEXT primary key, exact case-sensitive identity; no trimming, case conversion, or generated replacement in storage |
| `name` | `name` | Nullable TEXT; missing names remain NULL |
| `address` | `address` | Nullable TEXT; missing addresses remain NULL |
| `latitude` | `latitude` | Required numeric value from -90 through 90 |
| `longitude` | `longitude` | Required numeric value from -180 through 180 |

This is the mapping for future persistence, not a new save endpoint. The existing
discovery response and its validation are unchanged. No hotels or nightly rows
are inserted by the migration.

`demo_hotel_nights` references `saved_hotels.hotel_id` and uses the composite
primary key `(hotel_id, stay_date)`. Dates must be valid calendar dates in
`YYYY-MM-DD` form. `nightly_rate_cents` defaults to 10000 ($100.00), and
`rooms_available` defaults to 20. Both are required nonnegative integers.
These are fictional classroom defaults, never provider rates or availability.
Each hotel may have only one row for each date. Referenced hotels cannot be
deleted while their nightly rows exist; no cascading deletion is configured.

## Migration and inspection

`database.initialize()` calls the additive migration in the same transaction as
initialization, before checking the existing seed marker. `CREATE TABLE IF NOT
EXISTS` makes repeat calls harmless. Existing sample table schemas, rows, and
seed metadata are left untouched. Fresh databases still import the same four CSVs.
Every application connection enables `PRAGMA foreign_keys = ON`; external SQL
clients must also enable that per-connection setting to enforce foreign keys.

In DB Browser, reopen the database to refresh Database Structure. Inspect the two
new tables and their constraints. Both should be empty at this checkpoint.

## Verification — October 1, 2026

- `backend/.venv/bin/python -m pytest backend/tests -q`: **159 passed in 0.46s**.
- New tests cover fresh and pre-migration databases, repeated initialization,
  preserved edited/deleted seed records, exact provider IDs, nullable metadata,
  defaults, zero values, persisted nightly rows, duplicate keys, invalid numeric
  values/coordinates/dates, and foreign-key rejection including parent deletion.
- Applied initialization twice to the local database. Compared all original
  table SQL and every row against a pre-edit snapshot: unchanged (8 hotels,
  12 trips, 6 users, 6 bookings, 1 metadata row).
- Both new tables contain zero rows. Application connection reports foreign-key
  enforcement enabled, `foreign_key_check` returns no violations, and
  `integrity_check` returns `ok`.
- No frontend, API response, provider logic, dependencies, or sample records
  changed. The backend regression suite includes discovery and ZIP tests.
  Browser/live API checks and frontend lint/build were not repeated for this
  schema-only change. Student DB Browser inspection remains pending.
- No commit or push performed for this change.
