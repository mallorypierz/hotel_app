# Design and UI research

## Responsibilities

Vue is the View: search, fixed-date stay selection, demo traveler selection, confirmation, and booking history. FastAPI validates requests through Pydantic models and delegates to the database controller. Python's controller performs parameterized SQLite search and CRUD. The model layer consists of the relational schema in database.py and typed API models in models.py.

## Persistence

Hotels have many trips; users and trips have many bookings. SQLite foreign keys enforce these relationships. Startup seeds all four CSV files atomically only when the database has no version marker. IDs from the starter files are preserved. New bookings use UUID IDs. Cancellation changes status; deletion removes a record. Subsequent startup reads the marker and preserves stored changes. The local database is ignored by Git.

## UI research direction

Research checked on September 22, 2026: [Expedia Hotels](https://www.expedia.com/Hotels) groups destination, dates, travelers, and Search, and exposes a Trips navigation link. Wayfinder adapts that task order into hotel/city search, fixed-date stay review, demo traveler selection, and booking history. The existing photographic introduction, warm accent, and generous spacing are retained as local design choices. Booking.com's page did not expose usable content during this check, so no new observation is claimed for it.

The supplied overview refers to In-class Activity 2 but does not include its complete instructions. This note records the research actually available and the resulting decisions; compliance with any additional activity-specific worksheet is unverified.

Part 2 adds labeled traveler selection, review before confirmation, reference IDs, visible status badges, and confirmation before cancel/delete. Dates come from fixed offered stays, so the app does not offer a free-date calendar. The table retains clear hotel and trip columns and scrolls horizontally on phones. Keyboard focus, disabled pending actions, explicit empty/error states, and cancellation retaining history support usability. At 390 pixels, the page fits the viewport and booking references wrap.
