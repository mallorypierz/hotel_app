# Wayfinder Hotels — Assignment 2 Part 2

**Revised October 1 brief · updated October 9, 2026.**
The complete two-request OpenAI workflow is verified with actual saved hotels,
including successful and no-match browser cases. **The Part 2 video recording
and course submission remain incomplete. Publication is also blocked by invalid GitHub Git credentials.** Controlled and live evidence are
labeled separately. See the [full benchmark audit](docs/chatbot-final-audit.md).

The original [Assignment 2 Part 1 report](report-assignment2-part1.md) is preserved
byte-for-byte at the repository root, keeping the same relative-link base and
all existing immutable code/video links. [Preservation hash and link inventory](docs/chatbot-verification-evidence/part1-report-preservation.json).
The [earlier assignment report](report-previous-assignment-part2.md) is also unchanged.

## Project access and assessed version

| Item | Actual status |
| --- | --- |
| Repository | [mallorypierz/hotel_app](https://github.com/mallorypierz/hotel_app) |
| Working branch | `assignment2_part2_in_class` |
| Current HEAD | `3a31777445071e51159e965c98e0ac41da6f0f88` — preserved local-storage foundation |
| Assessed Part 2 chatbot commit | `6bce3f406c675175f14dfe3e7e9b69520104d00b` — verified application/evidence checkpoint, local only; push rejected because GitHub credentials are invalid. |
| Part 2 demo video URL | **MISSING — script prepared; no new recording supplied or created** |
| Live OpenAI success/no-match evidence | **VERIFIED October 9 — real success and no-match, both model stages completed** |
| Repository/artifact access | Existing repository public (unauthenticated HTTP 200, private=false, October 9). New chatbot artifacts are NOT published: push authentication failed. |
| Access method | Existing repository public; new assessed artifacts unavailable remotely until push succeeds. Instructor-device/network conditions not tested. |
| Canvas submission | **NOT PERFORMED** |

Local relative links work in this checkout and will work in a published repository
containing these files. They are not proof of public availability. Before uploading
standalone report.md, publish an authorized assessed checkpoint and replace local
artifact links with that commit's immutable URLs, or provide the complete folder.
Do not use the old Part 1 video as a Part 2 chatbot demonstration.

## Startup and private configuration

See [README](README.md) for complete setup. Observed environment: Python 3.12.5 /
SQLite 3.45.3; Node 24.20.0 / npm 11.19.0. No chatbot dependencies were added.
For a fresh checkout, obtain project-required approval before installing declared
packages with `backend/.venv/bin/python -m pip install -r backend/requirements.txt`
and `npm install` in frontend; create the venv first with `python3 -m venv backend/.venv`.
Use the assessed chatbot code version identified in this report.

Privately configure project-root ignored `.env`: `GEOAPIFY_API_KEY` for discovery,
`OPENAI_API_KEY` for chat, `OPENAI_MODEL=gpt-4.1-mini-2025-04-14`,
`OPENAI_TIMEOUT_SECONDS=20`, `OPENAI_MAX_OUTPUT_TOKENS=1800`.
These are backend-only settings. Never show key values in source, browser config,
reports, screenshots, terminal recordings or chat. No alternate model/provider
fallback is implemented. Restart FastAPI after private changes.

Backend, project root (this Mac needs the existing CA bundle):

```sh
SSL_CERT_FILE=/etc/ssl/cert.pem backend/.venv/bin/uvicorn backend.app.main:app --reload --port 8010
```

Frontend, separate terminal:

```sh
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173/`; Vite proxies `/api` to 8010. Omit the SSL_CERT_FILE
prefix only on systems with a working default trust store. Preserve ignored
`data/wayfinder.sqlite3`: it contains student saves and sample bookings.

## Research, early design and revisions

[Dated OpenAI research](docs/chatbot-research.md), October 8, links official model,
Responses API, structured-output, pricing and error/limit documentation. Selected
snapshot: **OpenAI `gpt-4.1-mini-2025-04-14`**, for both calls. Documented prices
at research time were $0.40 input / $0.10 cached input / $1.60 output per million
tokens; no free tier was listed for this model. These are dated findings, not an
account-access or billing guarantee. Structured outputs help constrain proposals;
they do not prove SQL safety or correct factual reasoning. Standard-library
networking avoids an unnecessary SDK. Real calls succeeded October 9; future account availability is not guaranteed.

The prior [discovery research](docs/live-hotel-research.md) records actual comparison
site observations; no new competitor-chatbot study is claimed. Useful design
features retained: synchronized map/list selection, visible provenance, optional
missing fields. Limitations retained: provider result caps, uncertain coverage,
missing prices/availability, and overlapping markers.

Original pre-implementation chatbot designs, October 8:
[desktop](docs/chatbot-desktop-v1.png), [mobile](docs/chatbot-mobile-v1.png),
[state board](docs/chatbot-states-v1.png), [explanation](docs/chatbot-design.md).
All are clearly fictional design examples and remain unchanged. The
[dated design change log](docs/chatbot-design-changes.md) explains raw-night
retrieval instead of aggregate-only SQL, backend-rendered verified facts, all
candidate cards, initially collapsed evidence, and focus-preserving Send behavior.
[Implemented desktop](docs/chatbot-verification-evidence/desktop.png) and
[mobile](docs/chatbot-verification-evidence/mobile.png) screenshots use labeled mocks.

## Local-storage foundation and MVC

Saving retains exact provider IDs in `saved_hotels`, ZIP associations in
`saved_hotel_locations`, and simulated dated prices/rooms in `demo_hotel_nights`.
Duplicate saves preserve existing values; removal deletes only the selected
hotel and its dependent rows. Local-first search uses saved matches; only a
successful empty local lookup falls back to the frozen discovery API. Saves,
removals and bookings survive refresh/restart. [Schema](docs/assignment2-part2-schema.md)
and [storage workflow](docs/assignment2-part2-local-hotels.md).

| Layer | Responsibility and implementation |
| --- | --- |
| Model/data | Pydantic `chat_contracts.py` / `chat_models.py` validate input, SQL proposals and response shapes. `chat_queries.py` opens restricted read-only SQLite connections. `chat_stays.py` independently checks intent, provenance, every night, room counts and costs. |
| Controller | Thin `chat_routes.py` dispatches POST /api/chat to `chat_controller.py`. `llm_provider.py` owns backend-only OpenAI HTTP transport; `chat_prompts.py` owns trusted instructions. |
| View | `HotelChat.vue`, `ChatHotelCards.vue`, `ChatEvidence.vue` render questions/states/facts and read-only evidence. `useChat.js` calls only FastAPI, bounds requests, prevents duplicates and ignores stale replies. No raw HTML rendering or editable SQL interface. |

Assignment 1 sample search/bookings and frozen Part 1 ZIP/list/map/attribution
behavior remain separate. The chatbot does not save, remove or book hotels.
All rates and inventory carry the persistent label:
**“Simulated course rates and availability—not real booking information”.**

## Complete two-request workflow

1. The browser submits the question to FastAPI. First OpenAI request sends the
   question, relevant three-table schema and strict query rules; no saved rows or
   Assignment 1 traveler/booking records are sent in this first request.
2. OpenAI proposes SQL with bound parameters and explicit intent, or asks for
   clarification. The backend treats question text as untrusted and independently
   checks dates/ZIP/rooms/budget intent.
3. A dedicated `mode=ro` SQLite connection enforces query_only, a default-deny
   table/column/function authorizer, disabled extensions, single-statement
   preflight/execution and bounded work/results (50 rows, 24 KiB). Unauthorized
   SQL is rejected. The model never connects to SQLite.
4. The backend independently verifies retrieved raw nights, then calculates
   check-in-inclusive/checkout-exclusive totals and minimum room counts. Missing
   nights never imply availability; location associations must not duplicate sums.
5. Second OpenAI request sends the original question, bounded hotel identity/name,
   stay-date/rate/room records and checked facts. Record text is untrusted data.
   The model selects eligible IDs and factual reasons; Python validates those
   selections and renders verified dates/costs/availability. No answer fallback
   is manufactured if either request fails.
6. Vue shows the answer, facts, limitations and expandable question/SQL/validation/
   records/provider/model evidence, including safe failure states.

Only selected saved-hotel data leaves the backend, not the SQLite file,
coordinates, booking history or API key. Request `store:false` is documented;
it is not a promise of zero provider retention. See [research privacy details](docs/chatbot-research.md).

## Readable workflow trace — controlled, not live

**This question was actually exercised through mocked HTTP model responses and
real isolated SQLite retrieval. A real-provider trace is missing.** Full request
bodies and result: [captured trace](docs/chatbot-verification-evidence/mock-success.json).
The [displayed answer screenshot](docs/chatbot-verification-evidence/desktop.png)
replays the corresponding labeled fixture result in Vue, rather than proving
live end-to-end transport.

Question:

> Which saved hotels in 06109 have one room from Oct 10 to Oct 12, 2026, for $350 total or less?

Proposed SQL (mocked first model response):

```sql
SELECT h.hotel_id, h.name, n.stay_date, n.nightly_rate_cents, n.rooms_available
FROM saved_hotels h LEFT JOIN demo_hotel_nights n ON n.hotel_id=h.hotel_id
AND n.stay_date>=? AND n.stay_date<?
WHERE EXISTS (SELECT 1 FROM saved_hotel_locations l WHERE l.hotel_id=h.hotel_id AND l.postcode=?)
ORDER BY h.hotel_id, n.stay_date
```

Bound parameters: `["2026-10-10", "2026-10-12", "06109"]`.

Validation: `passed_read_only_and_record_verification`; 7 records, complete saved-subset retrieval, not truncated. Both mocked model stages completed.

Retrieved records (all seven; values are simulated cents and room counts):

| Hotel ID | Name | Night | Rate cents | Rooms |
| --- | --- | --- | --- | --- |
| demo-birch | Example Birch House | 2026-10-10 | 12000 | 3 |
| demo-birch | Example Birch House | 2026-10-11 | 14000 | 2 |
| demo-full | Example Unavailable | 2026-10-10 | 10000 | 0 |
| demo-full | Example Unavailable | 2026-10-11 | 10000 | 5 |
| demo-gap | Example Missing Night | 2026-10-10 | 9000 | 9 |
| demo-river | Example River Inn | 2026-10-10 | 14000 | 5 |
| demo-river | Example River Inn | 2026-10-11 | 16000 | 5 |

Backend answer displayed as literal text (the persistent label also appears above the form):

> Simulated course rates and availability—not real booking information
> Example Birch House (demo-birch): 2026-10-10 to 2026-10-12, 2 nights, 1 room(s), $260.00 total; at least 2 rooms on every night. Recommended because it has the lowest matching total.
> Checkout is excluded. Comparisons cover only saved hotels; all amounts and availability are simulated.

| Expected check | Observed |
| --- | --- |
| Birch Oct 10 + Oct 11 = 12000 + 14000 = 26000 cents | $260 total; two nights; minimum 2 rooms |
| River = 14000 + 16000 = 30000 cents | $300; minimum 5 rooms; Birch has lowest eligible total |
| Checkout Oct 12 excluded | Birch's Oct 12 99000-cent, zero-room row absent from retrieval; no false rejection |
| All nights must have enough rooms | Unavailable hotel rejected because Oct 10 has zero rooms |
| Missing Oct 11 cannot be inferred | Missing-night hotel has null full total and is ineligible |
| Two ZIP associations must not double Birch cost | Still $260; EXISTS constrains ZIP membership |

**No match:** same two-night stay, ZIP 06108, one room, $250 total returns
`no_matches` after two mocked calls; Birch's $260 exceeds the budget.
[Trace](docs/chatbot-verification-evidence/mock-no-match.json) ·
[displayed result](docs/chatbot-verification-evidence/no-match.png).
**Insufficient data:** ZIP 06109, Oct 11–14, one room, $350 total returns
`insufficient_data`; requested nights are missing.
[Trace](docs/chatbot-verification-evidence/mock-insufficient.json).

**Rejected queries:** fresh October 8 controlled checks submitted
`DELETE FROM saved_hotels`, `SELECT booking_id FROM bookings`, and
`SELECT name FROM saved_hotels; DELETE FROM saved_hotels` directly to the
restricted executor in a new disposable fixed-fixture database. All returned
`query_rejected`. Every table's contents and full schema matched before/after;
file SHA256 remained
`adcf5df8fb843d4931e6cc3f8e78b425643aecbc4efcde037eb34182f6f51041`.
[Per-attempt evidence](docs/chatbot-verification-evidence/rejected-queries.json).
These are controlled security tests, not live model proposals or a public SQL route.

## Repeatable verification and remaining work

[Fixed JSON fixture](data/chatbot-fixture.json) includes changing nightly rates,
zero/missing nights, leading-zero ZIP and multiple associations.
[Full verification commands/results](docs/chatbot-verification.md) describe isolated
loading, browser adapters, restart comparison, expected console errors and limits.
From the repository root, using existing packages:

```sh
backend/.venv/bin/python docs/browser-checks/chatbot-verification.py
backend/.venv/bin/python docs/browser-checks/chatbot-rejected-evidence.py
backend/.venv/bin/python -m pytest backend/tests
npm --prefix frontend run lint
npm --prefix frontend run build
```

Both evidence scripts create isolated databases; never overwrite student saves.
The last full verification on October 8 recorded **341 tests passed in 1.41s**,
clean lint, successful 33-module build (178ms), chatbot browser checks, 16 frozen
Part 1 scenarios, Boston four rows/Aspen empty, duplicate saves/removal/local-first,
and sample booking refresh/restart checks. Isolated table/schema/hash snapshots
were identical across restarts. Real student DB SHA256 stayed
`e7d83319033ee45c131fd8a9722ca492a1bc65638aa4b4b01d23ef4a29952c16`.
No fresh full-suite rerun was needed for this report-only assembly; the three
rejection evidence cases above were executed fresh.

### Actual live workflow — October 9

Question: “Compare saved hotels in ZIP 06109 for 1 room from 2026-10-10 to
2026-10-12 under $350 total for the stay.” OpenAI model
`gpt-4.1-mini-2025-04-14` completed both `hotel_query` and `hotel_answer`.
Proposed SQL:

```sql
SELECT h.hotel_id, h.name, n.stay_date, n.nightly_rate_cents, n.rooms_available
FROM saved_hotels h
LEFT JOIN demo_hotel_nights n ON n.hotel_id=h.hotel_id AND n.stay_date>=? AND n.stay_date<?
WHERE EXISTS (SELECT 1 FROM saved_hotel_locations l WHERE l.hotel_id=h.hotel_id AND l.postcode=?)
ORDER BY h.hotel_id, n.stay_date
```

Parameters: `["2026-10-10", "2026-10-12", "06109"]`. Outcome: passed read-only
validation and independent record verification; two rows, complete, not truncated.

| Saved hotel | Night | nightly_rate_cents | rooms_available |
|---|---|---:|---:|
| Comfort Inn | 2026-10-10 | 20000 | 15 |
| Comfort Inn | 2026-10-11 | 10000 | 20 |

The second request receives the original question, those retrieved records and
independently checked facts. Exact raw identifiers/SQL/records/model stages are in
the [live UI transcript](docs/chatbot-audit-evidence/live-success.txt) and
[screenshot](docs/chatbot-audit-evidence/live-success.jpg). Exact request bodies
are demonstrated separately in the [labeled controlled transport capture](docs/chatbot-audit-evidence/mock-success.json);
the live UI capture is not a provider packet capture.

Displayed answer: “Comfort Inn: 2026-10-10 to 2026-10-12, 2 nights, 1 room(s),
$300.00 total; at least 15 rooms on every night. Recommended because it meets
your dates, room count and budget.” Checkout exclusion and simulated-data
limitations are displayed. Expected $200+$100=$300 and min(15,20)=15; observed
values match, checkout October 12 excluded.

With the same request under **$1 total**, both real model stages again completed;
the frontend displayed no matching saved hotels and explained the $300 candidate
was outside budget. [Live negative transcript](docs/chatbot-audit-evidence/live-no-match.txt)
and [image](docs/chatbot-audit-evidence/live-no-match.jpg).

Fresh October 9 checks: **349 backend tests passed**, lint/build passed, manual
Boston four joined rows and Aspen no-results passed. Fixed-fixture success,
no-match, insufficient-data and rejected-query checks reran on isolated databases.
[Full expected/observed audit](docs/chatbot-final-audit.md) and
[no-mutation proof](docs/chatbot-audit-evidence/rejected-queries.json). Student database
remained byte-identical throughout the audit. Earlier October 8 results above
are historical, not the latest verification.

[Demo script](docs/chatbot-demo-script.md) distinguishes real calls from controlled
rejection evidence. No new video URL exists. Current limitations include Chrome
only, no screen-reader speech check, no production load or future quota guarantee, no instructor-device/network check, and conservative explicit
ZIP/year/dates/rooms/budget parsing. Cooperative query deadlines are not a hard
process sandbox; browser cancellation may not stop already-started provider work.

## AI disclosure

[AI tools/model provenance and genuine revisions](docs/chatbot-ai-evidence.md) ·
[selected actual prompt excerpts linked to code/tests](prompts/12-chatbot-actual-evidence.md).
Codex assisted research, design, implementation, tests, debugging and reporting.
The configured application model is known exactly; the current coding session's
exact backend snapshot is not exposed. No live OpenAI model execution, additional
AI tool use, new video or fresh access verification is invented.
