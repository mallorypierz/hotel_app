# Wayfinder Hotels

A small educational hotel-search application with a Vue frontend and Python/FastAPI backend. It uses sample CSV data only and does not make real reservations or process payments.

## Architecture

- `frontend/` — Vue search, stay review, confirmation, and booking history
- `backend/` — FastAPI routes, Pydantic models, SQLite schema, and database controller
- `data/` — four supplied CSV seed files and the local, Git-ignored `wayfinder.sqlite3`
- `docs/` — design and repeatable verification notes
- `prompts/` — selected major project prompts
- `handoffs/current.md` — verified current state and next task

`GET /api/hotels?q=Trail` searches hotel names and cities. The existing `?city=Boston` endpoint remains supported. Vue displays joined stays in a labeled table and offers a simulated booking for a selected demo traveler.

FastAPI initializes SQLite on first startup, importing hotels, trips, users, and bookings in one transaction. Existing IDs and relationships are preserved. A database version marker prevents repeat seeding; later starts retain additions, cancellations, and deletions. After initialization all application reads and writes use SQLite. New bookings receive UUID-based IDs. Do not delete `data/wayfinder.sqlite3` if you want to retain saved bookings.

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

## Run

Start FastAPI from the project root:

```sh
backend/.venv/bin/uvicorn backend.app.main:app --reload --port 8010
```

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
