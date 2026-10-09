# Live OpenAI follow-up — October 8, 2026

After the student privately configured OPENAI_API_KEY, restarted the backend,
and reported purchasing credits, an authorized live POST /api/chat was tested
against actual saved hotel records. OpenAI remains the sole provider; model
remains gpt-4.1-mini-2025-04-14. No credential values were displayed or saved.

First live attempt: query_model completed, but the proposed SQL placed WHERE
EXISTS before LEFT JOIN. The unchanged validator rejected it at retrieval with
HTTP 502/query_rejected; no answer or retrieved records were returned. Added a
valid clause-order/query-shape example and binding order to QUERY_RULES.

Second live attempt: HTTP 200 clarification incorrectly asked to reconfirm room
count/year despite “one room” and two ISO dates. Its actual response is saved in
[unnecessary clarification](chatbot-verification-evidence/live-openai-unnecessary-clarification.json).
Clarified in the trusted prompt that words one through ten are explicit counts
and ISO dates already specify year/stay length. No backend intent or SQL guard
was relaxed; no replacement SQL or mock fallback was added.

Third live attempt: **HTTP 200 answer, both actual OpenAI requests completed**.
[Sanitized full live backend response](chatbot-verification-evidence/live-openai-success-attempt.json)
contains exact question, proposed SQL/parameters, validation, retrieved records,
answer, model identifiers, response IDs and actual token counts. It is live
backend evidence, not a recording or a claim of a fresh frontend screenshot.

Question: “Which saved hotels in 06109 have one room from 2026-10-10 to
2026-10-12 for $350 total or less?”

Expected versus observed: Comfort Inn Oct 10 20000 cents/15 rooms plus Oct 11
10000 cents/20 rooms = 30000 cents ($300) for one room; minimum rooms 15;
checkout Oct 12 excluded. Observed records, checked facts and answer agree.
Validation passed_read_only_and_record_verification; two rows; no truncation.
Total recorded tokens for successful calls: 1132 + 956 = 2088. Earlier failed/
clarification requests also used provider tokens; no exact bill is inferred.

Only trusted query instructions changed; no dependency/provider/model changes.
Real SQLite hash before and after remains
 e7d83319033ee45c131fd8a9722ca492a1bc65638aa4b4b01d23ef4a29952c16.
Services remain running at the student's request. The prior report's absent-key/
no-live-success statements are historical and superseded by this follow-up.
Live no-match/insufficient-data capture, video, assessed commit and instructor
access remain pending. A single successful request does not guarantee all
future natural-language proposals will be valid; rejection remains fail-closed.

## October 9 — natural date range and live frontend verification

The student's visible question was “Are there 2 rooms available for October 11th
to 12th 2026 in zip code 06109?” The backend's independent parser did not support
ordinal dates with a shared month, so it returned clarification before retrieval.
The generic evidence text “No SQL proposal received” obscured that cause.

Expanded only explicitly shared month/year ranges and accepted ordinal suffixes
in named dates. Missing years, reversed/invalid dates and excessive stays still
require clarification. Added eight regression cases, including two-call retrieval,
checkout exclusion, two-room totals and missing-night behavior. ChatEvidence now
explains that clarification pauses the query; SQL validation remains unchanged.

Observed the original browser state, reloaded the updated Vue app, and submitted
the exact original question through the real UI (no interception/mocks). Both
OpenAI stages completed with gpt-4.1-mini-2025-04-14. Expanded evidence showed
parameters 2026-10-11, 2026-10-12, 06109, passed read-only/record verification,
and one actual saved Comfort Inn night: 10000 cents, 20 rooms. Expected and
observed total: 10000 × 2 rooms × 1 stored night = 20000 cents ($200); checkout
excluded. The displayed answer/cards agreed. See [live screenshot](chatbot-verification-evidence/live-ordinal-question-2026-10-09.jpg)
and [visible UI transcript](chatbot-verification-evidence/live-ordinal-question-2026-10-09.txt).

Fresh checks: 349 backend tests passed in 1.83s; frontend lint clean; build passed
33 modules in 213ms. No dependencies, stored data or provider/model changed.
This is a live frontend success capture, not a screen-recorded video or a live
negative-case demonstration. Services remain running for the student.
