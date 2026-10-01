# Assignment 2 Part 2: local-first hotel discovery

Implemented on `assignment2_part2_in_class`, based on checkpoint `cc6d3da`.
Database: `/Users/mallorypierz/Documents/hotel_app/data/wayfinder.sqlite3`.
This extends the schema-only checkpoint documented in assignment2-part2-schema.md.

## Storage and behavior

`local_models.py` defines validated save/local-response contracts independently
of frozen discovery models. `local_controller.py` performs database operations;
`local_routes.py` registers GET, POST, and DELETE `/api/local-hotels` with safe
503 errors on storage failure. Provider IDs retain their exact text, including
case and whitespace. Names and addresses may remain NULL.

The additive migration creates `saved_hotel_locations`, keyed by hotel ID and
five-digit ZIP, with stored country, locality, and ZIP-center coordinates. Each
hotel may be associated with multiple ZIPs. Repeated saves leave existing hotel
metadata, associations, and nightly values intact. A ZIP search uses its first
stored center ordered by provider ID if saves contain differing centers for the
same ZIP. It does not geocode again for local matches.

Saves atomically add the hotel, association, and five nights (October 10–14,
2026 inclusive), relying on database defaults of 10000 cents and 20 rooms.
Targeted conflict handling adds missing rows without replacing any existing
rates or availability. Removal atomically deletes all nights and all ZIP
associations for that exact hotel, then the hotel itself. No Assignment 1 tables
are involved. Other hotels remain intact.

The Vue composable first requests saved matches and global saved IDs. A successful
empty local result permits the frozen Part 1 API call. Failure blocks fallback.
The list retains separate selection buttons and adds sibling save/remove controls,
so there are no nested buttons. Local results include stored nightly rows with
explicit simulated-classroom labeling. Removing a local result rebuilds markers;
removing the last result prompts a new search rather than silently calling the
provider. A timeout reports that the operation could not be confirmed and suggests
retrying or searching again, since a server commit may precede a lost response.

## Automated verification — October 1, 2026

- `backend/.venv/bin/python -m pytest backend/tests -q`: **166 passed in 0.51s**.
  All mutation tests use pytest temporary databases. New ASGI route tests cover
  exact IDs, repeated saves, five defaults, existing rate/inventory preservation,
  multiple ZIP associations, reopen/reinitialization persistence, global saved
  status, deletion isolation, input validation, and transactional rollback on
  injected save/delete failures. Original discovery/ZIP tests pass unchanged.
- `cd frontend && npm run lint && npm run build`: passed with no lint warnings;
  production build transformed 26 modules (151 ms).
- `LOCAL_TEST_BACKEND=http://127.0.0.1:8011 node
  docs/browser-checks/local-hotels.cjs`: passed using a separate temporary-database
  backend and controlled API results/tiles. Verified local failure blocks provider,
  pending/failed/successful saves, refresh persistence, global saved status across
  ZIPs, dated demo values, list/map keyboard selection, failed/successful removal,
  refresh after removal, empty-local fallback, 390px layout, Boston/Aspen, and no
  uncaught page errors. The test backend is no longer running.
- Existing 16 Part 1 controlled browser scenarios passed through an adapter with
  an empty local response and selectors scoped to selection buttons. Original
  evidence files were preserved; adapter/output are ignored under `.capture/`.
  Includes 320/390px reflow, stale searches, rate limiting, empty/unresolved/error
  results, attribution, keyboard behavior, tile failure, and Boston/Aspen.
- Compared all Assignment 1 table SQL and records with the pre-schema snapshot:
  unchanged. Local integrity check `ok`; no foreign-key violations. Local saved
  tables remain empty: no controlled fixture hotels entered the real database.
- Initial test attempts exposed unavailable TestClient dependency and router
  introspection compatibility; reused existing dependency-free ASGI testing and
  direct route registration. Browser harness corrections scoped an ambiguous
  locator and used the actual `localhost` Vite binding. No dependencies added.

## Restart and manual verification

Verified original listener commands and working directories belonged to this
project (backend 41648/42595, Vite 41666). They had already exited when restart
was attempted; confirmed no listeners on 8010, 5173, or temporary 8011. Started
fresh backend and frontend using the documented commands. No unrelated process
was stopped. Running URLs: frontend http://localhost:5173/; backend
http://127.0.0.1:8010/ (API docs at /docs).

Student verification remains:

1. Search `02108` with empty local storage; confirm **API results** and Add buttons.
2. Add a hotel; confirm saved status and Remove become available only on success.
3. Inspect `saved_hotels`, `saved_hotel_locations`, and five `demo_hotel_nights`
   rows in DB Browser (refresh/reopen its database view as needed).
4. Refresh the page and search the same ZIP; confirm **Saved locally**, the stored
   center, dates October 10–14, and simulated $100.00/20-room values.
5. Remove the hotel; verify all three related sets of rows disappear together.
6. Search again; confirm API fallback and Add availability.

No live Geoapify calls were needed for these controlled checks. Student browser
and DB Browser inspection remain pending. No commit or push was performed.
