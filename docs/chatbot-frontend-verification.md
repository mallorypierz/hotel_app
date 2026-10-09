# Chatbot frontend verification — October 8, 2026

Acceptance: the approved design is integrated into Vue, calling only the existing
FastAPI chat route, safely rendering checked answers and read-only evidence,
with accessible states, duplicate/stale protection and preserved hotel workflows.
No dependencies, backend implementation or real database records changed.

## Implementation

`frontend/src/components/HotelChat.vue` owns form/layout and state presentation;
`ChatHotelCards.vue` renders backend facts and `ChatEvidence.vue` renders the trace.
`frontend/src/composables/useChat.js` owns POST /api/chat, abort/version handling,
50-second browser deadline, bounded response parsing and Retry-After cooldown.
The frontend performs no SQL execution, SQL generation, provider request or
credential lookup. Vue interpolation renders answer/name/SQL strings literally.
No raw HTML, Markdown-to-HTML conversion, booking action or local chat persistence.
The view formats integer cents only; the backend calculates stay facts.

## Checks and observed results

| Check | Expected | Observed |
| --- | --- | --- |
| Backend regression | Existing test suite remains passing | 341 passed in 1.48s |
| Frontend lint | No errors or warnings | Passed after formatting new components |
| Frontend build | Production bundle builds | Passed, 33 modules, 201ms |
| Keyboard | Enter newline, Tab/Enter Send, preserve focus, native expandable evidence | Passed; Edit focuses question |
| Successful answer | Fixture identity/dates/$260 total/minimum 2 rooms/recommendation reason and limitations | Passed; data comes from labeled backend mock trace |
| Loading/duplicates/stale | One submission, editing invalidates old response | Passed; next question succeeds |
| Other states | Clarification, no matches, insufficient data and persistent label | Passed |
| Failure | Safe error, respect retry delay through edits, malformed response | Passed; two-second controlled cooldown |
| Timeout | End loading with safe message | Passed at 50 seconds using Playwright controlled clock |
| Injection | HTML payloads remain text | Passed for answer/name/SQL; no injected image or script effect |
| Evidence | Question, SQL/parameters, validation, records, row/byte/truncation metadata, provider/model | Passed |
| Mobile | Readable stacked layout with no page overflow | Passed at 390px and 320px, including expanded evidence |
| Browser isolation | No direct provider calls or uncaught JS errors | Zero observed |
| Actual route failure | No configured key yields safe UI failure | Passed with test server OPENAI_API_KEY explicitly empty |
| Discovery/storage regression | Local-first, no fallback on storage error, save/remove states, IDs across ZIPs, refresh, five nights, synchronized keyboard map/list | Existing local-hotels.cjs passed on isolated database; controlled discovery responses |
| Sample search | Boston four rows / Aspen no results | Passed against actual isolated backend |
| Booking regression | Create unique IDs, cancel retaining record, delete confirmation, refresh persistence | Existing booking harness passed on isolated database; no console/page/API errors. One DELETE request logged ERR_ABORTED after its successful 204 response; the record was absent on refresh. No service-restart persistence check repeated. |

Browser cases: [script](browser-checks/chatbot.cjs),
[labeled results](browser-checks/chatbot-results.json),
[desktop screenshot](chatbot-ui-desktop-v2.png),
[mobile screenshot](chatbot-ui-mobile-v2.png). Both screenshots visually inspected.
They are controlled mock-response screenshots, **not live OpenAI evidence**.
The existing booking harness was copied to ignored `.capture/chatbot-ui/` solely
to redirect its historical result/screenshots; original evidence was preserved.

## AutoLoop corrections

Initial lint had 70 formatting warnings, zero errors; ESLint's existing fixer
resolved them. Initial browser check exposed native disabled Send losing focus;
changed to aria-disabled with the existing synchronous canSend guard. The rerun
passed, and an additional controlled-clock deadline check passed. No other
application correction cycles. Initial server binding was sandbox-blocked;
authorized local execution started test services. The original mockup checksum
command initially ran from the wrong directory; rerunning from docs verified all
three v1 images unchanged.

## Preservation and limits

Real `data/wayfinder.sqlite3` SHA256 before/after:
`e7d83319033ee45c131fd8a9722ca492a1bc65638aa4b4b01d23ef4a29952c16`.
All mutations in regression checks used `.capture/chatbot-ui/isolated.sqlite3`.
Original v1 mockups, discovery code, storage code, sample/bookings code, manifests
and lockfiles were not edited. App.vue only imports/inserts the assistant and
adds its navigation link. Test services were stopped after verification.

No live OpenAI or Geoapify calls were made. Production success depends on private
backend configuration and account/model access. Real two-call latency, account
limits, screen-reader speech, other browsers and a full recorded demonstration
remain unverified. Browser abort prevents stale display but may leave already
started server/provider work running. The report and new recorded full workflow
still need real evidence and student review; historical report/video untouched.
