# Project Rules

Work only inside this project. Read the repository and current handoff before editing. Preserve unrelated work, prefer small focused changes, and ask before adding, removing, or upgrading dependencies.

## Boundaries

- Vue screens and interactions belong in `frontend/`.
- FastAPI routes, Pydantic models, and Python data logic belong in `backend/`.
- Sample data belongs in `data/`; do not hardcode records in Vue components.
- Keep durable notes in `docs/`, selected major prompts in `prompts/`, and current state in `handoffs/current.md`.
- Update `README.md` when setup, architecture, or run instructions change.
- Use sample data only. Do not add authentication, payments, real booking APIs, or unnecessary database complexity unless requested.

## Preserved Part 1 Checkpoint

- Provide one city input and a Search button.
- Return matching stays from `GET /api/hotels?city=...`.
- Python must read `hotels.csv` and `trips.csv` and join them through `hotel_id`.
- Vue must show results in a plain table with clear column labels.
- Show a clear message when no city matches.

## Approved Part 2 Contract

- Preserve the Part 1 Git checkpoint; the current application searches hotel names and cities.
- Seed SQLite once from all four supplied CSVs, preserving IDs and relationships. All later application reads and writes use SQLite.
- Vue must provide demo traveler selection and booking create, read/history, cancel/update retaining the record, and delete with confirmation.
- Verify new IDs are unique and additions, cancellations, and deletions survive refresh and service restart without repeat seeding.
- Keep Python models and the database controller separate from the Vue view. Authentication, payment, and bonus pricing are excluded.

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
