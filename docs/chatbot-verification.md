# Chatbot verification — October 8, 2026

**Controlled verification passed. Live OpenAI verification is incomplete: no
OPENAI_API_KEY is configured.** No application or test source, dependency,
student record, original mockup or historical screenshot was changed. Only new
verification documentation/harness/evidence was written. No commit or push.

Run began **10:48:59 EDT (14:48:59 UTC)**; timestamps are retained in the
[evidence](chatbot-verification-evidence/preservation.json). Working branch:
`assignment2_part2_in_class`. Earlier uncommitted work was preserved.

## Fixed fixture and isolated loading

Reused [data/chatbot-fixture.json](../data/chatbot-fixture.json), unchanged and
explicitly labeled simulated course data. Dates below are October 2026; prices
are cents per room per night.

| Hotel | ZIP associations | Oct 10 | Oct 11 | Oct 12 |
| --- | --- | --- | --- | --- |
| Example Birch House | 06109, 06108 | 12000 / 3 rooms | 14000 / 2 rooms | 99000 / 0 rooms |
| Example River Inn | 06109 | 14000 / 5 rooms | 16000 / 5 rooms | missing |
| Example Unavailable | 06109 | 10000 / 0 rooms | 10000 / 5 rooms | missing |
| Example Missing Night | 06109 | 9000 / 9 rooms | missing | missing |

To load safely, from the repository root run:

```sh
backend/.venv/bin/python docs/browser-checks/chatbot-verification.py
```

This [verification-only loader](browser-checks/chatbot-verification.py) creates a
**new randomly named directory** under ignored `.capture/`, asserts its database
does not exist, initializes sample seeds there, and loads this JSON into the
three saved-hotel tables. It never loads the fixture into `data/wayfinder.sqlite3`.
It records the new path in `.capture/chatbot-verification/runtime.json`, captures
three mocked HTTP workflows, and asserts every table/schema and the database
hash remain unchanged during each workflow. Repeating it creates another isolated
database. This path must be used for any mutation/browser regression below.

## Expected versus observed: retrieval and two-model workflow

Fresh [success trace](chatbot-verification-evidence/mock-success.json),
[no-match trace](chatbot-verification-evidence/mock-no-match.json), and
[insufficient-data trace](chatbot-verification-evidence/mock-insufficient.json)
contain both actual serialized request bodies, the intervening real isolated
SQLite retrieval, and the returned answer/evidence. Only HTTP responses are
mocked; these are **not live OpenAI calls**. No authorization headers are captured.

| Check | Expected | Observed |
| --- | --- | --- |
| 06109, Oct 10–12, 1 room, $350 total | Birch $260, River $300; Birch cheapest | HTTP 200 answer; 26000 and 30000 cents, answer recommends Birch at $260; two mocked requests |
| Checkout exclusion | Ignore Birch's $990 / zero-room Oct 12 checkout row | Seven retrieved rows; no Oct 12 row; Birch remains eligible |
| Rooms every night | Birch minimum 2, River minimum 5; unavailable hotel fails | Exact minima; demo-full ineligible despite 5 rooms on second night |
| Missing night | No full total or assumed availability for demo-gap | Oct 11 listed missing; total null; ineligible |
| Multiple ZIP associations | Birch totals must not double | Still 26000 cents over two nights; leading-zero ZIP retained |
| 06108, same stay, $250 total | No matching hotels | HTTP 200 no_matches after two mocked requests; truthful budget explanation |
| ZIP 00000, same stay | No saved candidates | Unit test returns no_matches after two calls |
| 06109, Oct 11–14 | Missing coverage means insufficient data | Fresh trace: HTTP 200 insufficient_data, two requests, incomplete stays identified |
| Nightly vs total / multiple rooms | Every nightly rate checked; two Birch rooms cost $520 | Tests pass $150/night/room case; $500 total fails; $520 printed for qualifying two-room case |
| Ambiguous question | Ask for missing intent; no invented dates/rooms/budget | 11 ambiguous/invalid intent cases + explicit model clarification pass; one call, retrieval not reached |
| First request contents | Original question, schema and query rules; strict output contract | HTTP transport test and trace pass; payload contains original question, instructions contain relevant schema |
| Second request contents | Same question plus actual bounded retrieved rows and checked facts | Captured second payload exactly matches evidence records; two calls required |
| Answer factual agreement | Only verified eligible hotel/cost/date/room facts | Exact expected facts; tests reject fabricated IDs, wrong lowest-total/more-rooms reasons, unavailable recommendations and conflicting status |
| Record instruction injection | Text remains untrusted data | Test passes; record content stays out of trusted instructions; browser HTML payload remains literal text |

The backend's constrained second response chooses IDs/reasons; Python renders
verified factual text. This pass confirms that documented design, not arbitrary
free-form model prose accuracy.

## Expected versus observed: rejection and provider failures

All cases below ran in the fresh full suite. The [JUnit results](chatbot-verification-evidence/backend.xml)
retain every parameterized case; [test output](chatbot-verification-evidence/backend.log)
records **341 passed in 1.41s**. Ninety query-boundary tests use isolated snapshots.

| Input | Expected | Observed |
| --- | --- | --- |
| Writes, schema changes, ATTACH/DETACH, model PRAGMAs | Reject without changes | Passed; native authorization/read-only layers plus proposal contract deny them |
| Assignment 1 tables, schema reads, forbidden columns/functions | Deny all unauthorized access | Passed, including reads hidden in predicates/subqueries |
| Multiple statements | Reject before original query executes | Passed; original-statement trace assertions pass |
| Large cross join/count, excessive rows/bytes, supplied huge or absent LIMIT | Bound work and results independently; no partial answer | Passed with safe query_limit/rejection; 50-row, 24-KiB, VM/deadline limits exercised |
| Invalid proposal types/extra fields | Fail before opening a connection | Passed |
| Rejected attempt preservation | All schemas/table contents and file hash unchanged | Fixture teardown assertions passed after malicious cases |
| Malformed provider output | Safe error, no guessed answer | Missing/wrong/nonfinite/duplicate/nested/refused/incomplete response cases pass |
| Timeout/deadline | Safe provider_timeout; no fallback | Transport/controller tests pass; browser 50-second controlled-clock case passes |
| Simulated quota/rate limit | Safe 503; bounded numeric retry guidance where applicable | Provider/controller tests pass; browser cooldown survives editing |
| Second-call failure | No answer; retain safe retrieval evidence and failed stage | Mock timeout 504, quota 503, malformed 502 cases pass at answer_model |
| Wrong model / redirect | Never silently substitute model or forward key to redirect | Provider tests pass |

Timeout tests use simulated errors/controlled clocks; they do not establish live
provider latency. SQLite deadlines remain cooperative, not a process sandbox.

## Frontend and existing workflow regression

Fresh lint: **passed, no warnings/errors**. Fresh production build: **passed,
33 modules, 178ms**. Existing Playwright runtime and Chrome were reused; no package
was installed. Tests used localhost ports 8010/5173 and the new isolated database.

| Check | Expected | Observed |
| --- | --- | --- |
| Chat keyboard/states | Newline, Tab/Enter submit, retained focus, loading, clarification, no-match, insufficient, failure | All pass; model output rendered literally |
| Duplicate/stale requests | Block duplicate Send; editing invalidates pending reply | Passed, including next request success |
| Evidence/mobile | Readable question, SQL, parameters, records/model; no horizontal overflow | Passed at 390px and 320px including expanded evidence |
| Sample search | Boston four joined rows; Aspen no-results | Passed repeatedly using actual isolated backend |
| Frozen Part 1 | Leading-zero ZIP, invalid/empty/unresolved/error/loading, synchronized keyboard list/map, attribution, no request on selection, limits/tile failure | 16 adapted historical browser scenarios passed; backend regressions also pass |
| Local-first | Saved ZIP never calls discovery; read failure must not fall back | Passed, including after service restart |
| Duplicate saves | Preserve IDs and edited nightly values, no duplicate rows | API repeat-save tests plus explicit snapshot comparison passed; edited 12345-cent night retained |
| Add/remove/refresh | Pending/failure/success feedback and persistent removal | Existing local-hotels browser suite passed |
| Booking regression | Create unique IDs; cancel retaining record; delete confirmation; survive refresh | Passed on isolated sample seeds; original records untouched |
| Restart persistence | No reseeding; saved/removed hotels and cancelled/deleted bookings retain state | Both servers stopped/restarted; every isolated table/schema and byte hash identical; browser confirms $123.45 edited rate, cancelled booking and absent deleted booking |

Fresh [desktop](chatbot-verification-evidence/desktop.png),
[mobile](chatbot-verification-evidence/mobile.png), and
[no-match](chatbot-verification-evidence/no-match.png) screenshots are explicitly
labeled controlled mocks. They do not replace a live recorded demonstration.

Console/API inspection: chatbot cases recorded two expected 503s (mock rate limit
and deliberately unconfigured backend); local cases recorded three expected
503s (read/save/remove failures). Discovery recorded expected 404, 503 and aborted
network/tile failures. No uncaught JavaScript errors. Booking console/API/page
errors were empty; its DELETE logged net::ERR_ABORTED after a successful 204,
and the record remained absent after refresh/restart. Restart checks had zero
console, API or page errors. See diagnostic JSONs and browser results in
`docs/chatbot-verification-evidence/`; errors are not hidden by a blanket
“console clean” claim.

## Live-provider verification: incomplete

At 10:48:59 EDT, the normal backend config loader reported only the boolean
`openai_configured: false`; `.env` values were never displayed. Configured model
identifier is `gpt-4.1-mini-2025-04-14`. **Zero live requests were made.**
No live successful workflow or live no-match/insufficient capture is claimed.

Read-only inspection of actual saved data found Comfort Inn, ZIP 06109, five
nights Oct 10–14. Oct 10 is 20000 cents/15 rooms; following nights 10000/20.
For one room Oct 10–12, expected total is $300 and minimum rooms 15. These are
local-data expectations, not observed live model results. See
[live status](chatbot-verification-evidence/live-status.json).

Focused follow-up prompt:

> After I privately configure OPENAI_API_KEY in the ignored root .env and restart
> this project's backend, perform a verification-only live OpenAI check using
> gpt-4.1-mini-2025-04-14 and actual saved hotels. Ask “06109, 2026-10-10 to
> 2026-10-12, one room, $350 total” and then the same stay with “$1 total”. Capture
> both model stages, intervening SQL/parameters/records, displayed answer and
> expected-versus-observed facts. Never print credentials, mutate records, switch
> models/providers or substitute mock evidence. Stop and report safe service errors.

## Exact commands and harness adaptations

Run from the project root unless indicated:

```sh
backend/.venv/bin/python -m pytest backend/tests -q --junitxml=docs/chatbot-verification-evidence/backend.xml
npm --prefix frontend run lint
npm --prefix frontend run build
backend/.venv/bin/python docs/browser-checks/chatbot-verification.py
```

Isolated backend startup, repeated unchanged for the restart check:

```sh
backend/.venv/bin/python -c 'import json,os; from pathlib import Path; from backend.app import database; database.DATABASE=Path(json.loads(Path(".capture/chatbot-verification/runtime.json").read_text())["database"]); os.environ["OPENAI_API_KEY"]=""; from backend.app.main import app; import uvicorn; uvicorn.run(app,host="127.0.0.1",port=8010)'
```

Frontend startup from `frontend/`, also repeated for restart:

```sh
npm run dev -- --host 127.0.0.1
```

Verification commands (temporary copies preserve historical harness outputs):

```sh
python3 .capture/chatbot-verification/adapt.py
node .capture/chatbot-verification/chatbot.cjs
LOCAL_TEST_BACKEND=http://127.0.0.1:8010 node .capture/chatbot-verification/local-hotels.cjs
node .capture/chatbot-verification/discovery.cjs
node .capture/chatbot-verification/smoke-bookings.cjs
PYTHONPATH=. backend/.venv/bin/python .capture/chatbot-verification/persistence.py
# Stop/restart both owned services with the commands above.
node .capture/chatbot-verification/restart.cjs
```

Adapter, persistence setup and restart browser command text are retained as
`.txt` files in the evidence directory. Adaptations redirect output paths and
add console/API diagnostics. The historical discovery harness also needs an
empty local-first response and selectors restricted to buttons with
`aria-pressed`, since Add/Remove buttons now share each list item.

Initial adapter attempt returned an incomplete local response and timed out
waiting for a hotel. **Harness failure, not an application failure.** Corrected
only the disposable adapter to return:
`{source:'local', postcode:<requested ZIP>, hotels:[], count:0, saved_ids:[], center:null}`.
The rerun passed all 16 cases. The retained adapt.py.txt records the original
attempt; apply this response correction before reproducing that historical
script. No application repair was performed or is indicated by passing tests.

If maintaining the historical browser script later, focused repair prompt:

> Update only the discovery verification harness to return the current LocalResults
> shape for its empty-local mock, scope selection to aria-pressed buttons, and
> parameterize fresh output paths. Preserve application source and earlier evidence.
> Rerun all 16 controlled scenarios and propagate nonzero script exit codes.

## Preservation and untested areas

Before/after hashes confirm every snapshotted backend/frontend/data file,
including manifests, lockfiles, fixture and real SQLite, remained unchanged.
Real database SHA256:
`e7d83319033ee45c131fd8a9722ca492a1bc65638aa4b4b01d23ef4a29952c16`.
No listeners occupied 8010/5173 at start. Only this check's server sessions were
started, restarted, then stopped. No unrelated service was stopped.

Not verified: live OpenAI credentials/access/billing/latency or model compliance;
fresh real Geoapify calls; screen-reader speech; browsers beyond Chrome;
instructor access; final report/recorded demonstration. Controlled tests do not
prove arbitrary natural-language semantic correctness. No source-code changes
or dependency repairs are authorized by this verification-only pass.
