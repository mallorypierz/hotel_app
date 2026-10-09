# Assignment 2 Part 2 — chatbot audit and implementation plan

Audit date: October 8, 2026 (Eastern). Planning only; no chatbot implemented.
Authority: the student-supplied **Revised Part 2 — Business Intelligence with
RAG and an LLM**, updated October 1, 2026, plus [project rules](../AGENTS.md).
The revised brief requires two model requests around checked SQL retrieval;
local storage alone meets the separate in-class checkpoint, not this submission.
The revised deadline is October 8, 2026, 11:59 PM Eastern.

Provider decision, October 8: the student selected **OpenAI API only**.
[Provider research](chatbot-research.md) selects the documented snapshot
`gpt-4.1-mini-2025-04-14` for both requests and records pricing, API format,
structured output, failure handling and private setup. Account access/live
calls remain unverified. Early mockup and implementation remain pending;
earlier provider-selection language below describes the original audit stage.

Implementation update, October 8: the [early design](chatbot-design.md) is saved,
and the [read-only retrieval boundary](chatbot-retrieval-verification.md) is now
implemented with 90 new tests (256 total backend tests passing). The status
tables below preserve the initial audit; LLM integration, chatbot routes and
Vue behavior remain pending.

Subsequent backend update, October 8: [two-request backend verification](chatbot-backend-verification.md)
records implemented POST /api/chat, transport, independent stay/record checks
and 341 passing backend tests. OpenAI key is absent, so live integration remains
unverified; only labeled mocked calls have run. Frontend and recording pending.

## Audited baseline and preservation boundary

Branch: `assignment2_part2_in_class`. HEAD:
`3a31777445071e51159e965c98e0ac41da6f0f88` (local-first storage checkpoint).
The working tree was clean before this audit. No branch switch, commit, push,
dependency change, service restart, or provider request was performed.

Read [README](../README.md), [current handoff](../handoffs/current.md),
[storage schema](assignment2-part2-schema.md),
[local operations and verification](assignment2-part2-local-hotels.md), and the
storage, routes, models, Vue discovery components/composable, and test code.
Older statements that local tables were empty are historical: the current
database has saved records described below.

| Capability | Audited status / implementation |
| --- | --- |
| Assignment 1 search and bookings | Existing SQLite initialization, controller, routes, sample UI; preserve supplied IDs/records and seed marker. |
| Frozen Part 1 discovery | Existing ZIP/geocoding/Places API and synchronized list/map; preserve exact ZIP, leading zeros, 5 km radius, result limits, errors, and visible attribution. |
| Local storage | `local_models.py`, `local_controller.py`, `local_routes.py`, `migrations.py`; GET/POST/DELETE `/api/local-hotels` implemented. |
| Save/remove | Transactional save preserves existing metadata/night edits, adds missing associations/nights; removal deletes selected hotel plus all its associations/nights. |
| Local-first lookup | `useDiscovery.js` uses saved matches; only a successful empty local response falls back to discovery. Storage failures do not trigger fallback. |
| Saved UI | `DiscoveryList.vue` has Add/Remove controls, global saved-ID status, and explicitly simulated dated rates/room counts. |
| Chatbot | No chatbot route, provider integration, SQL validation boundary, two-request orchestration, or chatbot Vue view found. All remain to implement. |
| Submission evidence | Prior reports and browser evidence exist. Revised chatbot research, early mockup, dedicated fixed JSON fixture, live trace, verification, report, and recording remain. Existing JS-controlled responses do not replace the required repeatable JSON fixture. |

Do not repurpose the writable booking/local controllers as an arbitrary SQL
executor. Do not change frozen provider contracts, existing storage semantics,
sample records, or demo dates as a side effect of chatbot work. No schema
migration is currently needed. No vector database, authentication, payments,
real bookings, deployment, or persistent chat-history storage is proposed.

## Actual SQLite schema and data

Database: `data/wayfinder.sqlite3`, ignored and untracked. Inspected directly
with SQLite URI `mode=ro` and `PRAGMA query_only=ON`, without app startup or
initialization. Live schema agrees with `backend/app/migrations.py`.

| Table | Actual columns and constraints |
| --- | --- |
| `saved_hotels` | `hotel_id TEXT NOT NULL PRIMARY KEY COLLATE BINARY`; nullable `name TEXT`, `address TEXT`; required numeric `latitude REAL` in [-90,90] and `longitude REAL` in [-180,180]. |
| `saved_hotel_locations` | Required `hotel_id TEXT` referencing saved hotels; required five-ASCII-digit `postcode TEXT`; required `country_code TEXT` constrained to `us`; nullable `locality TEXT`; required bounded numeric `latitude REAL`, `longitude REAL`. Composite PK `(hotel_id, postcode)`; index on `postcode`. These coordinates are the ZIP center, not hotel coordinates. |
| `demo_hotel_nights` | Required `hotel_id TEXT` referencing saved hotels; required valid ISO calendar `stay_date TEXT`; required nonnegative integer `nightly_rate_cents INTEGER DEFAULT 10000` and `rooms_available INTEGER DEFAULT 20`; composite PK `(hotel_id, stay_date)`. |

API `place_id` maps to exact, case-sensitive `hotel_id`; preserve whitespace and
case. Foreign keys have no delete cascade; existing controller removes children
explicitly. Relationships are one hotel to many locations and many nightly rows.
Join on `hotel_id`, never names. A location join can multiply nightly records
when a hotel has multiple ZIP associations; filter the ZIP or use `EXISTS` before
aggregation. Missing names/addresses remain unknown, not invented.

Observed current counts: 8 sample hotels, 12 trips, 6 users, 6 bookings, 1 metadata
row; **1 saved hotel, 1 location association, 5 demo nights**. Saved hotel:
Comfort Inn, ZIP **06109**, Wethersfield, US. The current edited demo values are:

| Stay date | Rate cents | Simulated USD/night | Simulated available rooms |
| --- | ---: | ---: | ---: |
| 2026-10-10 | 20000 | 200.00 | 15 |
| 2026-10-11 | 10000 | 100.00 | 20 |
| 2026-10-12 | 10000 | 100.00 | 20 |
| 2026-10-13 | 10000 | 100.00 | 20 |
| 2026-10-14 | 10000 | 100.00 | 20 |

These are stored course data, not provider prices/inventory. Do not reset the
edited first night to defaults. One saved hotel supports a grounded answer,
but not a meaningful comparison of multiple hotels. Use isolated labeled
fixtures for comparison tests; later live demonstration may need additional
hotels saved deliberately through the existing UI.

Potential later verification inputs, **not chatbot results observed today**:

- “For one room in 06109, checking in October 10, 2026 and out October 12,
  2026, which saved hotels cost at most $350 total?” Expected current record:
  Comfort Inn, two nights, $300 total, minimum 15 rooms across those nights.
- Same stay with a $250 total budget: no matching saved hotel.
- Check-in October 14, checkout October 16: October 15 is missing; do not claim
  full-stay availability or calculate a complete total from only October 14.

## Environment and dependency check

Observed Python 3.12.5, SQLite 3.45.3, Node v24.20.0, npm 11.19.0.
`backend/requirements.txt` matches installed pinned versions; `python-dotenv`
is unpinned in that file and installed at 1.2.3. No separate Python lockfile was
found. Relevant installed packages: FastAPI 0.141.1, Pydantic 2.13.5,
uvicorn 0.52.4, pytest 9.1.1. No LLM SDK, HTTPX, or SQL-parser package is installed.
`pip check` reports no broken requirements. Pip's cache-permission warning
disabled its cache; it did not prevent inspection.

Frontend lockfile version 3 root requirements match `package.json`; all eight
direct installed versions match lock entries: Vue 3.5.42, Leaflet 1.9.4,
Vite 8.3.0, @vitejs/plugin-vue 6.0.8, ESLint 10.10.0,
@eslint/js 10.0.1, eslint-plugin-vue 10.11.0, globals 17.12.0.
`npm ls --depth=0` succeeds. Existing urllib/json/sqlite3, Pydantic, Vue and
dependency-free ASGI test helpers are candidates for reuse; SDK installation
is not assumed necessary. Preserve the Geoapify transport rather than changing
its behavior to accommodate an LLM.

No dependency change is approved or performed. If one becomes necessary,
CHECK installed/locked packages, explain exact package/version, installation
command, purpose and affected files, obtain student approval, TAKE ACTION only
for that change, then VERIFY and record results.

## Proposed MVC and file boundaries

All names below are proposals, not existing chatbot functionality.

| Responsibility | Proposed files / limited integration |
| --- | --- |
| Model contracts | `backend/app/chat_models.py`: bounded question, SQL proposal plus typed parameters, clarification, answer/evidence and safe-error contracts. |
| Local retrieval | `backend/app/chat_queries.py`: explicit schema/column allowlist, SQL validation, dedicated read-only connection, resource limits and result mapping. Do not invoke initialization. |
| Provider adapter | `backend/app/llm_provider.py`: one selected provider, POST transport, response validation, timeouts and sanitized errors. Reuse backend config conventions with minimal additions to `config.py`. |
| Controller | `backend/app/chat_controller.py`: request 1 → validation/retrieval → request 2, clarification and failure branches, sanitized evidence trace. |
| HTTP boundary | `backend/app/chat_routes.py`: proposed `POST /api/chat`, small validated dispatch; register in `main.py`. No public raw-SQL execution route. |
| View | `frontend/src/components/HotelChat.vue`, optionally `ChatEvidence.vue`, plus `frontend/src/composables/useChat.js`; mount in `App.vue` without rewriting discovery. |
| Verification | `backend/tests/test_chat_queries.py`, `test_chat_provider.py`, `test_chat.py`; `data/chatbot-fixture.json`; browser checks using the existing harness. |
| Evidence | Research/design/verification/demo/AI notes under `docs/`; selected actual prompts under `prompts/`; preserve Part 1 report before updating `report.md`; update README when setup/architecture actually changes. |

Proposed request input is a bounded natural-language `question`. Initial design
can remain single-turn: ask for a complete clarified question when dates, ZIP,
room count or budget meaning are ambiguous. Do not silently infer missing
dates. Define concrete limits and error contracts before implementation.

## Full-credit acceptance checks

- [ ] **Research and early design:** dated official provider research and an
  image/link to a chatbot mockup created before implementation; preserve original
  design and explain later changes. Select one permitted provider: paid OpenAI
  API, Gemini API, or class-configured Nemotron through OpenRouter. Provider,
  exact model, availability, limits and credentials are not established by this
  audit; research them next. Never silently choose a replacement model.
- [ ] **First model request:** original question plus actual relevant schema
  and query rules yields a validated SQL/parameters proposal, or an explicit
  clarification. A hardcoded query alone does not meet the required workflow.
- [ ] **Checked local retrieval:** only the three approved tables/columns can
  be read. Treat question, proposed SQL and database text as untrusted. Use
  `mode=ro`, `query_only`, a default-deny SQLite authorizer, allowed functions,
  single-statement execution, disabled extension loading, execution deadline /
  progress limits, row and byte limits. Reject writes, schema changes,
  ATTACH/DETACH, model PRAGMAs, unauthorized reads/functions and multiple
  statements. A SELECT prefix/regex alone is insufficient. Enforce bounds
  independently of the model's LIMIT and distinguish truncation from completeness.
- [ ] **Correct stay semantics:** check-in inclusive, checkout exclusive;
  validate date order, count every requested night, require enough rooms on all
  nights and sum actual integer cents. Missing nights are insufficient data.
  Distinguish total versus nightly budgets and per-room versus multi-room totals.
  Avoid duplicate aggregation through location joins. Read-only safety alone
  does not establish semantic correctness; test and check these invariants.
- [ ] **Second model request:** original question plus limited actual retrieved
  records produces an answer grounded only in those records. Include an empty
  result when appropriate; no invented hotels, rates, vacancies, ratings or
  booking confirmations. Record data must not override model instructions.
- [ ] **Actionable Vue answer:** show hotel identity, dates, simulated costs,
  availability and recommendation reason, or clear no-match/insufficient-data
  feedback. Label simulated course data and limited saved inventory visibly.
  Keyboard-accessible input/send, loading and failures; prevent stale/duplicate
  submissions; safely render text without raw model HTML.
- [ ] **Evidence trace:** expandable view/report can show original question,
  SQL/parameters, validation status, retrieved records, displayed answer,
  exact provider/model and result limits; demonstrate both model requests in
  order without exposing keys, raw sensitive provider errors or credentials.
- [ ] **Failure cases:** missing configuration, invalid proposal, no matches,
  incomplete nights, malformed provider output, timeout, rate/quota limit and
  second-request failure have safe distinct handling. Label mocks clearly;
  never present a mock fallback as a successful live model call.
- [ ] **Regression and persistence:** duplicate save, removal, browser/backend
  restart, edited demo values, local-first behavior, sample Boston/Aspen and
  booking workflows remain correct. Frozen ZIP/list/map behavior and attribution
  remain intact. Compare database schemas/rows around rejected-query tests in an
  isolated database; never attack or reset the student's database to test safety.
- [ ] **Submission:** report and recording show a successful live full workflow,
  no-match/insufficient-data case and rejected-query evidence with expected versus
  observed checks. Link repeatable fixed JSON sample, startup/config instructions,
  repository and assessed commit, research/mockup, video and AI evidence with a
  genuine failed/revised approach. Verify instructor access without additional
  requests; mark pending evidence honestly. Earlier Part 1 video is not a
  substitute for this new demonstration.

Keep provider requests/credentials exclusively on the backend in local ignored
`.env`; no `VITE_*` secret, remote SQLite access, or tool that can make bookings.
Send only necessary question/schema/hotel records; exclude sample user/booking
tables. Inspect secret tracking without printing secret values.

## Staged implementation and exit checks

1. **Provider research:** student selects one provider; verify official API,
   exact model and limits (request class configuration if Nemotron is chosen).
   Write `docs/chatbot-research.md`, configuration and dependency decision.
2. **Early mockup and contract:** save original desktop/mobile state boards,
   define request/response/trace/error contracts, concrete limits, supported stay
   semantics and SQL validation strategy. No implementation before mockup.
3. **Read-only executor:** implement contracts and restricted SQLite executor;
   isolated tests prove allowed joins/aggregations, rejection and unchanged data.
4. **Two-request backend:** selected provider adapter and controller; mocked
   tests assert payloads, ordering, original question/records in request 2,
   semantic correctness and safe failures; add thin route.
5. **Vue interface:** implement mockup, state handling, simulated-data labeling
   and evidence panel. Lint/build and keyboard/mobile/browser checks.
6. **Verification:** dedicated labeled JSON fixture with varied prices, absent
   and unavailable nights, leading-zero ZIP and multiple associations. Run full
   regression suite and persistence checks in isolation; then a small deliberate
   live-provider demonstration using saved data. Capture exact expected/observed
   evidence; never exhaust quotas to test limits.
7. **Report and demonstration:** preserve Part 1 report, assemble actual traces,
   recording script/video, research/mockup, AI log and repeat instructions.
   Review complete diff and manually test Boston/Aspen before any authorized Git
   checkpoint. Publication/submission requires its own user instruction.

## Audit verification — October 8, 2026

| Check | Observed |
| --- | --- |
| `backend/.venv/bin/python -m pytest backend/tests -q` | 166 passed in 0.70s. Existing regression tests, not chatbot coverage. |
| `npm run lint` in frontend | Passed, no reported warnings. |
| `npm run build` in frontend | Passed, 26 modules, 288 ms. |
| `backend/.venv/bin/python -m pip check` | No broken requirements found. |
| `npm ls --depth=0 --prefix frontend` and direct lock/install comparison | Passed; all eight direct package versions match lock. |
| Read-only SQLite schema/count/night inspection | Counts and values above; integrity `ok`, zero foreign-key violations. |
| Database SHA-256 before/after inspection | Unchanged: `e7d83319033ee45c131fd8a9722ca492a1bc65638aa4b4b01d23ef4a29952c16`. |
| Secret/runtime tracking | `.env` and database ignored; neither tracked; no credential contents displayed. |

No fresh browser, live Geoapify/LLM, restart-persistence, video, or instructor
access check was performed in this planning step. Prior browser evidence remains
historical. README, application source, manifests, lockfile and database were not
edited; generated ignored build/test outputs may be refreshed by checks.
