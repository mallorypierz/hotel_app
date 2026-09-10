# Verification

Run checks from the project root unless a step says otherwise. Do not add or change dependencies without approval.

## Structure

- Confirm `frontend/`, `backend/`, `docs/`, `prompts/`, and `handoffs/` exist.
- Confirm `docs/design-pipeline.md`, `docs/verification.md`, and `handoffs/current.md` exist.
- Confirm prompt records use a two-digit sequence such as `prompts/01-setup.md`.
- Confirm Vue files stay in `frontend/` and Python/FastAPI files stay in `backend/`.

## Backend

From the project root:

1. Install only the dependencies declared in `backend/requirements.txt` inside a virtual environment.
2. Run `backend/.venv/bin/python -m pytest backend/tests`.
3. Start FastAPI with `backend/.venv/bin/uvicorn backend.app.main:app --reload --port 8010`.
4. Confirm `/api/hotels?city=Boston` returns four joined stays, `/api/hotels?city=Aspen` returns no stays, and a blank city returns HTTP 422.

## Frontend

From `frontend/`:

1. Install only the dependencies declared in `frontend/package.json`.
2. Run `npm run lint` from `frontend/`.
3. Run `npm run build` from `frontend/`.
4. Start the development server and confirm the page loads without console errors.

## Feature Smoke Check

For the implemented hotel-search slice:

1. Start the backend and frontend development servers.
2. Search for `Boston`; confirm four joined trip rows appear with Hotel, City, State, Nightly rate, Trip, Check in, and Check out columns.
3. Search for `Aspen`; confirm the empty-results message appears.
4. Confirm there are no browser-console or API errors.

Expected and observed result for the latest Part 1 check:

| Search | Expected | Observed |
| --- | --- | --- |
| Boston | Four joined trip rows | Four rows across Harbor Lantern Hotel and Maple Square Inn |
| Aspen | A clear no-results message because Aspen is absent from the CSV data | “No results match that city. Check the spelling or try another city.” |

Hotel details, room selection, simulated booking, and booking confirmation are not implemented yet. Verify them only after those features exist.

Record any skipped or unavailable check in `handoffs/current.md`.
