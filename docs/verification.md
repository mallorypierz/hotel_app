# Part 2 verification

## Commands and results — September 22, 2026

- `backend/.venv/bin/python -m pytest backend/tests`: **12 passed in 0.30s**.
- `npm run lint` in `frontend/`: **passed**, no warnings.
- `npm run build` in `frontend/`: **passed**, 14 modules, 159ms.
- Reviewed tracked diffs and new Python/Vue files. VS Code is not available at its standard installation path; review was performed directly from file contents and Git diff, not represented as a VS Code review.

## Browser verification

Both services used README commands, backend on 8010 and Vue on 5173. Actions used Vue controls, not direct API mutations.

| Action | Expected | Observed |
| --- | --- | --- |
| Search Boston | Four joined trip rows with labeled columns | Passed: four rows across Harbor Lantern Hotel and Maple Square Inn |
| Search Trail | Matching hotel name | Passed: Valley Trail Inn, one offered stay |
| Search Aspen | Clear empty state | Passed: “No stays matched” and explanatory text |
| Choose Demo Traveler 6, review Trail stay, confirm | New unique booking in history | Created `B-f1874e7ca4094be89a756563dac4f30c`, confirmed, with reference message |
| Cancel created booking | Retain record with cancelled status | Passed after confirmation |
| Create another test booking | Another unique ID | Created `B-020dbdb0927e49088dde9cfbf83ced9b` |
| Delete that test booking | Confirmation then disappearance | Passed; DELETE returned 204 |
| Refresh browser | Cancelled addition remains; deleted record absent | Passed |
| Stop and restart both services, reload | Same stored records without repeat seeding | Passed: new cancelled booking remains; deleted ID absent |
| Compare SQLite before/after restart | Every row identical | Passed: 8 hotels, 12 trips, 6 travelers, 8 bookings, one seed marker |
| Mobile, 390×844 | Usable controls and no page overflow | Passed: page width 390; horizontally scrollable results and wrapping booking references |
| Console and API logs | No unexpected failures | No browser warnings/errors; observed API responses 200/201/204 |

Existing demo bookings were preserved. The local database is ignored by Git. A fresh checkout seeds six bookings; the verified local database contains two additional retained test bookings from this and the previous session.

## Automated coverage

Joined city/name search, blank input validation, unique booking IDs, CRUD after reopening connections and repeat initialization, deleted seed records staying deleted, invalid references/missing records, every supplied seed field and ID, foreign-key integrity, and reads/writes with CSVs unavailable after seeding.

## Repeat this check

Run the commands above. Start services using README. Search Boston, Trail, and Aspen. Select Demo Traveler 6, create and cancel a new booking; create and delete a second test booking using confirmation. Record IDs. Refresh, stop both services, restart, and verify retained/absent IDs in history. Confirm starter records are not duplicated. Stop services when finished.

## Evidence and limitations

Screenshots: [search](part2-search.png), [no results](part2-empty.png), [creation](part2-confirmation.png), [after restart](part2-persistence.png), [mobile](part2-mobile.png).

Not tested: other browsers, a physical phone, a full screen-reader audit, or instructor account access to GitHub. External fonts and hero imagery require internet; functional booking data is local. Fixed dates may be in the past because they are supplied classroom data. No authentication, payments, real bookings, or optional surge pricing. Video is reserved for the user. The exact In-class Activity 2 worksheet was not supplied. The Part 1 checkpoint remains `c9eaf9117e104d36be5d50fbfc94697c5791399b`.
