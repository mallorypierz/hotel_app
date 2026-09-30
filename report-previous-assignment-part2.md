# Wayfinder Hotels — Part 2

## Repository and commit

Repository: [https://github.com/mallorypierz/hotel_app](https://github.com/mallorypierz/hotel_app). Exact reviewed Part 2 application commit on main: [`89df62af6849366f106c85970512f36d1ae79ec5`](https://github.com/mallorypierz/hotel_app/commit/89df62af6849366f106c85970512f36d1ae79ec5). This report is a subsequent documentation-only checkpoint; application code is identical to that commit.

Development branch: `codex/part-two-completion`, merged into main after review and checks. Preserved Part 1 checkpoint: [`c9eaf9117e104d36be5d50fbfc94697c5791399b`](https://github.com/mallorypierz/hotel_app/commit/c9eaf9117e104d36be5d50fbfc94697c5791399b).

## Implementation

Part 1 joined hotel and trip CSVs for city search. Part 2 searches hotel names and cities and adds simulated booking, demo traveler selection, and booking history. Vue presents a labeled results table, selected-stay review, booking confirmation with a unique reference, cancellation retaining the record, and deletion after confirmation. All CRUD operations are performed through frontend controls and FastAPI requests.

SQLite is seeded atomically once from hotels.csv, trips.csv, users.csv, and bookings.csv, retaining every original ID and relationship. A version marker prevents reseeding. All subsequent reads/writes use SQLite; new bookings use UUID-based IDs. Tests verify operation even when CSV files are unavailable after initialization.

Model–View–Controller responsibilities: Python's relational schema and Pydantic models define records and relationships; Vue is the View; a separate Python database controller performs parameterized CRUD; FastAPI validates and dispatches HTTP requests. No dependencies were added. Authentication, payments, and optional surge pricing are excluded.

UI research and decisions are documented in the [design note](https://github.com/mallorypierz/hotel_app/blob/main/docs/design-pipeline.md). Expedia's grouped stay search and Trips navigation informed the workflow. The interface uses a photographic introduction, warm accent, clear labels, visible booking status, keyboard focus, and responsive spacing. Offered dates are fixed by the sample data.

## Verification

Reviewed the complete Git diff and new source files; visually inspected the controller in VS Code. Backend tests: **12 passed**. Frontend lint: **passed**. Production build: **passed**. Full details and repeatable steps: [verification record](https://github.com/mallorypierz/hotel_app/blob/main/docs/verification.md).

| Action | Expected | Observed |
| --- | --- | --- |
| Search Boston | Four joined stays | Four rows with labeled hotel, city, state, price, trip, check-in, and check-out columns |
| Search Trail | Match hotel name | Valley Trail Inn returned |
| Search Aspen | Clear no-results state | “No stays matched” appeared |
| Select Demo Traveler 6, review stay, confirm | New booking in history | Created `B-f1874e7ca4094be89a756563dac4f30c` with confirmed status |
| Cancel new booking | Retain record, update status | Same ID remained with cancelled status |
| Create then delete a second test booking | Unique ID, confirmation, then removal | `B-020dbdb0927e49088dde9cfbf83ced9b` created and removed |
| Refresh and restart frontend/backend | Saved changes persist without repeat seeding | Cancelled addition remained, deleted record stayed absent, and every database row matched the pre-restart snapshot |
| Mobile at 390×844 | Readable controls, contained table scrolling | No page overflow; booking references wrap |
| Inspect console/API logs | No unexpected failures | No console warnings/errors; successful 200/201/204 API responses |

[Search screenshot](https://github.com/mallorypierz/hotel_app/blob/main/docs/part2-search.png) · [No-results screenshot](https://github.com/mallorypierz/hotel_app/blob/main/docs/part2-empty.png) · [Creation screenshot](https://github.com/mallorypierz/hotel_app/blob/main/docs/part2-confirmation.png) · [Restart persistence screenshot](https://github.com/mallorypierz/hotel_app/blob/main/docs/part2-persistence.png) · [Mobile screenshot](https://github.com/mallorypierz/hotel_app/blob/main/docs/part2-mobile.png)

## Demo video

[Watch or download my Part 2 demo video](https://github.com/mallorypierz/hotel_app/blob/main/docs/part2-student-demo.mov). The student-recorded video is approximately 1 minute 31 seconds, below the three-minute limit. If GitHub does not show an inline player, use **View raw** or **Download raw file** to download and play the recording.

## Project context and next steps

- [README and run instructions](https://github.com/mallorypierz/hotel_app/blob/main/README.md)
- [Project rules](https://github.com/mallorypierz/hotel_app/blob/main/AGENTS.md)
- [Design and UI research](https://github.com/mallorypierz/hotel_app/blob/main/docs/design-pipeline.md)
- [Selected Part 2 prompt](https://github.com/mallorypierz/hotel_app/blob/main/prompts/09-part-2-sqlite-bookings.md)
- [Visual redesign prompt](https://github.com/mallorypierz/hotel_app/blob/main/prompts/04-visual-redesign.md)
- [Current handoff](https://github.com/mallorypierz/hotel_app/blob/main/handoffs/current.md)

Next: verify instructor access to the repository and linked video, then upload this report to Part 2 — Submission. The course site submission is not performed by this application.

Limitations: local sample data and simulated reservations only; fixed classroom dates may be past dates. External fonts/hero image require internet. Other browsers, physical phones, and a full assistive-technology audit were not tested. The overview references In-class Activity 2 but its complete worksheet was not supplied, so any additional worksheet-specific deliverables are unverified.
