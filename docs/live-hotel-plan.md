# Assignment 2, Part 1 — Live Hotel Search and Map

Prepared September 29, 2026 from the student-supplied assignment brief and repository inspection. Part 1 is due September 29, 2026 at 11:59 PM Eastern. This is a preparation plan, not a claim of completed live hotel discovery.

## Scope and preservation

Extend the existing Vue/FastAPI application with Geoapify hotel discovery around a U.S. ZIP and a synchronized Leaflet map. The search center is the provider's returned postcode point, not the traveler's position or every address in the ZIP area.

The earlier Part 1 CSV checkpoint and Part 2 SQLite booking implementation belong to the preceding assignment. Preserve those checkpoints, current SQLite records, hotel-name/city search, demo traveler selection, and simulated booking create/history/cancel/delete behavior. Live places must remain separate from sample bookable stays. No shortlist, new database complexity, real booking, payment, authentication, or deployment in this part.

Before editing, the audit read `AGENTS.md`, `README.md`, `handoffs/current.md`, the complete tracked Git diff, ZIP/configuration implementation and tests, Vue ZIP panel, API models/routes, frontend manifest, and previous ZIP evidence. Existing uncommitted changes include configuration/geocoding code and tests, `.gitignore`, README, requirements, Vue integration, the handoff, screenshots/videos, and the sequential prompt file. Preserve them; do not reset, stage, or publish them as a side effect of this plan.

## What already exists

| Area | Repository evidence | Status and limitation |
| --- | --- | --- |
| ZIP entry | `frontend/src/components/ZipLookupPanel.vue` | Text input, five ASCII digits, leading-zero example, loading and safe error feedback; currently displays a postcode table only. |
| Validated route | `backend/app/main.py` | `/api/demo/zip-location?postcode=...` accepts five-digit strings, defaults to `16802`, returns 422 for invalid input, 404 unresolved, 503 missing configuration, and 502 provider failure. |
| Exact U.S. resolution | `backend/app/geocoding.py` | Requests postcode geocoding filtered to the U.S.; accepts only matching postcode and `country_code=us`, with finite bounded coordinates. Uses a timeout and sanitized errors. |
| Provider fields | `ZipLocation` and ZIP panel | Optional locality has an honest missing-field label; no live hotel model yet. The existing `HotelStay` requires a positive nightly price and must not be reused by inventing one. |
| Credentials | `backend/app/config.py`, `.gitignore` | Loads project-root `.env`; health exposes configuration status only. `.env` is ignored and untracked in the current index. This is not a historical secret scan. |
| Tests | `test_config.py`, `test_geocoding.py`, `test_demo_zip_route.py` | Existing controlled tests cover configuration, postcode/country matching, invalid coordinates, malformed responses, safe errors, invalid input, and route-level leading-zero preservation. |
| Earlier live evidence | `docs/zip-lookup.md` | September 24 records successful `16802` and `02108` geocoding. These are historical postcode checks, not hotel/map evidence. |

At the initial audit, missing work included Geoapify Places integration and its tests, a validated live-place response model, hotel list/map components and shared selection, tile-provider decision/attribution, hotel-result limits, and complete hotel-search state handling. Research and the early mockup are now complete: see [research](live-hotel-research.md) and [original design](live-hotel-design.md). Implementation, live hotel verification, recording, and report remain outstanding. The dependency audit and implementation contract below supersede the initial open design questions.

One behavior to revisit during implementation: a matching geocoding result with invalid coordinates is currently skipped and may become an unresolved response. Decide and test how malformed provider data should be classified; it must never trigger a different-location search or appear as a successful empty hotel search. Provider quota failures currently use the generic provider-failure path and have no dedicated quota test.

## Acceptance checklist

Items remain unchecked until verified for the completed Part 1 feature, even where the ZIP demonstration supplies a working foundation.

- [ ] Accept exactly five ASCII digits as a string in Vue and FastAPI; preserve `02108`. Reject invalid input before provider requests.
- [ ] Resolve the requested U.S. postcode with usable coordinates. Treat mismatched postcode/country or unresolved lookup explicitly; never search a substitute location.
- [ ] Request Geoapify hotel places within 5,000 meters of the returned point through FastAPI. Verify category, radius, and coordinate order against official documentation and controlled tests.
- [ ] Return genuine provider identifiers, available names/locations, and validated coordinates in a separate external-place model. Label or omit missing fields honestly; do not invent prices, ratings, availability, or confirmations.
- [ ] Show returned hotels in a Vue list and Leaflet map; selecting either identifies the same provider place in the other. Support keyboard selection and a usable narrow-screen layout.
- [ ] Show distinct initial, loading, results, invalid-input, unresolved-ZIP, no-nearby-results, and failed-request states. Provider failures and quota/rate-limit responses must not look like successful empty searches. Prevent stale results/markers from misleading users after a new search.
- [ ] Explain the postcode-point center and 5 km radius. Document provider result limits and variable coverage; do not claim an exhaustive inventory or bookable rooms.
- [ ] Keep geocoding/Places credentials backend-only in ignored, untracked `.env`; exclude secrets from logs, reports, screenshots, and recordings. Research tile-provider rules, visible attribution, and any separately restricted client credential.
- [ ] Complete research before implementation: existing application patterns, weaknesses, adopted decisions, official API/library/tile documentation, usage limits, and source links.
- [ ] Save an early mockup image or accessible link before implementation, showing intended layout and relevant states; document later changes.
- [ ] Record expected-versus-observed verification, exact commands/results, tested ZIP and observation date, corrections, and limitations. Distinguish live from simulated checks; do not assert a fixed live hotel count.
- [ ] Recheck sample Boston (four joined trip rows), Aspen (no results), and existing booking behavior. Preserve SQLite state and prior work.
- [ ] Supply a new screen-recorded live demonstration of Part 1 with a working instructor-accessible link; prior ZIP screenshots and sample-booking videos are insufficient.
- [ ] Prepare `report.md` with repository link, assessed commit, startup/configuration, research, original mockup and changes, demo, verification, and AI disclosure/evidence. Identify actual tools/models and a genuine failed or revised approach. Verify instructor access to every linked artifact without exposing credentials.

## Implementation responsibilities and sequence

1. Research existing interfaces and current official Geoapify, Leaflet, and tile-provider documentation; record sources and decisions in `docs/live-hotel-research.md`.
2. Create the early mockup and `docs/live-hotel-design.md` before application changes.
3. CHECK installed dependencies/manifests/lockfiles. Explain exact proposed changes and obtain student approval before TAKE ACTION; VERIFY approved installations. No dependency changes are authorized by this plan alone.
4. Define the API contract and external-place model. Python/Pydantic owns data validation; FastAPI routes dispatch to Python provider/controller logic. Reuse exact postcode resolution where appropriate. Choose endpoint, hotel category, result limit, and tile provider after research rather than treating this plan as an implemented contract.
5. Implement and test the backend provider flow, bounded requests, missing data, and safe error mapping. Existing SQLite sample booking storage remains unchanged.
6. Implement small Vue Composition API components for ZIP form, feedback, hotel list, and Leaflet map with shared provider-ID selection. Vue owns display and interaction, not geocoding or Places calls directly to Geoapify.
7. Verify automated checks, live browser behavior, controlled failure/empty responses, keyboard/mobile layout, and sample regressions. Use the existing AutoLoop for corrections; keep the smoke test itself read-only.
8. Prepare a new recording and submission report, preserving prior assignment evidence. Review the full diff and successful/no-results city searches before a Git checkpoint. Do not mark submission complete until assessed code and all artifacts are accessible and the student has uploaded the report.

Sequential copyable prompts are in [the prompt guide](../prompts/10-live-hotel-search.md).

## Verification for this preparation step

- Targeted existing ZIP/configuration tests: `backend/.venv/bin/python -m pytest backend/tests/test_config.py backend/tests/test_geocoding.py backend/tests/test_demo_zip_route.py -q` — **43 passed in 0.43s** on September 29, 2026. These use controlled responses, not live Geoapify calls.
- `git check-ignore .env` returned `.env`; `git ls-files -- .env '.env.*'` returned no entries. No credential contents were read or printed.
- Only project instructions, this plan, and the current handoff are changed by this preparation step. Application behavior, dependencies, data, and run instructions are unchanged.
- Not run for this documentation-only step: fresh live API requests, browser/UI checks, full backend suite, frontend lint/build, or new hotel/map verification. Historical results remain labeled by date. No commit, push, or submission is performed.

## Dependency audit and proposal — September 29, 2026

**CHECK, approved TAKE ACTION, and installation VERIFY completed.** The inventory below records the pre-installation state; see the installation result following the proposal.

| Environment | Observed state | Decision |
| --- | --- | --- |
| Frontend | Node 24.20.0, npm 11.19.0; installed Vue 3.5.42, Vite 8.3.0, @vitejs/plugin-vue 6.0.8, ESLint 10.10.0, @eslint/js 10.0.1, eslint-plugin-vue 10.11.0, globals 17.12.0. `npm ls --depth=0` exited 0. | Reuse the installed Vue/Vite stack and native browser fetch. No Vue map wrapper or HTTP client needed. |
| Frontend lockfile | `frontend/package-lock.json`, lockfileVersion 3; inspected Vue/Vite/plugin/ESLint entries match installed versions. Leaflet is absent from manifest, lockfile, and installed directory. | Add only the proposed Leaflet package after approval. Preserve existing resolved versions. |
| Backend | FastAPI 0.141.1, Pydantic 2.13.5, Uvicorn 0.52.4, pytest 9.1.1, python-dotenv 1.2.3 installed. `pip check`: no broken requirements. | Reuse Python's urllib/json, existing configuration and geocoding, and current test tools. No new backend dependency. |
| Backend dependency record | `backend/requirements.txt` pins existing packages except the pre-existing unpinned `python-dotenv` entry. No separate backend lockfile was found. | Record this reproducibility limitation; do not pin, upgrade, or otherwise change it without approval. |

Proposed package: **`leaflet@1.9.4`**, saved as an exact runtime dependency for map rendering, markers, selection events, radius circle, tile loading, and attribution. The [official Leaflet download page](https://leafletjs.com/download.html), accessed September 29, 2026, identifies 1.9.4 as stable; 2.0.0-alpha.1 is a prerelease. Use the stable API researched for the mockup.

Exact command, executed from `frontend/` **only after approval**:

```sh
npm install --save-exact leaflet@1.9.4
```

Expected installation changes: `frontend/package.json`, `frontend/package-lock.json`, and the ignored `frontend/node_modules/` installation (including npm's internal lock metadata). No backend requirements or application source changes in this installation step. Later map integration will import Leaflet and its bundled CSS in the frontend. Do not run upgrade or audit-fix commands; review the lockfile diff for unrelated resolution changes.

Verification procedure: verify `npm ls leaflet --depth=0`, exact manifest/lock versions and resolved CSS/JS assets, then run frontend lint/build and inspect the dependency diff. The pip inventory emitted a cache-directory warning because the user's cache was not writable; both inventory and compatibility checks completed without installation.

### Approved installation result — September 29, 2026

The student explicitly approved the exact proposal. Ran `npm install --save-exact leaflet@1.9.4` from `frontend/`. The initial sandbox attempt failed to resolve `registry.npmjs.org` (ENOTFOUND); retry with authorized network access succeeded, adding one package. npm reported zero vulnerabilities. It also warned about a pre-existing `fsevents@2.3.3` install script not covered by its allowScripts policy; no script-policy approval or unrelated dependency change was made.

- `npm ls leaflet --depth=0`: **leaflet@1.9.4**, exit 0.
- Manifest and lockfile: exact version **1.9.4**; every pre-existing locked package entry unchanged. Only Leaflet dependency/root metadata and its package entry added.
- Local Leaflet JavaScript, stylesheet, and marker icon assets: **present**.
- `npm run lint`: **passed**, exit 0.
- `npm run build`: **passed**, 17 modules, 235 ms.
- `git diff --check`: **passed**.

Installation is complete; map integration and browser validation remain for the implementation stage. The build verifies the current app, which does not yet import Leaflet. No backend dependency, application source, SQLite schema, or sample record was changed.

## Implementation contract — backend and frontend implemented September 29, 2026

### Route and provider flow

Add **`GET /api/discovery/hotels?postcode=02108`**. Require `postcode` as exactly five ASCII digits with no default; Vue trims surrounding whitespace before submission, while the API validates the submitted string strictly. Never parse it as an integer. Preserve existing `/api/hotels`, booking routes, and `/api/demo/zip-location` behavior.

Use the existing geocoding/configuration foundation. Resolve `postcode`, `type=postcode`, `filter=countrycode:us`, `format=json`, with an explicit geocoding limit of 5. The discovery flow must establish exact returned postcode, U.S. country code, postcode-level result, and finite bounded coordinates. Do not trust a city's matching ZIP field alone. No matching postcode candidate means unresolved; a matching candidate with unusable coordinates or malformed provider structure is a provider-data error. Reuse parsing through a small helper if needed rather than copying it; regression-test the old demo contract before changing shared logic.

Only after resolution, request Geoapify Places with `categories=accommodation.hotel`, `filter=circle:<longitude>,<latitude>,5000`, `bias=proximity:<longitude>,<latitude>`, and `limit=20`. One page; no pagination, boundary search, viewport search, or location permission. These parameters follow the [researched official documentation](live-hotel-research.md). Both requests run in Python with finite timeouts (reuse 10 seconds per provider request), backend-only credentials, sanitized errors, and no automatic retry loop. Keep synchronous urllib work in a synchronous FastAPI route/worker, not on an async event loop.

### Successful response: Pydantic models

Return HTTP 200 for results or a genuine successful empty provider response. Define separate discovery models; do not extend `HotelStay`, fabricate `nightly_price`, or attach sample trip/booking IDs.

| Model / field | Type and meaning |
| --- | --- |
| `SearchCenter.postcode` | Five-digit string; equals submitted ZIP. |
| `SearchCenter.country_code` | Literal `us`. |
| `SearchCenter.locality` | Provider text or null. |
| `SearchCenter.latitude`, `.longitude` | Strict finite numeric values within [-90, 90] / [-180, 180]; reject booleans and numeric strings. |
| `ExternalHotel.place_id` | Nonblank genuine provider place ID. Unique within returned hotels. |
| `ExternalHotel.name`, `.address` | Nonblank provider strings or null. Address uses available formatted address, or joins supplied address components without inventing missing parts. UI owns missing-field labels. |
| `ExternalHotel.latitude`, `.longitude` | Same coordinate validation as center; never substitute center coordinates. |
| `HotelDiscoveryResponse.provider` | Literal `geoapify`. |
| `.center` | `SearchCenter`. |
| `.radius_meters` | Literal 5000. |
| `.hotels` | List of `ExternalHotel`, length 0–20. |
| `.count` | Number of unique usable hotels returned; equals list length. |
| `.limit` | Literal 20: requested provider page cap, not a total count. |
| `.limit_reached` | True when the raw provider page contains 20 records, before validation/deduplication. Means more may exist, not that more definitely exist. |
| `.omitted_count` | Number of unusable provider records omitted; does not include duplicates. |
| `.duplicates_removed` | Count of repeated place IDs removed; keep the first valid occurrence in provider order. |

Do not add a claimed total inventory or a false `has_more` certainty. Counts/flags derive from the actual response. Empty names/addresses normalize to null. A valid nonempty page may return valid records with explicit `omitted_count` feedback, but a nonempty page with no usable records must return a provider-data error, not 200 with an empty list. Missing/malformed `features` is an error; an actual empty feature array is empty success. Coordinates outside the requested radius must not be plotted as valid nearby results; the implementation should validate the returned point distance and count rejected records as omitted. Unexpected pages larger than the requested cap are provider-data errors.

For a successful empty search, return the resolved `center`, `radius_meters: 5000`, `hotels: []`, `count: 0`, `limit: 20`, `limit_reached: false`, `omitted_count: 0`, and `duplicates_removed: 0`, alongside `provider`. Retain the map center/radius and show that no hotels were returned, not that none exist.

### Errors and UI mapping

| HTTP status | Condition | Response / UI handling |
| --- | --- | --- |
| 422 | Missing/invalid `postcode` | Retain FastAPI's standard validation `detail` array. Vue maps this status to “Enter a five-digit U.S. ZIP code.” No provider call. |
| 404 | No matching U.S. postcode-level location | `detail: {code: "zip_unresolved", message: "The requested U.S. ZIP could not be located."}`; no Places call. |
| 503 | Backend key absent | `detail: {code: "service_unconfigured", message: "Hotel search is not configured."}`. |
| 502 | Provider failure, timeout, rejected credentials, or unusable response | `detail: {code: "provider_error", message: "Hotel search could not be completed."}`. Never expose raw provider body, URLs, or keys. |
| 503 | Provider explicitly reports quota/rate limiting, including HTTP 429 | `detail: {code: "provider_limited", message: "Hotel search is temporarily limited. Try again later."}`. Forward only a validated retry delay via `Retry-After` if supplied; otherwise omit it. Do not label every 403 as quota exhaustion. |

Vue maps network errors and other unexpected non-2xx responses to failed-request feedback. Safe error messages and codes above belong only to the new route; do not globally rewrite validation or errors on existing endpoints. Empty success remains HTTP 200 and is never used for outages. Tile failures are a separate frontend state and do not alter the successful hotel response.

### MVC ownership and intended file boundaries

| Responsibility | Intended location / behavior |
| --- | --- |
| Models | `backend/app/discovery_models.py`: Pydantic center, external hotel, and response models. Keep sample models unchanged. |
| Routing | `backend/app/main.py`: validate ZIP, call discovery controller, declare response model, map safe errors. |
| Provider/controller | `backend/app/discovery.py`: coordinate geocoding and Places, normalize/validate results and limit metadata. Reuse `geocoding.py` and `config.py`; keep provider details out of routes and Vue. |
| View / selection | Small components under `frontend/src/components/` for discovery form/status, hotel list, and Leaflet map; parent owns results, loading/error state, and `selectedPlaceId`. Both representations emit the same provider-ID selection. |
| Map | Convert provider longitude/latitude to Leaflet latitude/longitude explicitly. Use keyless OSM tiles and visible map/API credits. Pan/zoom/selection make no new geocoding/Places calls. |
| Existing data | Current SQLite schema, seed process, sample hotel/booking controller, and records unchanged. No persistent live-place storage or shortlist in Part 1. |

Clear stale results and selection when starting a new search; prevent repeated submits and ignore outdated responses. Preserve ZIP input on errors. Use real buttons, descriptive marker labels, visible focus, and the missing-field/limit language from the original design. API success is not evidence of availability or bookability.

### Verification gates for later implementation

Controlled tests must cover exact/leading-zero ZIP, postcode-level/country mismatch, no Places call on unresolved input, circle radius and coordinate order, optional text, invalid coordinates, duplicate IDs, partial/all-unusable results, true empty results, limit flags, sanitized provider failure, and quota/retry handling. Browser checks must cover both selection directions, keyboard/narrow-screen behavior, all design states, tile attribution/failure, and original sample regressions. The contract stage itself made no implementation changes. The subsequent backend implementation and controlled test results are recorded in [backend verification](live-hotel-verification.md); frontend list/map checks and one live search are now also recorded there.
