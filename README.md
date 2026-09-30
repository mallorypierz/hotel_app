# Wayfinder Hotels

A small educational hotel-search application with a Vue frontend and Python/FastAPI backend. Hotel and booking data use sample CSV seeds; the ZIP demonstration and discovery API request real Geoapify location/place data. It does not make real reservations or process payments.

## Architecture

- `frontend/` — Vue search, stay review, confirmation, and booking history
- `backend/` — FastAPI routes, Pydantic models, SQLite schema, and database controller
- `data/` — four supplied CSV seed files and the local, Git-ignored `wayfinder.sqlite3`
- `docs/` — design and repeatable verification notes
- `prompts/` — selected major project prompts
- `handoffs/current.md` — verified current state and next task

`GET /api/hotels?q=Trail` searches hotel names and cities. The existing `?city=Boston` endpoint remains supported. Vue displays joined stays in a labeled table and offers a simulated booking for a selected demo traveler.

FastAPI initializes SQLite on first startup, importing hotels, trips, users, and bookings in one transaction. Existing IDs and relationships are preserved. A database version marker prevents repeat seeding; later starts retain additions, cancellations, and deletions. After initialization all sample hotel and booking reads and writes use SQLite. New bookings receive UUID-based IDs. Do not delete `data/wayfinder.sqlite3` if you want to retain saved bookings.

The database controller in `backend/app/controller.py` performs CRUD; `database.py` defines relational storage and `models.py` defines API models. Vue is the view; FastAPI dispatches validated requests to the controller. This demo has no authentication and must only be run locally with sample data.

Run the reusable preparation and verification stages in `prompts/start-up-prompts.md` when setting up or resuming the project.

## Setup

From the `hotel_app/` project root, create the backend environment and install its declared packages:

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
```

Install the declared frontend packages:

```sh
cd frontend
npm install
cd ..
```

Ask for approval before installing or changing dependencies.

Backend configuration lives in the project-root `.env`, beside `frontend/` and
`backend/`. Set `GEOAPIFY_API_KEY` there. The helper in `backend/app/config.py`
loads that explicit path at process startup; existing environment variables take
precedence. Restart the backend after editing `.env`, even when using `--reload`.
`GET /api/health` reports the API status and only whether the key is configured;
absent, empty, or whitespace-only values are not configured. This does not
validate the key or call Geoapify.

`GET /api/demo/zip-location` performs a live Geoapify lookup for the fixed ZIP
`16802`. Add `?postcode=02108` to look up an entered five-digit U.S. ZIP; omitting it
defaults to `16802`. This legacy API remains available. The webpage uses one ZIP input in live
discovery, where the returned ZIP, locality, country and coordinates appear
alongside the nearby hotels and map. It returns a small
location response, or a safe error: 503 for missing
configuration, 404 for an unresolved ZIP, and 502 for provider failure.

## Run

Start FastAPI from the project root:

```sh
backend/.venv/bin/uvicorn backend.app.main:app --reload --port 8010
```

On this Mac, the Python installation lacks its default CA bundle. Use the
existing macOS CA bundle when starting the backend so HTTPS verification works:

```sh
SSL_CERT_FILE=/etc/ssl/cert.pem backend/.venv/bin/uvicorn backend.app.main:app --reload --port 8010
```

This keeps certificate verification enabled and installs no dependencies.
Other environments with a working Python trust store can use the first command.

In another terminal, start Vue:

```sh
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173/`. Vite proxies `/api` to port `8010`. Set `VITE_API_PROXY_TARGET` only when using another backend origin.

## Verify

```sh
backend/.venv/bin/python -m pytest backend/tests
cd frontend
npm run lint
npm run build
```

Then search for `Boston` and confirm four joined trip rows appear. Search for `Aspen` and confirm the no-results message appears. See `docs/verification.md` for recorded expected and observed results.

## Booking workflow

Search a hotel name or city, select a fixed-date stay, choose a demo traveler, and confirm the simulated booking. Booking history supports reading records, cancelling while retaining a record, and permanently deleting test bookings after confirmation. Refresh and restart both services to verify that changes persist. Traveler selection is remembered locally; booking records live in SQLite.

API: `GET /api/users`, `GET /api/bookings?user_id=U006`, `POST /api/bookings` with `user_id` and `trip_id`, `PATCH /api/bookings/{id}/cancel`, and `DELETE /api/bookings/{id}`. All CRUD is available through the frontend. Authentication, payments, and surge pricing are outside the required scope.

## Public API assignment

See [historical ZIP verification and submission evidence](docs/zip-lookup.md).
The legacy ZIP endpoint remains available; the current webpage combines ZIP
lookup and live hotel discovery in one form, separate from sample bookings.


## Assignment 2, Part 1 discovery backend

`GET /api/discovery/hotels?postcode=02108` requires exactly five ASCII digits,
preserving leading zeros. Python resolves the exact U.S. postcode-level result,
then requests `accommodation.hotel` places within 5,000 meters of its returned
point. The response includes the center, validated provider IDs/coordinates,
optional names/addresses, and omission/duplicate counts. Missing optional text
is null; no price, rating, availability, or booking claim is generated.

One provider page is requested with `limit=20`. `limit_reached` means the raw
page reached that cap, so more places may exist. Coverage is not exhaustive,
even below the limit. A valid empty page is HTTP 200; missing configuration is
503, unresolved ZIP is 404, invalid input is 422, provider/data failures are
502, and explicit rate/quota limits are 503 with a safe error code. Each provider
request uses a 10-second timeout and no automatic retries.

Use the existing startup commands and backend-only project-root `.env` key
above; no additional dependencies or frontend credentials are needed. The
Vue discovery panel now displays synchronized hotel lists and Leaflet markers;
select a list button or marker with the mouse or keyboard. At narrow widths the
map appears above the list. Sample stays/bookings remain a separate section. ZIP location lookup and
live hotel discovery share one ZIP input; the legacy demonstration endpoint
remains available without a second webpage form. See [backend verification](docs/live-hotel-verification.md)
for controlled tests, error details, and remaining live/browser checks.


Discovery UI uses the installed Leaflet 1.9.4 and keyless OpenStreetMap tiles.
Attribution stays visible; normal browser caching and Referer behavior are
preserved. Search requests go only to the local FastAPI endpoint. Editing a ZIP
clears the previous search; retries respect a returned delay. Tile failures keep
hotel information available. No frontend API credential is required.

Controlled browser checks are saved in `docs/browser-checks/discovery.cjs`.
With the documented servers running, use `node docs/browser-checks/discovery.cjs`
when an existing Playwright runtime and Chrome are available. This Mac's bundled
runtime is the default; elsewhere set `PLAYWRIGHT_RUNTIME` to an existing module
path. No Playwright dependency was added to the app. The separate
`discovery-live.cjs` makes one real Geoapify search and normal tile requests;
run it deliberately, not as part of repeated automated checks.
