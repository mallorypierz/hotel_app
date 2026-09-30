# Assignment 2, Part 1 — backend verification

Date: September 29, 2026 (America/New_York). Scope: discovery backend only.
Research, v1 mockups, and the agreed contract preceded this implementation; see
[live-hotel-plan.md](live-hotel-plan.md). The frontend list/map remains pending.

## Acceptance check and implementation

Accept a five-digit string; resolve only the requested U.S. postcode-level
location; search hotels within 5,000 meters of that returned point; return
validated provider fields and honest metadata; never turn failures into empty
success. Preserve sample search/bookings and the existing ZIP demonstration.

- `backend/app/discovery_models.py`: separate validated center, external hotel,
  and response models, with strict finite bounded coordinates and unique IDs.
- `backend/app/discovery.py`: controller for exact resolution, Places query,
  optional text mapping, spherical distance validation, omissions, and deduplication.
- `backend/app/geocoding.py`: existing parsing reused via strict discovery mode.
  The old demo default and error contract remain intact. Discovery requires
  `result_type=postcode`, the exact postcode, and `country_code=us`.
- `backend/app/provider.py`: shared urllib/JSON transport and safe exceptions.
- `backend/app/main.py`: small synchronous route, validation and error mapping.
- `backend/tests/test_discovery.py`: 69 isolated cases using controlled provider
  responses through the actual FastAPI ASGI route (plus controller traceback check).

## Commands and exact results

Run from the project root with the existing environment; no packages installed:

| Command | Observed result |
| --- | --- |
| `backend/.venv/bin/python -m pip check` | Exit 0, `No broken requirements found.` Existing user-cache permission warning; cache disabled. |
| `git check-ignore .env` | Exit 0, `.env` — ignored. |
| `git ls-files -- .env '.env.*'` | Exit 0, no entries — untracked in current index. |
| `backend/.venv/bin/python -m pytest backend/tests -q` (first run) | 121 passed, 3 failed in 0.46s. |
| Same full-suite command after correction | **124 passed in 0.37s**, exit 0. |
| `git diff --check` | Passed, exit 0. |

AutoLoop used one correction cycle. The three existing geocoding tests required
sanitized tracebacks to contain no URL. Shared transport initially left a
literal provider endpoint visible in the calling source line. URL construction
was moved to a separate line; tests were unchanged and then passed. Neither
real credentials nor key-bearing URLs were displayed. Synthetic test secrets
are used only in controlled failure fixtures.

## Expected versus observed

All observations below are controlled automated results, not live provider data.
The principal test ZIP is `02108`; existing demonstration tests also cover
`16802` and unresolved `00000`.

| Expected behavior | Observed |
| --- | --- |
| Keep `02108` as a string through routing, geocoding query, and returned center | Passed; exact outgoing query and serialized response asserted. |
| Reject missing, wrong-length, whitespace/newline, alphabetic, and non-ASCII digits before requests | Passed; 422 and forbidden-call mocks. |
| Require matching postcode, U.S. country, and postcode result type | Passed; mismatches/unresolved produce 404 and no Places call; later exact candidate uses its own returned coordinates. |
| Malformed geocoding or matching invalid coordinates fail safely | Passed; 502, no Places call, including booleans, strings, null, nonfinite and out-of-bounds values. |
| Geocoding request uses postcode type, U.S. filter, JSON, limit 5 | Passed via parsed-query assertion. |
| Places request uses hotel category, longitude then latitude, circle 5000, proximity bias, limit 20 | Passed via parsed-query assertion; altered center fixture verifies coordinates are not hardcoded. |
| Populated response retains genuine fixture provider fields | Passed, full expected response asserted. |
| Missing/blank/nontext optional fields are null; available address lines can be joined | Passed; no invented name, address, or price. |
| Valid empty feature array succeeds with center and zero counts | Passed, HTTP 200. |
| Missing/malformed features, invalid JSON, oversized page, or all unusable records fail | Passed, HTTP 502 rather than successful empty list. |
| Bad IDs/coordinates and out-of-radius points are omitted from partially usable pages | Passed; omitted count matches; a page containing only a bad record fails. |
| Keep first valid ID occurrence, preserve order, count duplicates separately | Passed. |
| Raw page of 20 sets limit flag before omission/deduplication | Passed: 18 usable, 1 omitted, 1 duplicate, limit reached true. |
| Both requests use timeout 10, no automatic retry | Passed; opener timeout and request counts asserted. |
| Missing configuration produces 503 without network | Passed. |
| Timeout, network, generic 403 credentials rejection, and 500 fail safely in either stage | Passed; 502, provider_error, no unsafe body or console output. |
| HTTP 429 and explicit quota-exceeded 403 in either stage are distinct | Passed; 503, provider_limited, valid Retry-After forwarded. |
| Unsafe retry header is not forwarded | Passed; injected/non-numeric value omitted. |
| Existing sample search and bookings stay intact | Existing tests passed: Boston four joined rows, Aspen empty, CRUD, unique IDs, reinitialization persistence, seed relationships. Tests use temporary databases. |
| Existing ZIP demo/configuration behavior stays intact | All existing tests passed, including leading zeros, default ZIP, safe errors and configuration. |

## Limits and interpretation

The controller requests one page capped at 20, with no pagination. `count` is
the unique usable returned count, not an inventory total. `limit_reached` means
the raw page contained 20 records; more may exist, but this does not prove it.
Geoapify coverage/category membership can omit hotels even below the cap.
The circle is centered on the resolved postcode point, not the entire ZIP area.
No prices, ratings, availability, real reservations, or sample booking IDs are
attached to discovery records.

Coordinates come from Geoapify `properties.lat`/`properties.lon`; absent or
invalid coordinates are omitted, never replaced with center coordinates.
Available `formatted` address is preferred, otherwise available `address_line1`
and `address_line2` are joined. Distance uses a spherical Haversine calculation
with mean Earth radius 6,371,008.8 m. Strictly greater than 5,000 m is omitted.
This can differ slightly from a provider's distance calculation at the boundary.

Each outbound request has a 10-second urllib socket timeout; this is not a hard
end-to-end deadline for the entire two-request flow. No automatic retries.
HTTP 429 is limited regardless of body. Non-200 responses with explicit
quota/rate phrases in the JSON `message` also map to provider_limited;
unrecognized provider error formats remain safe generic failures. A generic
403 is never automatically called quota exhaustion. Retry-After forwarding is
restricted to 1–6 ASCII digits (delay seconds); dates or other formats are
omitted. Raw provider error bodies and URLs are never included in API errors.

No live Geoapify calls, quota exhaustion, browser checks, frontend lint/build,
map rendering, real provider field/coverage verification, or service restart
were performed in this backend-only step. Controlled responses cannot establish
live account access or current hotel counts. `.env` checks cover ignore rules
and the current Git index, not a historical secret scan; contents were not read
or displayed. Existing local SQLite records were not modified. No dependencies,
frontend files, manifests, or lockfiles were changed by this implementation.

Startup commands are unchanged; the README now explains the new endpoint and
its metadata/errors. Keep the key in backend-loaded project-root `.env`. On
this Mac retain the documented `SSL_CERT_FILE=/etc/ssl/cert.pem` launch command.
No services were started/stopped deliberately and no commit/push was made.
Frontend integration and subsequent live/browser demonstration remain separate
verification gates; this is not completion of the whole assignment.

## Vue interface verification — September 29, 2026

This later section supersedes the earlier backend-only frontend/live limitations
for the checks explicitly listed here. No backend code or dependencies changed.

### Commands and observations

| Check | Result |
| --- | --- |
| `cd frontend && npm run lint` | Passed, exit 0. |
| `cd frontend && npm run build` | Passed, exit 0; 28 modules, 207 ms; JS 235.53 kB / gzip 76.63 kB. |
| `backend/.venv/bin/python -m pytest backend/tests -q` | 124 passed in 0.41s. |
| `node docs/browser-checks/discovery.cjs` | Passed, 16 controlled browser scenarios; 7 mocked discovery requests in final run. |
| `node docs/browser-checks/discovery-live.cjs` | One live 02108 search succeeded at 2026-09-30 00:24:35 UTC (September 29, 20:24 Eastern). |
| `git diff --check` | Passed. |
| `.env` ignore/index checks | Ignored and untracked; no contents displayed. |
| `rg -l 'GEOAPIFY_API_KEY\|apiKey=' frontend/src frontend/dist` | No matching files (rg exit 1 means no matches). Browser network also checked below. |

The scripts use the already available external Playwright runtime and installed
Chrome; neither became a project dependency. Default runtime path is Mac-specific;
`PLAYWRIGHT_RUNTIME` can point to another already installed module. Start the
README's backend/Vite services before running scripts. Initial sandbox binding
and browser launch attempts failed; authorized local execution resolved those
environment restrictions. Services started for these checks were stopped.

### Controlled browser results

[Machine-readable results](browser-checks/discovery-results.json) and
[repeatable script](browser-checks/discovery.cjs). Hotel fixtures and tiles are
intercepted only by the external test; they are not shipped in Vue components.
Repeated checks made no Geoapify calls and did not repeatedly fetch OSM tiles.

- Initial state makes no discovery request. Invalid ZIP shows field-associated
  feedback without a request; `02108` survives submission and returned display.
- List Space activation selects/highlights its marker. Marker Enter and Space
  select the matching list item by provider ID, reveal it, and retain keyboard
  focus on the activated marker. Selected marker/list states match.
- Selecting places and restoring the search area make no discovery request.
- 390×844 and 320×844 layouts have no document horizontal overflow. Map appears
  above list; selected row is revealed within a one-CSS-pixel rounding tolerance.
  OpenStreetMap attribution remains visible at both widths.
- Names/addresses omitted by controlled responses receive honest labels.
  Counts/omissions and Geoapify attribution render without invented offers.
- New search clears old markers during loading. Editing ZIP while a delayed
  request is pending clears results and rejects the late response.
- True empty results retain ZIP center/circle and have zero hotel markers.
  Unresolved ZIP removes the previous map and presents unresolved feedback.
- Network failure presents request-failure feedback and Retry. A controlled
  quota response disables Search and Retry until its two-second delay expires.
- Tile-load failure shows a separate warning, retaining the successful list and
  both markers. Reloading before this scenario avoids decoded image reuse.
- Real local sample routes still produce four Boston rows and Aspen's no-result
  message. Demo traveler/history reads succeeded; no booking mutation was made.
- No uncaught page errors in the final run. Expected failed-network console
  messages during intentionally aborted requests are not application crashes.

### One live integration check

[Live results](browser-checks/discovery-live-results.json) and
[script](browser-checks/discovery-live.cjs). No interception in this run; normal
browser tile caching and Referer behavior were retained.

`02108` → HTTP 200, **20 hotels and 20 markers**, `limit_reached=true`, zero
omissions and duplicates. The live first record lacked a name; the honest
missing-name label was shown. This is a dated observation, not a guaranteed
count or exhaustive inventory. Six observed tile responses returned HTTP 200;
all carried a localhost Referer. Linked Leaflet/OSM attribution stays inside
the map. The app uses the researched keyless HTTPS OSM endpoint, `keepBuffer: 0`,
normal cache behavior, and no bulk/offline downloads, automatic area scans,
location permission, or map-driven hotel requests. Changing tile providers
requires reviewing URL/attribution and policy together in `DiscoveryMap.vue`.

Browser network observation: **zero requests to api.geoapify.com**, **zero
credential query parameters**, and no uncaught page errors. Only local FastAPI
receives the discovery ZIP; the backend key stays in its local `.env`.

### AutoLoop corrections and visual evidence

Two application correction cycles were needed: initialize Leaflet's view before
accessing marker DOM elements, then explicitly handle Enter for custom markers.
Test harness refinements scoped duplicate list/marker accessible names, waited
for Vue's asynchronous DOM/scroll updates, allowed normal subpixel rounding,
and isolated tile-failure loading from cached decoded images. Original failure
logs are not claims about final behavior; final checks passed.

Browser screenshots: [desktop controlled](live-hotel-ui-controlled-desktop.png),
[390px controlled](live-hotel-ui-controlled-mobile.png),
[tile error controlled](live-hotel-ui-tile-failure.png), and
[live ZIP 02108](live-hotel-ui-live-02108.png). Desktop, narrow, and live screenshots
were opened and visually inspected. Original v1 mockup files were preserved;
[design log](live-hotel-design.md) describes the implementation refinements.

### Remaining limitations

No screen reader or physical mobile-device testing, multi-browser compatibility
matrix, automated contrast audit, or repeated live ZIP coverage survey. Quota,
no-results, network failure, stale-response, and tile-failure states were
controlled, not provoked against real provider services. The live check covered
one ZIP and does not verify every provider field/location. Dense markers can
overlap at the full-radius zoom; keyboard/list selection and zoom remain
available without adding clustering dependencies. A persistent tile warning
reports any failed tile in the current search; a new search resets it.

Booking create/cancel/delete were not repeated in the browser in this turn;
existing backend persistence tests passed and booking source was unchanged.
The UI and backend are implemented, but a new assignment demonstration video,
final report and instructor-access/submission verification remain outstanding.
No commit or push was performed.

## Extended smoke test — September 29, 2026, 20:33–20:38 Eastern

**Overall: NEEDS REPAIR — not a clean smoke-test pass.** Functional checks passed,
but the frontend requests a missing `/favicon.ico`, producing a reproducible
HTTP 404 and browser-console error. No application source was changed or defect
fixed in this verification-only pass. The repair and relevant rechecks remain
outstanding. This section is the latest smoke-test result and supersedes any
implication of a clean console in earlier observations.

### Setup, commands, and preservation

Read `README.md`, `docs/verification.md`, and the current handoff before testing.
No listeners were found on ports 8010/5173, so no already-running service was
stopped. Started FastAPI with
`SSL_CERT_FILE=/etc/ssl/cert.pem backend/.venv/bin/uvicorn backend.app.main:app --port 8010`
and Vite with `npm run dev -- --host 127.0.0.1` from `frontend/`. Health was HTTP
200. Both test-owned services were restarted for persistence verification and
stopped at the end. The reload flag was unnecessary because source stayed fixed.

| Command / check | Observed | Result |
| --- | --- | --- |
| `backend/.venv/bin/python -m pytest backend/tests` | 124 collected, **124 passed in 0.43s** | PASS |
| `npm run lint` in `frontend/` | Exit 0, no lint diagnostics | PASS |
| `npm run build` in `frontend/` | Exit 0; 28 modules, 200 ms; JS 235.53 kB / gzip 76.63 kB | PASS |
| `git diff --check` | Exit 0 | PASS |
| SHA-256 comparison of application source, existing tests, manifests and Vite config | All 33 recorded files unchanged | PASS |
| SQLite logical-row comparison after test cleanup | Every table matches starting hash; 8 hotels, 12 trips, 6 users, 6 bookings, 1 metadata row | PASS |
| `.env` ignore/index checks | Ignored, untracked; contents not displayed | PASS |
| Frontend source/build credential-marker scan | Zero `GEOAPIFY_API_KEY` / `apiKey=` matches | PASS within stated scope |

No dependencies installed or changed. Only verification scripts, JSON evidence,
screenshots and documentation were added in this pass; source and existing tests
were preserved. [Integrity evidence](browser-checks/smoke-integrity-results.json)
and [starting hashes](browser-checks/smoke-baseline.json).

### Live provider observations — two searches only

Both searches were submitted through the Vue text input using Enter, with the
real FastAPI route and real provider responses. Result counts were compared to
the actual response, not a fixed expected inventory. No additional live hotel
search was used for error testing, diagnosis, or rechecks.

| Input / time | Expected | Observed | Result / screenshot |
| --- | --- | --- | --- |
| `16802`, September 29 at 20:33:24 Eastern (`2026-09-30T00:33:24.678Z`) | Requested U.S. ZIP center; returned records correspond to list and map | HTTP 200; postcode `16802`, country `us`, locality State College; center 40.803167822, -77.861384958; 20 API records, 20 rows, 20 markers; limit reached; 0 omitted/duplicates | PASS — [live map/list](smoke-live-16802.png) |
| `02108`, September 29 at 20:33:26 Eastern (`2026-09-30T00:33:26.368Z`) | Leading zero retained in input, request and returned U.S. center | HTTP 200; input/center `02108`, country `us`, Boston; center 42.357581412, -71.065946589; 20 API records, 20 rows, 20 markers; limit reached; 0 omitted/duplicates | PASS — [live map/list](smoke-live-02108.png) |
| Compare every returned record's name/address and numbered marker label | Match API order and honest missing-field labels; unique provider IDs | Every row and marker label matched; unique IDs/counts agreed | PASS |
| Click first list row; focus final marker and press Enter, for both ZIPs | Matching pressed/highlighted state in both views; marker selection retains focus; no additional hotel request | List/marker correspondence and focus assertions passed; request count unchanged | PASS |
| Resize live Boston results to 390×844 and 320×844 | No page overflow; map above list; attribution visible | Both widths passed; attribution stayed visible | PASS — [320px](smoke-live-320.png) |
| Inspect live attribution and network | Linked OSM/Geoapify credits; normal OSM Referer; no direct browser Geoapify API calls or credential parameters | Credits visible; observed live OSM responses carried localhost Referer and returned 200; zero direct API/credential-parameter requests | PASS |
| Inspect console/API during live flow | No unexpected console or API errors | No uncaught JS errors or hotel/booking API failures, but one resource console error; targeted check reproduced frontend `/favicon.ico` 404 | **FAIL — D1 below** |

The live center/radius and coverage explanation were present. At the cap, the UI
said additional places may exist. Twenty is an observation for these two calls,
not an expected future count or exhaustive coverage claim. Screenshots capture
actual hotel information and tiles; the selected item is visible with its map
state. Live map imagery was still loading in parts of the 16802 capture; tile
responses observed by the check returned 200. No tile failure was observed in
the live API checks.

### Simulated checks — no live provider faults induced

`PYTHONPATH=. backend/.venv/bin/python docs/browser-checks/smoke-provider.py`
generated seven responses through the actual ASGI discovery route with controlled
urllib geocoding/Places responses in a separate process. It asserted upstream
call counts. Browser interception then delivered those route outputs to the
unmodified Vue interface. Thus mismatch handling was tested in Python, and its
resulting feedback was tested in the browser; the running backend was not
patched. [Provider evidence](browser-checks/smoke-provider-results.json).

| Input / action | Expected | Observed | Result / screenshot |
| --- | --- | --- | --- |
| Enter `2108` and submit | Invalid-input feedback, no discovery request | Field marked invalid; five-digit guidance; request count unchanged; direct real FastAPI validation also returned 422 | PASS — [invalid](smoke-simulated-invalid.png) |
| Request `02108`, geocoder supplies postcode `02109` | Unresolved; never search substitute postcode | Actual route returned 404; Places calls 0; Vue unresolved message and no map | PASS — [postcode mismatch](smoke-simulated-mismatched_postcode.png) |
| Request `02108`, geocoder supplies country `ca` | Unresolved; never search non-U.S. location | Actual route returned 404; Places calls 0; Vue unresolved message and no map | PASS — [country mismatch](smoke-simulated-non_us.png) |
| Geocoder supplies no result | Unresolved ZIP state | HTTP 404; no Places call; unresolved feedback | PASS — [unresolved](smoke-simulated-unresolved.png) |
| Exact ZIP resolved; Places returns empty feature array | Successful empty state with ZIP center/radius | HTTP 200; zero hotel markers, one ZIP center, honest no-returned-hotels message | PASS — [empty](smoke-simulated-empty.png) |
| Places returns HTTP 500 | Safe failed-request state, never empty success | Actual route 502; Vue Retry/error feedback, no map | PASS — [provider failure](smoke-simulated-provider_failure.png) |
| Places returns HTTP 429 with two-second retry delay | Limited state and disabled retry/search until delay | Actual route 503 `provider_limited`; buttons disabled, enabled after delay | PASS — [rate limit](smoke-simulated-rate_limit.png) |
| Places returns explicit quota-exceeded HTTP 403 | Distinguish quota from generic provider failure | Actual route 503 `provider_limited`; same safe limited UI and delay | PASS — [quota](smoke-simulated-quota.png) |
| Start delayed response after populated results | Loading shown, repeat submit disabled, old markers gone | Loading feedback and disabled button; zero old markers | PASS — [loading](smoke-simulated-loading.png) |
| Edit ZIP while delayed response is pending | Abort/invalidate old result | Late response did not restore old results; initial prompt remained for edited ZIP | PASS |
| Two same-name hotels with different IDs; Tab to Search; Enter submit; list Space; marker pointer/Space | Selection uses ID, not name; both directions and keyboard work | Only intended row/marker selected; narrow-screen row revealed without moving marker focus | PASS — [selection at 390px](smoke-simulated-selection-mobile.png) |
| Abort tile requests while returning one usable hotel with missing text | Separate tile warning; keep hotel data and marker | Warning displayed; one row/marker retained; “Name not provided” / “Address not provided” | PASS — [tile failure](smoke-simulated-tile-failure.png) |

Simulated non-2xx responses and aborted tiles intentionally produce browser
resource errors; those expected messages are separate from the unexpected
favicon error. No uncaught JavaScript error occurred. No quota was exhausted.

### Existing sample workflow — real local SQLite/API

All create/cancel/delete actions used Vue controls and confirmation steps.
The starting database already contained two U006 bookings; those records were
preserved, rather than assuming an empty traveler history.

| Input / action | Expected | Observed | Result / screenshot |
| --- | --- | --- | --- |
| Search Boston | Four joined trip rows with labeled columns | Four rows; Hotel, City, State, Nightly rate, Trip, Check in, Check out, Book a stay | PASS — [Boston](smoke-sample-boston.png) |
| Search Aspen | No-results message | “No stays matched” | PASS — [Aspen](smoke-sample-aspen.png) |
| Choose Demo Traveler 6; search Trail; Select stay | Review offered sample stay | Valley Trail Inn review, fixed dates and sample price | PASS |
| Confirm simulated booking | Unique record and explicit simulated confirmation | HTTP 201; created `B-ef99cb5fd11f4378bb2f9bb373c92df5`; confirmed history row | PASS — [creation](smoke-booking-created.png) |
| Cancel with confirmation | Record retained as cancelled | PATCH 200; cancelled record remained | PASS |
| Create second; Delete; Keep booking; Delete and confirm | Unique second ID; no deletion before confirmation | Created `B-1e8b12bb60bd4584a720ef2293c0f1c5`; Keep retained it; confirmed DELETE 204 removed it | PASS |
| Browser reload | Cancelled first retained; deleted second absent; selected traveler retained | All assertions passed | PASS — [refresh](smoke-booking-refreshed.png) |
| Restart both test-owned services and reopen U006 | No reseeding or lost changes | Cancelled first retained, deleted second absent | PASS — [restart](smoke-booking-restarted.png) |
| Delete only this pass's remaining test record through confirmation; reload | Original data restored | Both new IDs absent; original two U006 rows remain; all SQLite tables hash-identical to baseline | PASS — [cleanup](smoke-booking-cleanup.png) |

No real reservations or payments occurred. A browser request cancellation was
recorded around a successful DELETE/reload; the endpoint returned 204 and the
deletion survived refresh/restart. No booking API HTTP failure occurred.

### Evidence, test-harness corrections, and remaining defect

Primary script/evidence: [extended browser script](browser-checks/smoke-extended.cjs),
[initial results](browser-checks/smoke-extended-results.json),
[booking follow-up](browser-checks/smoke-bookings-results.json),
[restart observation](browser-checks/smoke-restart-results.json), and
[cleanup/tile/favicon follow-up](browser-checks/smoke-followup-results.json).
Initial failures were retained, not overwritten or relabeled as passing:

1. The first booking locator used exact text-label lookup and timed out. The
   accessible snapshot showed a combobox named “Demo traveler”; using role/name
   located it and the workflow passed without source changes.
2. A follow-up test wrongly expected an empty U006 after cleanup. Existing U006
   records were present in the starting database. Correct verification compares
   only created IDs and the full database baseline; both passed. No existing
   record was deleted to satisfy that mistaken expectation.
3. The initial aggregate console check failed. A fresh browser capture identified
   `/favicon.ico` and a direct check confirmed HTTP 404. This is a real outstanding
   asset defect, not a fixture/test assumption.

**D1 — Missing favicon (low severity, open):** loading the app causes a browser
request for `/favicon.ico`, which returns 404 and emits an error in the console.
It does not block hotel or booking behavior, but fails the requested clean-console
smoke criterion. No repair was made because this pass forbids source changes.

Focused repair prompt:

> AutoLoop: Fix the verified Assignment 2, Part 1 defects just reported. State the acceptance checks, make the smallest in-scope corrections, rerun the failing checks and affected regressions, and update the verification record. Stop after five correction cycles or when dependency, scope, or data-model approval is required. Preserve an honest record of the failed approach and correction for the AI evidence log.
>
> Focus on D1: supply a local favicon and reference it from the frontend document so a fresh browser load makes no missing-favicon request or console 404. Add no dependency. Verify the actual icon URL returns 200 with an appropriate image type, inspect fresh-load console/network, rerun frontend lint/build and affected smoke checks using controlled hotel responses. Preserve this failed smoke record and append the correction/recheck results; avoid unnecessary live provider calls.

### Limitations and final status

Chrome on this Mac only; responsive emulation at 390/320 CSS pixels, not a
physical phone or screen-reader audit. Hotel positions were validated by backend
model/radius tests and list/marker identity/text/order by browser checks; no
independent geodetic survey of actual hotel addresses was performed. Every
marker was counted/labeled against the response, while selected first/last
items and controlled same-name records exercised interaction; not every live
marker was individually clicked. Dense markers can overlap at full-radius zoom.

Credential checks covered static frontend credential markers, visible console
output and browser URL parameters/direct Geoapify requests. No secret contents
were printed; this is not a Git-history, browser-memory, or exhaustive security
audit. Public fonts/hero imagery remain external resources. Existing ZIP-demo
behavior was covered by backend tests, not a further live demonstration request.
No new assignment recording, report/submission, commit, or push was performed.

**Do not mark the smoke test complete until D1 is corrected and its relevant
console/network and frontend rechecks pass.** All recorded source checksums and
all original database rows remain unchanged at the end of this pass.

## D1 AutoLoop repair and recheck — September 29, 2026, 20:44 Eastern

**D1 CLOSED.** The previously blocked smoke criterion now passes. The earlier
failed run, diagnosis, and test-harness corrections above remain unchanged as
AI evidence. This is an asset-only correction and affected recheck, not a claim
that all previous live/booking tests were rerun in this turn.

### Acceptance and smallest correction

Acceptance: an explicitly referenced local favicon must return HTTP 200 with an
image content type; a fresh browser must not produce the missing-favicon console
error; frontend lint/build and affected controlled smoke checks must pass.

Added `frontend/public/favicon.svg`, a small native SVG Wayfinder “W”, and one
`rel="icon"` link in `frontend/index.html`. The original document omitted an icon
reference, causing the browser's `/favicon.ico` fallback request and 404. The
corrected document explicitly requests `/favicon.svg`. No dependency, route,
Vue interaction, backend, credential configuration, or data-model change.
The unreferenced legacy `/favicon.ico` URL was not added; the actual browser
request and linked asset, not that unused fallback, are the acceptance target.

One correction cycle; no further application changes were needed.

| Input / action | Expected | Observed | Result |
| --- | --- | --- | --- |
| `npm run lint` in `frontend/` | Clean lint | Exit 0, no diagnostics | PASS |
| `npm run build` in `frontend/` | Successful build containing the referenced icon | Exit 0; 28 modules, 289 ms; HTML 0.54 kB; JS/CSS outputs unchanged | PASS |
| Inspect built HTML and copied asset | Correct icon reference and identical SVG bytes in dist | Build link present; `dist/favicon.svg` equals public asset | PASS |
| Fresh Chrome context at `http://127.0.0.1:5173/` | Browser loads the local SVG without a fallback error | Requested `/favicon.svg`; response **200, image/svg+xml**; no `/favicon.ico` request | PASS |
| GET actual linked icon | Correct response status/type and SVG content | **200, image/svg+xml**, SVG body | PASS |
| Fresh-load console/network | No favicon or other unexpected console/JS error | Zero console errors/warnings, zero page errors, zero direct browser Geoapify API requests | PASS |
| Existing controlled browser suite | Preserve affected discovery/sample behavior | All **16 scenarios passed**; 7 intercepted discovery requests, zero live Geoapify calls | PASS |
| `git diff --check` | No whitespace errors | Exit 0 | PASS |

Commands: `node docs/browser-checks/d1-favicon.cjs` and
`node docs/browser-checks/d1-regression.cjs`. The regression wrapper reuses the
existing suite but saves new screenshot/JSON paths to preserve earlier evidence.
Its passing checks cover initial/invalid input, leading-zero submission,
list Space and marker Enter/Space selection, focus/row reveal, no API calls on
selection, 390/320 px reflow, loading/old-marker clearing, stale responses,
empty center retention, unresolved/network/rate-limit feedback, tile failure,
Boston four rows, and Aspen no results. Simulated error responses deliberately
produce resource errors; they are separate from the clean fresh-load check.

Evidence: [fresh-load result](browser-checks/d1-favicon-results.json),
[controlled regression result](browser-checks/d1-regression-results.json),
[fresh-load screenshot](d1-fresh-load.png),
[controlled desktop](d1-controlled-controlled-desktop.png),
[controlled mobile](d1-controlled-controlled-mobile.png), and
[controlled tile failure](d1-controlled-tile-failure.png).
Fresh-load observation time: `2026-09-30T00:44:28.187Z`, September 29 at 20:44
Eastern. Controlled screenshots are not live provider observations.

No live provider calls, package installations, or booking mutations were made.
Backend tests and booking persistence were not rerun for this HTML/SVG-only
change; their latest passing results remain in the preceding smoke record.
Only test-owned services were started (8010 with the documented SSL certificate
setting, and 5173); both were stopped afterward. Existing unrelated working-tree
changes were preserved. No commit/push or assignment submission was performed.
The earlier screen-reader/physical-device/browser-coverage and submission
limitations still apply. No verified defect from this smoke pass remains open.

## Submission preparation review — September 29, 2026, about 20:48 Eastern

Reviewed the complete tracked diff and proposed untracked additions, preserving
unrelated legacy media; see [checkpoint plan and exact manifest](live-hotel-checkpoint.md).
No code, dependency, database, commit or push change was made in this preparation.
The previous report was copied byte-for-byte at the same project-root level;
[preparation checks](submission-preparation-checks.json) record its hash and
successful local link-target validation.

The agent manually operated the sample search in the available Codex in-app
browser and inspected the resulting table/state: Boston → four joined rows with
labeled columns; Aspen → “No stays matched” with explanatory guidance. Returned
browser error/warning log was empty. Evidence:
[Boston](submission-review-boston.png), [Aspen](submission-review-aspen.png).
No booking mutation was made. This was a focused preparation gate, not a new
full-suite or two-ZIP smoke run; earlier dated live and simulated results remain
as recorded. If code changes before checkpoint, repeat the required gate.

Current report, demonstration script and AI disclosure are prepared; student
confirmed model setting GPT-6 Astra, medium reasoning. Assessed commit, new
recording/link, instructor artifact access, publication and Canvas upload are
explicitly pending. Repository remote was read; attempted public web retrieval
returned a cache miss, not proof of public/private visibility. Existing report
and video were preserved and not reused as new-feature recording evidence.


## Single ZIP form refinement — September 29, 2026, 20:59 EDT

Focused follow-up to the student's request for one ZIP lookup in live discovery.

| Input/action | Expected | Observed | Result |
| --- | --- | --- | --- |
| Fresh in-app browser load | One ZIP field in discovery; no separate lookup panel | ZIP textbox count 1; old “Look up ZIP” button count 0; sample city search still visible | PASS |
| Enter `2108`, select Search hotels | Five-digit validation feedback | “Enter a five-digit U.S. ZIP code, including any leading zero.” | PASS |
| Inspect browser warning/error log | No warnings/errors | Returned log empty | PASS |
| `npm run lint --prefix frontend` | Exit 0 | Exit 0 | PASS |
| `npm run build --prefix frontend` | Exit 0 | Exit 0; 26 modules; 194 ms | PASS |

This pass used invalid input only, with no new live provider calls or simulated
provider responses. Earlier dated live and controlled observations remain above;
backend tests, successful discovery, map selection and full booking regression
were not rerun for this panel-removal-only change. No new screenshots captured.
The page was reloaded to its initial state and left open with local services on
8010 and 5173. The earlier checkpoint gate predates this UI change: repeat complete
diff review and manual Boston/Aspen checks before any checkpoint. No commit/push.


## Authorized Part 1 checkpoint gate — 2026-09-29 21:09 EDT

Student explicitly requested final review, Boston/Aspen rechecks, commit and push.
Reviewed tracked changes and selected new application/test artifacts against the
96-path checkpoint manifest and earlier evidence review. No blocking defect
found. The exact local credential was scanned without printing it: no match in
selected files; `.env` ignored and untracked. Previous report archive still
matches pre-checkpoint HEAD byte-for-byte; all selected Markdown local links
resolve. Six unrelated legacy media files remain excluded. Remote main matched
local pre-checkpoint HEAD; no history rewrite is needed.

| Check/action | Expected | Observed | Result |
| --- | --- | --- | --- |
| Backend pytest suite | All tests pass | 124 passed in 0.40s | PASS |
| Frontend lint | Exit 0 | Exit 0 | PASS |
| Frontend build | Exit 0 | 26 modules, 194 ms; exit 0 | PASS |
| Browser: type Boston in sample search and press Enter | Four labeled joined trip rows | Harbor Lantern Hotel and Maple Square Inn, four trip rows; hotel/city/state/rate/trip/check-in/check-out/booking labels | PASS |
| Browser: replace with Aspen and press Enter | No-result feedback | “No stays matched” | PASS |
| Browser warning/error log | Empty | Empty returned list | PASS |

Reused healthy existing services on 8010/5173 and left them running. No booking
mutation or new live provider search in this gate; existing user discovery
results were preserved. No new screenshots taken; prior screenshots remain
historical evidence. Full live/controlled discovery smoke was not repeated.
The first local credential-scan command used system Python without dotenv and
stopped with ModuleNotFoundError; rerunning with the documented backend virtual
environment passed. No dependency installation or source repair was needed.

This gate authorizes the requested checkpoint operation, not a completed Canvas
submission. Record the real assessed SHA after commit in a documentation follow-up.
