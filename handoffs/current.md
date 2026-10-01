# Current Handoff

## State

Wayfinder Hotels Part 2 is implemented: hotel-name/city search, SQLite seeded once from all four CSVs, demo traveler selection, booking confirmation/history, cancellation retaining the record, and confirmed deletion. Models/storage, controller, FastAPI routes, and Vue views are separate. Existing work was completed on `codex/part-two-completion`; the reviewed feature was merged into main at `89df62af6849366f106c85970512f36d1ae79ec5`.

## Verification

September 22, 2026: 12 backend tests pass; frontend lint and build pass. Browser Boston/Trail/Aspen checks and all four CRUD actions pass. A browser reload and full backend/frontend restart preserve additions, cancellation, and deletion; every database row is unchanged by restart. Mobile 390×844 fits without page overflow. Console has no warnings/errors. See `docs/verification.md` for exact IDs, evidence, limitations, and repeatable steps.

## Checkpoints and runtime

Part 1: `c9eaf9117e104d36be5d50fbfc94697c5791399b`. Repository: https://github.com/mallorypierz/hotel_app. No dependency changes. Local SQLite and generated artifacts remain ignored. Port 8000 belongs to another project; use 8010 and 5173. Vite HMR is disabled; manually refresh after edits. Verification services are stopped when the session finishes.

## Remaining user work

The student supplied a 90.833-second recording, saved as `docs/part2-student-demo.mov` and linked in report.md. Upload the updated report to the course submission page. Earlier local videos are preserved but are not submitted as Part 2 evidence. Verify instructor repository/video access. The full Activity 2 worksheet was not supplied. Authentication and surge pricing are optional and excluded. The app uses fixed classroom stays and makes no real reservations.

## Publication

The user explicitly approved committing and publishing the application, tests, report, documentation, and screenshots to the existing GitHub repository. The final report and review notes form a documentation-only checkpoint after the verified application merge. Earlier unused screenshots and videos remain local and are not submission evidence.

The supplied video is unchanged (49,007,737 bytes). Duration was checked from the MOV metadata; its full visual/audio content was not reviewed in this upload step.


## Public API assignment — September 24, 2026

Completed the ZIP input/table extension. The existing fixed backend route now
accepts an optional validated postcode query, defaulting to 16802. Vue sends the
entered ZIP and renders five labeled columns. Live 16802 and 02108 checks passed;
55 backend tests, frontend lint, and build passed. Health reports key is configured.
This Mac requires SSL_CERT_FILE=/etc/ssl/cert.pem when launching the backend
because Python's default CA bundle is absent; README includes that command.
See docs/zip-lookup.md for results and submission text, plus zip-16802.png and
zip-02108.png for safe screenshots. The student still needs to confirm the
in-class demonstration and upload evidence to Canvas. No commit or push was
performed for this completion; pre-existing uncommitted work was preserved.

## Assignment 2, Part 1 preparation — September 29, 2026

Current scope is **Live Hotel Search and Map**, distinct from the earlier
assignment's Part 1 CSV checkpoint and Part 2 SQLite bookings. Preparation only
is complete; live hotel discovery is not implemented. See
`docs/live-hotel-plan.md` for the audit, acceptance checklist, and sequence,
and `prompts/10-live-hotel-search.md` for the step-by-step prompts.

Existing ZIP geocoding preserves leading zeros, checks the requested U.S.
postcode, validates coordinates, and returns safe errors. The missing work is
Geoapify Places search within 5 km of the returned postcode point, a separate
live-place model, a synchronized Vue list/Leaflet map, complete hotel-search
states, and assignment-specific research/mockup/verification/video/report.
Next: research and an early mockup before implementation; then dependency review
and an API contract. Check the installed environment and obtain student approval
for exact dependency changes before installation, then verify the result.

`AGENTS.md` now permits Geoapify discovery data while retaining sample booking
boundaries, MVC responsibilities, and the existing AutoLoop/SmokeTest rules.
Preserve the SQLite records and sample search/booking behavior. No shortlist,
real booking, payment, authentication, or deployment is in this Part 1 scope.

Current preparation verification: targeted ZIP/configuration tests **43 passed
in 0.43s** using `backend/.venv/bin/python -m pytest
backend/tests/test_config.py backend/tests/test_geocoding.py
backend/tests/test_demo_zip_route.py -q`. `.env` is ignored and untracked; no
credential contents were displayed. Full-suite, frontend lint/build, fresh live
API, and browser checks were not rerun for this documentation-only step.
Application code, dependencies, and data were not changed. All pre-existing
uncommitted work and prior handoff history were preserved; no commit or push.
Services started earlier at the user's request should remain running; this
preparation step does not stop or restart them.

## Assignment 2, Part 1 research — September 29, 2026

Research is complete in `docs/live-hotel-research.md`. Direct browser
inspection covered OpenStreetMap and Google Maps ZIP/location search, selection,
missing-information examples, and no-result feedback; untested interactions are
explicitly identified. Official Geoapify Geocoding/Places, pricing/terms, Leaflet,
and OpenStreetMap tile-policy sources are linked with access dates.

Adopted design direction: exact U.S. postcode validation; hotel-category circle
search at 5,000 meters with a 20-result cap and explicit coverage limits; shared
provider-ID selection; keyless OSM raster tiles for the local demo with required
attribution and usage rules. Geoapify credentials remain backend-only. These are
design decisions, not completed implementation. Next is the early mockup, then
dependency approval and the API contract. No dependencies, application code,
database records, or running services were changed in this research stage.

## Early live hotel mockup — September 29, 2026

Saved original pre-implementation layout and state boards in
`docs/live-hotel-mockup-v1.png` and `docs/live-hotel-states-v1.png`, explained in
`docs/live-hotel-design.md`. These are annotated static sketches with labeled
placeholders and a schematic map, not live API results. Preserve v1 originals;
record later revisions/deviations in the design log. Both images were visually
inspected. No application behavior or dependencies changed. Next: inspect the
installed environment, obtain approval for any exact dependency installation,
and settle the API contract before implementation.

## Dependency audit and API contract — September 29, 2026

The implementation contract is now in `docs/live-hotel-plan.md`: proposed
`GET /api/discovery/hotels?postcode=...`, separate Pydantic external-place models,
exact postcode center, 5,000-meter radius, 20-result cap/metadata, explicit empty
success versus validation/unresolved/provider errors, and MVC file boundaries.
No shortlist, SQLite changes, or application implementation in this step.

Installed frontend packages and npm lockfile checked; Leaflet is absent.
Backend inventory and `pip check` passed; reuse urllib, FastAPI, Pydantic,
python-dotenv, and existing geocoding. Proposed dependency is exactly
`leaflet@1.9.4`, installed from `frontend/` with
`npm install --save-exact leaflet@1.9.4`. Student approval is pending. Do not
install until approved; afterward verify the exact version, lockfile diff,
assets, frontend lint, and build. No manifests, lockfiles, or source code changed
during preparation. Earlier research and v1 mockup remain preserved.

## Approved Leaflet installation — September 29, 2026

Student approved installing exactly `leaflet@1.9.4`. Installation completed via
`npm install --save-exact leaflet@1.9.4` from `frontend/`; initial sandbox DNS
failure was resolved by retrying with authorized network access. Only Leaflet
was added; all pre-existing locked package entries remain unchanged.

Verified exact manifest/lock/installed version and JS/CSS/marker assets.
Frontend lint passed; build passed (17 modules, 235 ms); diff checks passed.
npm reported zero vulnerabilities and a warning about the pre-existing
fsevents install script policy, which was left unchanged. No application source,
backend dependencies, SQLite schema, or data changed. Leaflet is installed but
not yet integrated. Next: implement and test the agreed discovery backend, then
the frontend map/list. The earlier pending-installation note is now superseded.


## Discovery backend AutoLoop — September 29, 2026

Implemented `GET /api/discovery/hotels?postcode=02108` using the agreed separate
Pydantic models and synchronous Python controller. Strict geocoding requires the
exact U.S. postcode-level result with finite numeric coordinates before Places
is called. The existing ZIP demo retains its original lookup/error contract.
Places uses `accommodation.hotel`, a longitude/latitude circle of 5,000 meters,
proximity bias, and one page capped at 20. Results retain provider IDs and
optional text, reject invalid/out-of-radius records, deduplicate valid IDs, and
report omissions/limit metadata. Nonempty all-invalid pages are errors.

Shared urllib transport uses a 10-second timeout per request, sanitized errors,
no retries, and explicit quota/rate handling. No new dependencies or database
changes. `.env` is ignored/untracked; contents and key-bearing URLs were not
displayed. No live calls, browser checks, service restart, commit, or push.

AutoLoop: first full run 121 passed / 3 failed (old sanitized-traceback assertions
saw a literal endpoint in a source line, without credentials). Moved URL
construction off the transport call line; rerun **124 passed in 0.37s**.
`git diff --check` passed. See `docs/live-hotel-verification.md` for exact commands,
controlled outcomes, and limitations. Next: frontend synchronized list/map and
states, followed by live/browser verification and assignment evidence. Existing
sample data and all pre-existing unrelated changes are preserved.


## Discovery Vue interface AutoLoop — September 29, 2026

Implemented small Composition API form/list/map components and a discovery
composable, reusing approved Leaflet 1.9.4. Live discovery precedes clearly
labeled sample stays/bookings. ZIP demo and existing workflows remain intact.
Provider place ID owns selection in both directions; keyboard controls,
narrow layouts, center/radius, metadata/coverage, attribution, and all feedback
states are implemented. Aborts/version checks clear stale data; rate delays and
separate tile warnings are handled. No dependencies or backend code changed.

Final `npm run lint` passed; `npm run build` passed (28 modules, 207 ms).
Backend regression suite: **124 passed in 0.41s**. Controlled Chrome browser
checks passed 16 scenarios, including 390/320 px reflow, keyboard selection,
stale response, empty/error/rate/tile states, Boston four rows and Aspen no
results. Two source corrections: initial Leaflet view and explicit Enter marker
activation. No uncaught page errors in final controlled/live runs.

One live `02108` search at 20:24 Eastern returned HTTP 200, 20 hotels/markers,
limit reached, zero omitted/duplicate records. Six observed OSM tile responses
were HTTP 200 with valid localhost Referer. No direct browser Geoapify API
requests or credential query parameters. `.env` remains ignored and untracked;
its contents were not displayed. Services started for this check were stopped.

Updated README, design change log, and `docs/live-hotel-verification.md`;
repeatable browser scripts/results live in `docs/browser-checks/`. Screenshots
preserve controlled/live provenance. No commit, push, new booking, or dependency
change. Screen-reader/manual assistive-tech testing, new assignment recording,
report, and submission evidence remain; the one live count is an observation,
not a fixed expectation or complete inventory.

## Verification-only extended smoke test — September 29, 2026

Latest result: **NEEDS REPAIR, not a clean smoke pass.** Tests 124 passed in
0.43s; frontend lint/build passed (28 modules, 200 ms). Two live searches,
16802 and 02108, returned the exact U.S. centers and matching API/list/marker
records (20 each at observation time). Controlled mismatch, empty, provider,
quota/rate, loading/stale, keyboard, narrow layout, and tile-failure checks passed.
Boston/Aspen and sample booking create/cancel/delete/refresh/service-restart
checks passed. Temporary test records were cleaned through UI; all database
rows match baseline. All 33 recorded application/test/manifest source hashes
are unchanged. No application source was edited during this pass.

Open defect D1: missing frontend `/favicon.ico` returns 404 and emits a browser
console resource error. No uncaught JS or hotel/booking API failure observed.
See the latest section of `docs/live-hotel-verification.md` for exact actions,
expected/observed results, preserved test-harness failures, screenshots, and a
focused AutoLoop repair prompt. Do not claim a clean smoke pass until the favicon
is repaired and relevant rechecks pass. No services existed on 8010/5173 at start;
only services started for the smoke check were restarted/stopped. No dependencies,
commit, push, or submission. Recording/report remain outstanding.

## D1 favicon correction — September 29, 2026, 20:44 Eastern

D1 is closed after one AutoLoop correction: added a local SVG favicon in
`frontend/public/favicon.svg` and an explicit icon link in `frontend/index.html`.
No dependency or behavior change. Fresh Chrome requested `/favicon.svg` and
received 200 `image/svg+xml`; no `/favicon.ico` fallback request, console
error/warning, or page error. Built HTML/asset verified. Lint passed; build
passed (28 modules, 289 ms). All 16 existing controlled browser regression
scenarios passed, including Boston/Aspen; no live Geoapify calls or booking
mutations. Test-owned services stopped. The original smoke failure is preserved
in `docs/live-hotel-verification.md`, followed by the correction and new evidence.
The earlier “needs repair” status is superseded for D1; no verified smoke defect
remains open. Broader testing/submission limitations are unchanged. No commit/push.

## Part 1 submission preparation — September 29, 2026

Prepared `report.md`, `docs/live-hotel-demo-script.md`, AI disclosure/evidence log,
actual prompt excerpts, and a proposed exact checkpoint manifest/review note.
Previous report preserved byte-for-byte at root as
`report-previous-assignment-part2.md`, preserving its link base. Student confirmed
“gpt 6 astra medium”; disclosure attributes the setting to that confirmation.

Reviewed tracked diff/new feature artifacts; manually operated Boston (four
joined rows/labels) and Aspen (no results) via CUA in-app browser. No returned
browser errors/warnings. Archive hash matches prior HEAD report; 141 local link
targets initially checked with no missing targets. New docs linked by the final
verification note are also present. No source/dependency/database changes.

Assessed commit remains PENDING. Current `main` HEAD is still prior-assignment
`eb256a3ac5cc08be4029e6e3354099c3ce903163`. No staging/commit/push. Proposed manifest
contains 96 files; excludes six unrelated old local media artifacts and all
ignored secrets/runtime/database files. Test-owned services stopped after review.

Remaining: student reviews and authorizes checkpoint/publication; records and
supplies a NEW live-feature demo URL/date/duration/assessed version; confirms any
additional AI tools; verifies instructor access to repository/commit/every
artifact/video; replaces pending report fields and repository-relative links
with tested immutable URLs for standalone Canvas; uploads `report.md` and checks
receipt. No video or instructor access was fabricated; no Canvas submission.


## Single ZIP lookup refinement — September 29, 2026, 20:59 EDT

Student requested only one ZIP field, within live discovery. Removed the separate
ZIP panel mounting/import from App.vue and clarified discovery introduction.
Legacy ZIP API/component source preserved; README/report describe shared input.
Lint and build passed; browser confirmed one ZIP field, no old lookup button,
and invalid `2108` feedback; warning/error log empty. No new provider calls.
Services started for this edit remain running on 8010/5173; updated app left open.
No dependency/backend changes or checkpoint. Repeat required diff review and
manual Boston/Aspen gate before any future commit; assessed SHA remains pending.


## Authorized checkpoint gate — 2026-09-29 21:09 EDT

Final review and browser Boston/Aspen checks passed after the one-ZIP refinement.
Backend 124 passed in 0.40s; lint/build passed (26 modules, 194 ms). Selected
96 files; secrets/runtime data and six unrelated legacy media excluded. Existing
services remain running. Student authorized commit/push; actual SHA will be
recorded after checkpoint. Demo/access/Canvas remain pending.


## Published Part 1 checkpoint — September 29, 2026

Student-authorized checkpoint [e6687356b620798414cb249cf5bde918d461aead](https://github.com/mallorypierz/hotel_app/commit/e6687356b620798414cb249cf5bde918d461aead) contains the reviewed 96 files.
`git push origin main` succeeded (`eb256a3..e668735`). A documentation-only
follow-up records this real assessed code SHA in report.md. Earlier pending/no-push
statements are historical and superseded by this entry. Six unrelated legacy
media files remain untracked; secrets/database/runtime artifacts remain excluded.
No new live calls or booking changes. Services were left running. Demo recording,
instructor access, remaining report fields and Canvas submission are still pending.


## Final recording and public access — September 29, 2026

Student supplied a 126.33-second silent MOV. Preserved source; native full-resolution
H.264 sharing copy in ignored .capture/private-submission/live-hotel-student-demo.mp4
(126.15 seconds). Student explicitly chose to keep it private; do not publish
the video or raw metadata. Deliver privately via Canvas or restricted link. Sampled
frames show 06109/16801 results and selected list/map states; other script steps
and absence of interception are not established. Public repository metadata and
114 artifact/report URL checks plus ten external research-source checks passed.
See docs/live-hotel-final-access.md and JSON records. Browser Boston/Aspen gate
repeated successfully; no console warnings/errors. Application source unchanged.
Report will use immutable artifact URLs after this evidence checkpoint. Student
reported no additional AI. Instructor-specific network/device access and rubric
compliance cannot be guaranteed; Canvas upload remains the student's final action.


## Public video authorization — September 29, 2026

The student explicitly changed the earlier privacy preference: “it can be public
now.” The 25,559,356-byte H.264 sharing copy is selected for publication as
`docs/live-hotel-student-demo.mp4`; source MOV remains untouched. Previous private
instructions above are historical and superseded for this recording copy.
Report will prominently link the published video using an immutable URL.
Before this checkpoint, reviewed the full pending diff and manually repeated
Boston (four labeled rows) and Aspen (“No stays matched”); browser warning/error
log empty. Application source unchanged; no new live requests or booking changes.

## Remaining media checkpoint — October 1, 2026

User requested committing all remaining changes and pushing to GitHub. The only
pending artifacts were four older Part 2 screenshots and two older demo videos;
application source was already committed. Reviewed all four screenshots and
sampled both silent videos at two-second intervals: observed sample hotel search
and booking UI, with no credentials or .env contents visible in reviewed frames.
This is a sampled review, not a frame-by-frame audit. These older artifacts do
not replace the assessed live-discovery recording.

Before checkpoint, manually searched Boston (four joined rows with labeled
columns) and Aspen ("No stays matched") in the running browser; warning/error
log was empty. git diff --check passed. No source or dependency changes; full
backend tests, lint, and build were not repeated for this media-only checkpoint.
.env, local SQLite, installers, and private review artifacts remain ignored and
untracked. Backend and frontend remain running on 8010 and 5173 as requested.

## Assignment 2 Part 2 schema — October 1, 2026

On `assignment2_part2_in_class`, added repeatable transactional creation of
`saved_hotels` and `demo_hotel_nights` before the existing seed-marker check.
Applied to local `data/wayfinder.sqlite3`; both tables are empty. API `place_id`
maps to the exact case-sensitive `hotel_id` key; optional name/address remain
nullable, coordinates are required and bounded. Nightly rows use a hotel/date
composite primary key, foreign key, valid ISO date, and nonnegative integer demo
defaults (10000 cents, 20 rooms). No save controls or endpoints added.

159 backend tests passed in 0.46s. Original schemas and every supplied/current
record match the pre-edit snapshot after repeated initialization; integrity and
foreign-key checks pass. No frontend, frozen discovery API, or dependencies
changed. See `docs/assignment2-part2-schema.md` for mapping and verification.
Stopped for requested student database inspection; no commit/push. Browser/live
API and frontend build/lint were not repeated for this schema-only step.

## Assignment 2 Part 2 local operations — October 1, 2026

Extended the schema checkpoint with `saved_hotel_locations` and local GET/POST/
DELETE endpoints. Saves preserve exact provider IDs and ZIP center context;
insert-only demo nights cover October 10–14, 2026. Transactional deletion removes
only the selected hotel, its associations, and its nights. Vue now searches local
storage first, falls back to the frozen discovery endpoint only on successful
empty local reads, and provides Add/Remove controls plus labeled simulated nights.

166 backend tests, frontend lint/build, isolated-database browser workflow, and
16 adapted Part 1 browser regressions passed. Assignment 1 table schemas/records
remain unchanged; the real local saved tables are empty. See
`docs/assignment2-part2-local-hotels.md` for exact outcomes and manual steps.
Project service ownership checked; original listeners exited before restart.
Fresh services now run on 8010/5173. Temporary test server is stopped. No unrelated
processes, dependencies, frozen discovery API logic, or sample records changed.
No commit/push; stop for student manual browser/database verification.

## Authorized Part 2 checkpoint — October 1, 2026

Student requested preserving and pushing all changes. Reviewed the complete
pending source, tests, and documentation; repeated manual Boston (four labeled
joined rows) and Aspen (No stays matched) checks in the browser. Browser warning/
error log empty; git diff --check passed. Prior 166-test, lint/build, isolated
mutation-browser and Part 1 regression results remain applicable; no source edits
since those checks. The current browser shows a saved hotel with edited demo
values; local database records are preserved and remain Git-ignored, as do .env
and private runtime artifacts. Publishing the Part 2 feature branch supersedes
the historical no-commit/no-push status above. No merge to main requested.
