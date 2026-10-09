# Wayfinder Hotels — Part 1

> **Demonstration recording · 2 minutes 6 seconds (silent)**
> **[Watch/download the Part 1 screen recording](https://raw.githubusercontent.com/mallorypierz/hotel_app/98b7b19c6f309d31b6349d9f495112828c0f595f/docs/live-hotel-student-demo.mp4)** · [GitHub video page](https://github.com/mallorypierz/hotel_app/blob/98b7b19c6f309d31b6349d9f495112828c0f595f/docs/live-hotel-student-demo.mp4)
> Public access — no sign-in required. GitHub does not preview this file size; download the MP4 and open it in your video player.

## Repository and commit

**Assignment 2, Part 1 — Live Hotel Search and Map**

**Report finalized from available evidence: September 29, 2026. Canvas submission remains outstanding.**

| Required item | Current status |
| --- | --- |
| Repository | [mallorypierz/hotel_app](https://github.com/mallorypierz/hotel_app) — public; unauthenticated access verified September 29, 2026 |
| Assessed Part 1 code commit | [`e6687356b620798414cb249cf5bde918d461aead`](https://github.com/mallorypierz/hotel_app/commit/e6687356b620798414cb249cf5bde918d461aead) |
| Published code/evidence | Published to `origin/main`; assessed checkpoint linked above |
| New screen-recorded demonstration | [Watch the 2:06 recording](https://raw.githubusercontent.com/mallorypierz/hotel_app/98b7b19c6f309d31b6349d9f495112828c0f595f/docs/live-hotel-student-demo.mp4) — publicly available |
| Artifact access | Public repository, linked artifacts, and recording available without login |
| Canvas upload | **PENDING — not performed** |

Assessed application/evidence checkpoint `e6687356b620798414cb249cf5bde918d461aead` was created and pushed to
`origin/main` after final diff review and manual Boston/Aspen checks. This report
update is a documentation-only follow-up; assessed application code is unchanged.
Public access was separately checked without credentials: repository metadata,
all 96 assessed artifact files (byte-for-byte matches), and current/previous
report URLs passed. This establishes public availability without an invitation;
it does not impersonate the instructor or guarantee institutional-network access.

The previous assignment report is preserved byte-for-byte as
[report-previous-assignment-part2.md](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/report-previous-assignment-part2.md) beside
this report. Its original link base and artifacts are unchanged. Its recording
is historical evidence only, not evidence of the live hotel/map feature.

Existing assessed artifact links below are immutable GitHub URLs suitable for
standalone Markdown. The recording is publicly linked above and in the demonstration section below.
The previous report remains unchanged.

## Implementation

**Implemented scope and MVC**

Enter a five-digit U.S. ZIP string, including a leading zero such as `02108`.
`GET /api/discovery/hotels?postcode=02108` resolves only the exact requested U.S.
postcode-level location and then searches Geoapify `accommodation.hotel` places
within 5,000 meters of the returned longitude/latitude point. An unresolved or
mismatched location never triggers a substitute-location search.

One ZIP input handles location lookup and live hotel discovery in the same
section; no separate ZIP demonstration form is shown. The legacy API endpoint
remains available. Vue renders the returned center, a hotel list and a Leaflet map with shared
provider-place-ID selection. List and marker controls support keyboard use;
the map stacks above the list on narrow screens. The interface distinguishes
initial/loading, results, invalid input, unresolved ZIP, successful empty
results, request failure, quota delay, and separate map-imagery failure.
Editing/submitting a ZIP clears old results; aborted/outdated responses are
ignored. Map pan/selection does not request more hotel records.

Pydantic defines separate validated external-place models. Python controller/
provider modules own geocoding, Places queries, optional field mapping,
timeouts, radius validation, deduplication, and safe errors. FastAPI routes
validate and dispatch. Vue owns presentation and shared selection. SQLite and
sample booking controllers retain the previous workflows unchanged; no new
live-place storage or schema is introduced.

One provider page is capped at 20 records. Coverage varies and is not exhaustive;
`limit_reached` means more places may exist, not that more definitely exist.
Missing names/addresses are labeled honestly; invalid/out-of-radius records
are omitted with counts, and an all-unusable nonempty page fails. There are no
invented live prices, ratings, room availability, or reservation confirmations.
The circle covers 5 km around the postcode point, not the whole ZIP boundary or
the traveler's location. Sample stays/bookings remain explicitly separate.
No shortlist, authentication, payments, real booking service, or deployment is
included in Part 1.

## Verification

**Verification from actual evidence**

Full inputs, expected/observed results, corrections and screenshots are in
[the verification record](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/live-hotel-verification.md). Dates below are
September 29, 2026, Eastern; machine logs use September 30 UTC where applicable.

| Evidence | Recorded result |
| --- | --- |
| Full backend suite, final checkpoint gate | **124 passed in 0.40s** |
| Frontend lint/build after single-ZIP refinement | Passed; 26 modules, build 194 ms |
| Live `16802`, 20:33:24 Eastern | HTTP 200; exact U.S. center; API/list/marker counts matched (20 at observation time) |
| Live `02108`, 20:33:26 Eastern | HTTP 200; leading zero retained; exact U.S. center; counts matched (20 at observation time) |
| Controlled upstream/browser responses | Invalid, mismatched postcode/country, unresolved, empty, failure, quota/rate, loading/stale and tile-failure checks passed; no live quota exhausted |
| Selection/accessibility/layout | Both directions; Enter/Space, same-name IDs, focus retention, 390/320 px reflow and attribution passed in controlled checks |
| Sample regression | Boston four joined trip rows, Aspen no results; booking create/cancel/delete/refresh/restart passed; original database restored |
| D1 discovered then fixed | Missing `/favicon.ico` caused console 404; local SVG/reference correction passed fresh-browser 200 `image/svg+xml`, no fallback request or console/page errors; 16 controlled regressions passed |
| Submission preparation browser review | Boston/Aspen manually operated and inspected again; see [review/checkpoint plan](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/live-hotel-checkpoint.md) |

[Live 16802](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/smoke-live-16802.png) · [Live 02108](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/smoke-live-02108.png) ·
[320px live layout](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/smoke-live-320.png) ·
[simulated selection](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/smoke-simulated-selection-mobile.png) ·
[D1 fresh-load result](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/browser-checks/d1-favicon-results.json).

The two live result counts are observations, never fixed acceptance counts or
claims of complete inventory. Controlled screenshots/errors are simulated
checks, not real outages. No direct browser Geoapify API requests or credential
query parameters were observed in the recorded network check; `.env` remained
ignored/untracked. No known verified smoke defect remains open after D1.

Limitations: Chrome/macOS and responsive emulation only for the extended smoke;
no physical-device, full screen-reader, cross-browser matrix, or independent
hotel-location survey. Not every live marker was individually clicked. The
credential review was not an exhaustive Git-history/browser-memory audit.
Historical earlier checks were not all repeated for the favicon-only fix.
Public artifact access is verified. Instructor-specific device/network access
is not tested; recording-review limits are described below.

<a id="demonstration-recording"></a>

**Student-recorded demonstration**

**[Watch the Part 1 demonstration — 2 minutes 6 seconds](https://raw.githubusercontent.com/mallorypierz/hotel_app/98b7b19c6f309d31b6349d9f495112828c0f595f/docs/live-hotel-student-demo.mp4)**

[Open the video on GitHub](https://github.com/mallorypierz/hotel_app/blob/98b7b19c6f309d31b6349d9f495112828c0f595f/docs/live-hotel-student-demo.mp4). Public MP4; no account or permission request
is needed. GitHub does not preview this file size; use the direct link above to
download and open it in your usual video player. The student authorized public publication.

Recorded September 29, 2026, at approximately 21:14 Eastern (source filename).
Original duration: 126.33 seconds; H.264 sharing copy: 126.15 seconds (about
**2 minutes 6 seconds**), 1702×1370, **no audio track**. The original MOV is
preserved; the sharing copy re-encodes the supplied video without synthetic
content or intentional trimming. See the [recording/access review](https://github.com/mallorypierz/hotel_app/blob/98b7b19c6f309d31b6349d9f495112828c0f595f/docs/live-hotel-final-access.md).

Sampled frames show the localhost app, leading-zero ZIP `06109` (Wethersfield,
US), `16801` (State College, US), returned centers, the 5 km explanation and
20-result limit, hotel names/addresses, selected list/marker states, and map
attribution. The interface matches assessed code `e668735`; the application
source remains unchanged since that checkpoint. A Git SHA and provider request
trace are not displayed in the clip, so it alone does not prove runtime version
or live transport. No simulated label was observed; interception status was not
explicitly confirmed. Earlier live and controlled verification retain their
separate labels.

The review sampled frames every ten seconds; it was not continuous playback or a
frame-by-frame audit. Startup terminals, spoken explanation, invalid/error
feedback, keyboard operation, and narrow-screen demonstration are not established
by that review. These are covered where noted in the verification record, not
claimed as demonstrated by this clip. The course recording rubric/time limit
was not supplied; compliance is not inferred. The [recording script](https://github.com/mallorypierz/hotel_app/blob/46c14205d758045e0e837d34c12a7010d4e14964/docs/live-hotel-demo-script.md)
remains available if a supplemental demonstration is required.

## Project context and next steps

**Exact setup and startup**

Use the checked-out project root. Recorded environment: Python 3.12.5; the
September 29 dependency audit recorded Node 24.20.0/npm 11.19.0. These are
observed versions, not a tested minimum-version matrix. See [README](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/README.md)
and the [dependency audit](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/live-hotel-plan.md).

For a fresh checkout, after the project's required dependency-install approval:

```sh
git clone https://github.com/mallorypierz/hotel_app.git
cd hotel_app
git checkout e6687356b620798414cb249cf5bde918d461aead
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
cd frontend
npm install
cd ..
```

Do not reinstall packages just to start the already prepared environment.
Leaflet is pinned to the student-approved `1.9.4`; no Vue map wrapper was added.
The pre-existing `python-dotenv` requirement is unpinned, a reproducibility
limitation retained without an unauthorized dependency change.

Privately create/edit project-root `.env` beside `frontend/` and `backend/` and
set `GEOAPIFY_API_KEY` to your own provider key. The key value is not included in
this report. `.env` is ignored and untracked. Existing process environment
variables take precedence; restart FastAPI after configuration changes. Never
put this key in `VITE_*`, frontend files, recordings, screenshots, URLs shown to
viewers, or reports. OSM tiles use no client key.

Backend terminal, from the project root on this Mac:

```sh
SSL_CERT_FILE=/etc/ssl/cert.pem backend/.venv/bin/uvicorn backend.app.main:app --reload --port 8010
```

This Mac needs the documented CA bundle because Python's default bundle is
absent. Certificate verification remains enabled. On a machine with a working
Python trust store, omit the `SSL_CERT_FILE` prefix. Do not use port 8000 for this
project. Frontend terminal:

```sh
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173/`. Vite proxies `/api` to `http://127.0.0.1:8010`.
`GET /api/health` reports configuration status without showing the key; it does
not validate provider access. Vite HMR is disabled; refresh after source changes.
Reuse healthy existing services instead of starting duplicates. Internet access
is needed for Geoapify/OSM; sample data remains local. Preserve the ignored
`data/wayfinder.sqlite3` to retain local sample bookings.

Verification commands:

```sh
backend/.venv/bin/python -m pytest backend/tests
cd frontend
npm run lint
npm run build
```

**Research, original design and changes**

- [Research and dated official sources](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/live-hotel-research.md): recorded
  browser inspection of OpenStreetMap and Google Maps, plus official Geoapify,
  Leaflet and OSM policy sources; inspected behavior is distinguished from docs.
- Original **pre-implementation** [layout mockup](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/live-hotel-mockup-v1.png)
  and [state board](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/live-hotel-states-v1.png), both preserved unchanged.
- [Design explanation and later changes](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/live-hotel-design.md): desktop
  sticky map, stacked narrow layout, selection details outside attribution,
  Show search area control, omission counts, explicit keyboard handlers,
  abort/version protection and quota countdown.
- [Agreed API contract and limits](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/docs/live-hotel-plan.md).

OSM attribution remains linked and visible. Keyless raster tiles use normal
browser caching/Referer behavior and viewport loading, with no bulk/offline
collection. Geoapify attribution is separate. Dense hotel markers may overlap;
list selection and zoom remain available.

**AI disclosure and evidence**

AI-assisted planning, implementation, tests, debugging and documentation used
Codex. The student confirmed the selected setting as **GPT-6 Astra, medium
reasoning** (“gpt 6 astra medium”). This is a student-confirmed setting, not a
per-call backend model attestation. The [AI disclosure/evidence log](https://github.com/mallorypierz/hotel_app/blob/46c14205d758045e0e837d34c12a7010d4e14964/docs/live-hotel-ai-evidence.md)
identifies tools, scope and provenance; [actual prompt excerpts](https://github.com/mallorypierz/hotel_app/blob/e6687356b620798414cb249cf5bde918d461aead/prompts/11-live-hotel-actual-evidence.md)
link instructions to code, decisions and verification. It preserves genuine
failed/revised approaches, including the favicon failure and correction.
When asked about additional AI tools, the student replied “no AI”; no additional
tools were reported. The prior explicit Codex/model disclosure is retained.
Native macOS AVFoundation/Swift inspected and transcoded the supplied recording;
Python checked public artifact links. No AI-generated video was substituted.
