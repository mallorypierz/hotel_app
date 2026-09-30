# Project Rules

Work only inside this project. Read the repository and current handoff before editing. Preserve unrelated work, prefer small focused changes, and ask before adding, removing, or upgrading dependencies.

## Boundaries

- Vue screens and interactions belong in `frontend/`.
- FastAPI routes, Pydantic models, and Python data logic belong in `backend/`.
- Sample data belongs in `data/`; do not hardcode records in Vue components.
- Keep durable notes in `docs/`, selected major prompts in `prompts/`, and current state in `handoffs/current.md`.
- Update `README.md` when setup, architecture, or run instructions change.
- Keep hotel booking workflows on sample data. Assignment 2 permits public Geoapify location and hotel-place data for discovery only. Do not add authentication, payments, real booking APIs, or unnecessary database complexity unless requested.

## Earlier Assignment — Preserved Part 1 Checkpoint

- Provide one city input and a Search button.
- Return matching stays from `GET /api/hotels?city=...`.
- Python must read `hotels.csv` and `trips.csv` and join them through `hotel_id`.
- Vue must show results in a plain table with clear column labels.
- Show a clear message when no city matches.

## Earlier Assignment — Approved Part 2 Contract

- Preserve the Part 1 Git checkpoint; the current application searches hotel names and cities.
- Seed SQLite once from all four supplied CSVs, preserving IDs and relationships. All later sample hotel and booking reads and writes use SQLite.
- Vue must provide demo traveler selection and booking create, read/history, cancel/update retaining the record, and delete with confirmation.
- Verify new IDs are unique and additions, cancellations, and deletions survive refresh and service restart without repeat seeding.
- Keep Python models and the database controller separate from the Vue view. Authentication, payment, and bonus pricing are excluded.

## Assignment 2 — Part 1: Live Hotel Search and Map

This scope is separate from the earlier assignment checkpoints above. See `docs/live-hotel-plan.md` for acceptance checks and the current audit. Preserve the existing sample search, SQLite records, demo travelers, and booking behavior.

- Accept five-digit U.S. ZIP strings, preserving leading zeros. Require the requested U.S. postcode before searching Geoapify hotels within 5 km of its returned point; never substitute another location.
- Present actual provider fields in a synchronized Vue list and Leaflet map. Do not invent prices, ratings, availability, or booking confirmations for live places. Document result limits and keep map attribution visible.
- Distinguish loading, results, invalid input, unresolved ZIP, no nearby hotels, and failed requests. Keep controls keyboard accessible.
- Route geocoding and Places requests through FastAPI. Keep the backend key in local, ignored, untracked `.env`; never copy it into frontend configuration. Any client-visible tile credential must be intended for client use and appropriately restricted.
- Complete research and an early mockup before implementation. Maintain verification, demonstration, report, and AI evidence. The persistent shortlist belongs to Assignment 2, Part 2; no shortlist, real booking, payments, authentication, or deployment in Part 1.

### MVC responsibilities

- Model: Python/Pydantic defines validated request and response data; SQLite and the database controller retain the existing sample records. Define external places separately from sample stays that require a nightly price, with provider identifiers and coordinates.
- View: Vue components own forms, feedback, list/map rendering, and shared selection state. Do not embed hotel records or provider request logic in the view.
- Controller: FastAPI routes validate requests and dispatch to Python controller/provider logic for postcode resolution, Places requests, response mapping, and safe errors. Keep provider logic out of Vue and keep routes small.

### Dependency loop

1. **CHECK** the existing environment, installed packages, manifests, and lockfiles; prefer reuse.
2. Explain the exact proposed package/version, installation command, purpose, and affected files, and obtain student approval before adding, removing, or upgrading a dependency.
3. **TAKE ACTION** only after approval, limited to the approved dependency change.
4. **VERIFY** the installed result and relevant checks; record the outcome.

## Development Priorities

Prioritize user experience, visual clarity, responsive layout, simple navigation, small reusable Composition API components, readable Python, clear Pydantic models, and fast interactions. Avoid large files, excessive animation, and overengineering.

## Verification

Run relevant checks before reporting completion. Record exact results and clearly identify anything not tested. Before a Git checkpoint, review the complete diff and manually exercise both a successful city search and a no-results search in the browser.

### AutoLoop

Trigger: **“AutoLoop”**

1. State the acceptance check.
2. Make the smallest in-scope change.
3. Run the relevant check.
4. Inspect failures, apply the smallest correction, and rerun.
5. Stop when checks pass, after five correction cycles, or when dependency, scope, or data-model approval is needed.
6. Report changes, results, and unverified areas.

### SmokeTest

Trigger: **“Run the smoke test”**

Do not change source code.

1. Read `README.md` and `docs/verification.md`.
2. Run backend tests, frontend lint, and frontend build.
3. Start FastAPI and Vue using the documented commands.
4. Search for `Boston`; confirm four joined trip rows appear with the labeled columns.
5. Search for `Aspen`; confirm the no-results message appears.
6. Confirm no browser-console or API errors.
7. Stop services started for the check unless the user asks to keep them running.
8. Report build, test, UI, and unverified status.

When later features exist, extend the smoke test to cover hotel details, room selection, simulated booking, and confirmation.
