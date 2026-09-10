# Expedia Replica

A small educational hotel-search application with a Vue frontend and Python/FastAPI backend. It uses sample CSV data only and does not make real reservations or process payments.

## Architecture

- `frontend/` — Vue city-search screen and hotel results table
- `backend/` — FastAPI route, validation, and Python CSV join logic
- `data/` — `hotels.csv` and `trips.csv`, connected through `hotel_id`
- `docs/` — design and repeatable verification notes
- `prompts/` — selected major project prompts
- `handoffs/current.md` — verified current state and next task

`GET /api/hotels?city=Boston` returns matching joined hotel and trip records. Vue displays them in a labeled table and shows a clear message when no city matches.

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

## Current Scope

Part 1 includes city search and joined table results. Hotel details, room selection, booking simulation, and confirmation are not implemented.
