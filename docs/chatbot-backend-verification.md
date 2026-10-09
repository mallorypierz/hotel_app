# Chatbot backend — implementation and verification

October 8, 2026 (Eastern). **Backend implemented; live OpenAI calls unverified.**
The key-configuration check returned false, without printing or editing `.env`.
All model calls in the tests and linked trace are labeled mocks. No network
request, billing operation, real database mutation or frontend edit was made.

## Implemented workflow and boundaries

`POST /api/chat` accepts `{"question":"..."}`. Request models reject extras,
empty/whitespace input, NULs and more than 2,000 characters/8,000 UTF-8 bytes.
A chat-only ASGI middleware caps the entire HTTP body at 16 KiB before JSON
parsing, including chunked requests. Existing routes are not subject to that cap.

1. OpenAI Responses request 1 sends the original question as untrusted user data,
   the relevant actual schema and strict query instructions as trusted instructions,
   and a strict JSON schema. The pinned model is `gpt-4.1-mini-2025-04-14`.
2. The model returns clarification or a typed stay intent plus SQL and bound
   parameters. Missing/unsupported intent produces clarification before retrieval.
   The backend independently extracts explicit dates/ZIP/rooms/budget from the
   question and rejects a conflicting model interpretation.
3. The existing [read-only executor](chatbot-retrieval-verification.md) validates
   and executes the **model's SQL** locally. An independent trusted read checks
   the returned raw hotel/night records against all saved candidates for that
   ZIP/date range. An omission, duplicate, fabricated value or unexpected column
   fails closed; the trusted query never silently substitutes for rejected SQL.
4. Python checks every requested night, rooms on each night, actual summed cents
   and budget. No incomplete stay receives a full total. It multiplies the sum
   by requested rooms for total-stay cost; a per-night/per-room budget is checked
   against every night's per-room rate. Checkout is excluded. ZIP EXISTS avoids
   multiplying nightly records through multiple location associations.
5. OpenAI request 2 receives the original question again, bounded actual records,
   checked stay facts, status, completeness metadata and simulated-data label.
   Records are explicitly untrusted data, never instruction text.
6. The second model returns a structured answer: status and recommended hotel IDs
   with factual reasons (`lowest_total`, `more_rooms`, `meets_requirements`).
   The backend rejects unknown/unavailable hotels, mismatched status, duplicate
   recommendations and incorrect comparative reasons. It renders the model's
   validated selections with actual dates, costs and rooms into the `answer` string.

This intentionally uses a constrained LLM-generated recommendation instead of
accepting unrestricted factual prose. Python supplies the verified numeric text;
the LLM chooses hotels and reasons. There is **no mock or template-only fallback**
when either model call fails: the second successful model decision is required
for an answer/no-match/insufficient-data response. Clarifications can come from
the model or from the backend's independent ambiguity guard. This design decision
is recorded in [the design change log](chatbot-design-changes.md).

## Files / MVC

| Responsibility | Files |
| --- | --- |
| Input, model-output and response contracts | `backend/app/chat_contracts.py`, existing `chat_models.py` |
| Two-stage controller and evidence | `backend/app/chat_controller.py` |
| Independent intent/record checks, stay calculations, factual rendering | `backend/app/chat_stays.py` |
| Trusted prompts | `backend/app/chat_prompts.py` |
| HTTPS transport and safe provider errors | `backend/app/llm_provider.py` |
| Thin FastAPI adapter / request-byte bound | `backend/app/chat_routes.py`, `chat_http.py`; registration in `main.py` |
| Backend-only settings | `backend/app/config.py` |
| Isolated tests / repeatable sample | `backend/tests/test_chat.py`, `test_chat_provider.py`, `data/chatbot-fixture.json` |

No booking mutation, remote SQLite access, new dependencies, authentication,
payments, conversation storage, fallback provider or automatic model switching.
The separate sample/local save controllers and frozen discovery routes remain.

## Response and safe failures

Successful HTTP 200 responses contain `status`, `answer`, `simulated_label`,
checked `hotels`, and `evidence`. Status is answer, no_matches, insufficient_data
or clarification. Evidence includes the original question, exact provider/model,
normalized intent when validated, actual proposed SQL/parameters, validation
outcome, raw retrieved records, row/byte limits, result count/size and completeness,
and each model call's stage/status/response ID/token usage when available.
`truncated: false` means no partial rows were returned; overflow is an error.
Completeness concerns the saved ZIP/date subset, not real-world hotel coverage.

Model/retrieval failures return a fixed safe code/message, failed stage and bounded
evidence in HTTP `detail`. Never expose raw provider messages, headers, API key,
SQLite exceptions or filesystem paths. Earlier-stage evidence remains available
if the second call fails; no answer is manufactured. Invalid user input is 422;
oversized bodies are 413. Configuration/access/quota/rate/storage errors are 503,
model timeout 504, other provider/validation/retrieval errors 502. Temporary
limits carry a validated numeric Retry-After when supplied; quota errors do not
pretend waiting alone will fix billing/access.

Transport uses standard-library urllib/SSL, POST to the fixed OpenAI endpoint,
Bearer authentication, `store:false`, `stream:false`, strict output schemas and
no retries. Redirects are disabled so credentials cannot move to another host.
It rejects incomplete/refused/malformed/wrong-model outputs, duplicate JSON keys,
nonfinite JSON and excessive nesting, rather than guessing a usable response.

Bounds: up to 1,800 output tokens per call; 48 KiB encoded provider request;
256 KiB provider response; 20-second per-call transport setting within a
45-second overall controller budget; 96 KiB final serialized chat response.
SQLite's existing 50-row/24-KiB/work limits remain. Read/deadline checks are
cooperative: socket operations or OS I/O are not forcibly preempted at an exact
wall-clock instant. Timed-out provider processing may still incur API usage.

## Supported question scope and limitations

For the initial backend, state one five-digit ZIP, two dates in check-in/checkout
order, an explicit year, 1–10 rooms and a 1–14-night stay. Supported dates are
ISO or written month/day (a single explicit shared year can apply to both).
Use dollar amounts such as `$350 total` (all rooms) or `$150 per night per room`.
For one room, `$150 per night` is unambiguous. No budget is allowed when none is
requested; vague affordability, bare amounts without currency, ambiguous budget
scope, invalid/missing dates and unsupported currencies request clarification.
This conservative parser is not a general natural-language date engine.

The model must retrieve exactly hotel_id, name, stay_date, nightly_rate_cents and
rooms_available for all ZIP candidates, with a date-filtered LEFT JOIN and no
price/availability filter. This preserves evidence of missing nights. Safe
aggregate-only SQL used in the early mockup is not accepted by this controller:
Python aggregates verified raw nights. Equivalent complete raw-row queries can
pass; incorrect/incomplete proposals fail instead of being silently rewritten.
If more than 50 rows/24 KiB would be needed, narrow the stay; automatic pagination
or silently selecting a few hotels is not implemented.

The two local reads are separate read-only connections. Concurrent local edits
may cause record-verification rejection; retry safely. No atomic multi-query
snapshot or complete semantic understanding of arbitrary requests is claimed.
Structured factual reasons are deliberately limited; arbitrary free-form
recommendation prose and unsupported search criteria are outside this version.

## Verification and AutoLoop record

Fixture: [labeled JSON sample](../data/chatbot-fixture.json). It contains four
fictional hotels, a leading-zero ZIP, two ZIP associations for one hotel, varying
nightly rates, an unavailable night, a missing night and an expensive unavailable
checkout night. Tests seed only disposable SQLite databases; after each fixture
test, all table contents/schema and file bytes must match its initial snapshot.

| Check | Expected | Observed |
| --- | --- | --- |
| 06109, Oct 10–12 2026, 1 room, $350 total | Two model calls around actual local SQL; Birch $260, minimum 2 rooms; checkout omitted | Pass; trace below |
| Same stay, 06108, $250 total | No matches; second request receives records/status | Pass |
| No saved hotels in 00000 | Empty records with honest no-match answer after call 2 | Pass |
| Missing requested nightly rows | Null full-stay total; insufficient_data | Pass |
| Sold-out requested night | Hotel not eligible | Pass |
| 2 rooms, $500 total / $150 per night per room | Birch fails $500 total but qualifies per-night/per-room; actual total $520 | Pass |
| Multiple ZIP associations | No duplicated nights or cost | Pass |
| Missing/invalid dates/rooms, vague/negative/unsupported budget | Clarification, no SQL/second request | Pass |
| Model changes ZIP/date/budget | Invalid model response, no SQL | Pass |
| Disallowed SQL, LIMIT-based omissions, fabricated rates, missing-night omissions | Reject; no second request | Pass |
| Model recommends unknown, unavailable or incorrectly cheapest hotel | Reject answer; preserve retrieval evidence | Pass |
| Record containing instruction-like text | Kept only in data payload, never trusted instructions | Pass with mocks; not a live injection evaluation |
| Missing config, wrong model, timeout, quota/rate limits, malformed/refused/incomplete output at either stage | Safe errors, no retries/fallback, correct failed stage | Pass |
| Oversized whole/chunked HTTP body and deep malformed JSON | Bounded safe rejection | Pass |
| Existing sample/local/discovery regression suite | Preserve behavior | Pass |

Initial targeted query/backend/provider run: **168 passed in 1.09s**; initial
full suite **334 passed in 1.40s**. Review added HTTP-body/deep-JSON and record
injection checks. That run was **82 passed / 1 teardown error in 0.81s**: the
test edited/restored a fixture name after its byte snapshot, changing SQLite
file metadata despite equal logical records. **Correction cycle 1** moved the
malicious test name into fixture creation before snapshot. Rerun: **82 passed
in 0.57s**, full suite **338 passed in 1.45s**. Review also added three ambiguity
guards/tests for bare-currency, negative and mixed-currency budgets and corrected
recommendation grammar. Final full suite: **341 passed in 1.37s**.

Commands:

```sh
backend/.venv/bin/python -m pytest backend/tests/test_chat.py backend/tests/test_chat_provider.py backend/tests/test_chat_queries.py -q
backend/.venv/bin/python -m pytest backend/tests -q
```

[Full labeled mocked trace](chatbot-backend-mock-trace.json) records question,
both mocked model input/output envelopes, proposed SQL, actual isolated retrieval,
returned answer and expected/observed total. Mock token counts and IDs are labeled;
they are not measured OpenAI usage. The extra trace capture passed with its
isolated database bytes unchanged. This is backend output, not a frontend demo.

The real local database SHA-256 remains
`e7d83319033ee45c131fd8a9722ca492a1bc65638aa4b4b01d23ef4a29952c16`.
No credentials were shown or written; only the configured boolean was checked.
No frontend tests/build/browser, service restart, recording, commit or push in
this step. The full backend suite is fresh; old browser checks remain historical.

## Real-call verification — separate and pending

**Not performed: backend OPENAI_API_KEY is absent.** Privately add the key to
the existing ignored root `.env`, preserving Geoapify settings; never paste it
into chat. Restart this project's backend after configuration. Model/project
access, billing, live schema acceptance, latency and real recommendation quality
remain unverified until then. Use the README's local request example for one
deliberate question, capture both actual response IDs/usage and compare actual
records to the answer. Do not relabel the mock trace as live or claim the required
full-credit live demonstration is complete. Vue integration and recording remain.

An additional local ASGI call using the actual current (unconfigured) settings
returned HTTP 503 / `unconfigured`, with no external request. Final Python syntax,
fixture/trace JSON, local documentation links, `git diff --check` and real
database hash checks passed. This confirms safe missing-configuration behavior,
not live OpenAI connectivity.
