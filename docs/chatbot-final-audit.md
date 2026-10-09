# Revised Assignment 2 Part 2 audit — October 9, 2026

**Recording follow-up:** Student-supplied [video](https://github.com/mallorypierz/hotel_app/releases/tag/assignment2-part2-demo-2026-10-09) published with explicit
public-sharing approval. Unauthenticated download HTTP 200 and matching SHA256
verified. Replacement duration 54.935 seconds (student requested replacing the earlier recording). This resolves the missing video-link item;
full recorded rubric coverage has not been reviewed. Course submission remains
pending. The audit matrix below preserves the earlier audit state.

**Checkpoint follow-up:** The student subsequently authorized commit/push. Current
report/README/demo script now include the actual live results. Application/evidence
checkpoint `6bce3f406c675175f14dfe3e7e9b69520104d00b` was committed locally. The
existing GitHub repository is publicly readable (unauthenticated API HTTP 200,
private=false), the first push failed with invalid Git credentials. Authentication was subsequently
restored and the checkpoint plus documentation were pushed successfully. Public
report and live-evidence URLs returned HTTP 200. Video and submission remain missing. The matrix below records
the pre-checkpoint audit; its report/commit gaps are resolved locally only.

**Implementation verified within the checks below; submission is not complete.** This audits the supplied October 1 revised brief. VERIFIED means observed code/tests/evidence support the benchmark, not a guarantee of a grade. FAILED means a required item is currently absent or inconsistent. UNVERIFIED means evidence is unavailable. No source changes, dependencies, commits, pushes, recordings or submissions were made during this audit.

## Benchmark matrix

| Benchmark | Status | Supporting evidence and limits |
|---|---|---|
| Saved API hotels, ZIP associations and dated simulated nights | VERIFIED | Actual `saved_hotels`, `saved_hotel_locations`, `demo_hotel_nights`; storage tests in fresh [349-test run](chatbot-audit-evidence/backend.xml). Real saved Comfort Inn used below. |
| Add/remove, duplicate prevention, refresh/restart persistence, local-first lookup | VERIFIED | Fresh backend tests; prior isolated [storage/browser verification](chatbot-verification.md), [restart browser evidence](chatbot-verification-evidence/restart-browser.json), [restart database evidence](chatbot-verification-evidence/restart-database.json). Mutating browser checks were not repeated on student records. |
| Frozen Part 1 exact ZIP resolution, provider fields, list/map synchronization, attribution and error states | VERIFIED | Discovery source unchanged by chatbot diff; prior [16-case browser evidence](chatbot-verification-evidence/discovery-browser.json), fresh regression suite. Historical live ZIP/date evidence retained in [original report](../report-assignment2-part1.md). No new live Geoapify search in this audit. |
| Assignment 1 records, joined city search and sample booking behavior | VERIFIED | Manual Boston returned four joined rows; Aspen displayed no results, [Boston](chatbot-audit-evidence/boston.txt), [Aspen](chatbot-audit-evidence/aspen.txt). Fresh backend suite and prior isolated [booking browser check](chatbot-verification-evidence/booking-browser.json). Real SQLite file byte-identical before/after audit. |
| Natural-language question, loading, answer, failure and clarification | VERIFIED | Live loading and success/no-match observed; failure/clarification controlled tests. Conservative explicit ZIP/date/year/room grammar is documented; arbitrary natural-language understanding is not guaranteed. |
| First LLM request carries original question, relevant schema and strict rules | VERIFIED | `chat_controller.py`, `chat_prompts.py`, `llm_provider.py`; complete first request body in [controlled transport trace](chatbot-audit-evidence/mock-success.json). Actual first stage completed in live UI trace. |
| Model produces SQL plus bound parameters | VERIFIED | Live evidence contains model-proposed SELECT, JOIN, EXISTS, date bounds and positional parameters. Invalid/malformed proposals fail closed in tests. |
| Backend validation and bounded, read-only local execution | VERIFIED | Separate `chat_models.py`/`chat_queries.py`; mode=ro, query_only, default-deny authorizer, explicit tables/columns/functions, extensions disabled, single-statement preflight/execution, result/VM/time limits. [Rejected evidence](chatbot-audit-evidence/rejected-queries.json) and fresh malicious/expensive-query tests. Remote model has no SQLite connection. |
| Second LLM request includes original question and retrieved records | VERIFIED | Captured controlled HTTP body exactly matches intervening real isolated SQLite records; controller source inspected. Both actual live stages completed. Live browser evidence shows returned stages/records, not a packet capture of encrypted provider traffic. |
| Grounded answer: hotels, dates, totals, availability, recommendation reason | VERIFIED | Real success below; LLM selects structured IDs/reasons, backend checks them and renders verified numeric prose. No silent mock fallback. Visible answer no longer displays provider codes; expanded raw evidence retains identifiers. |
| Multi-night correctness, checkout exclusion, all-night room sufficiency, missing-night honesty, budget semantics and duplicate associations | VERIFIED | Fixed fixture rerun and fresh tests: Birch $260, River $300, unavailable hotel excluded, missing total unknown, checkout's $990/zero-room row excluded, multiple ZIP associations do not duplicate totals. Nightly/total budgets and multiple rooms tested separately. |
| One allowed provider; backend-only credentials/model requests | VERIFIED | Only OpenAI, exact `gpt-4.1-mini-2025-04-14`; standard-library HTTPS to Responses API. Vue calls `/api/chat` only. No provider/model fallback. |
| Simulated label, no booking or database mutation in chatbot | VERIFIED | Persistent label in live UI; response limitations visible; separate existing sample booking workflow. Real database byte hash unchanged. |
| Keyboard, responsive layout, safe rendering, duplicate/stale protection, expandable evidence | VERIFIED | Native controls/details, Vue text interpolation, request guard/abort/version handling; previous [browser evidence](chatbot-verification-evidence/chatbot-browser.json), current live UI. Physical screen-reader and all-browser testing remain unverified. |
| Research: dated sources, observed useful/problematic features and design decisions | VERIFIED | [Chatbot research](chatbot-research.md), [Part 1 report](../report-assignment2-part1.md), provider limits and course-data scope documented. This audit does not freshly validate every external source URL. |
| Original early desktop/mobile mockup and later changes | VERIFIED | [Design](chatbot-design.md), original v1 image hashes pass; [design changes](chatbot-design-changes.md). Original images preserved. |
| MVC boundaries, small route, dependency approval loop | VERIFIED | Contracts/models, executor, controller and transport separate; Vue components/composable separate. No changes to requirements/package manifests/lockfile. Installed packages checked; no new dependency approval needed. |
| Fixed JSON sample and repeat instructions | VERIFIED | [Fixture](../data/chatbot-fixture.json), [repeat instructions](chatbot-verification.md); fresh isolated rerun below. Does not overwrite student records. |
| Expected/observed errors and no-mutation proof | VERIFIED | Fresh full suite covers malformed output, missing config, timeout, simulated quota/rate limits, second-call failures, unauthorized reads/writes/multiple statements/expensive SQL. Three fresh rejected attempts retain every table/schema and file hash. No quota exhaustion used. |
| Successful LIVE full workflow and LIVE negative case | VERIFIED | Fresh [live success text](chatbot-audit-evidence/live-success.txt)/[image](chatbot-audit-evidence/live-success.jpg) and [live no-match text](chatbot-audit-evidence/live-no-match.txt)/[image](chatbot-audit-evidence/live-no-match.jpg), both OpenAI stages completed. Four real model calls total in these two UI submissions. |
| Current report accurately presents completed live evidence | FAILED | `report.md` still says no configured key/live evidence incomplete in its table and verification text; README has the same stale statement. Top historical follow-up notice does not resolve contradictory current status. New audit evidence must be integrated. |
| Repository link and startup/private configuration instructions | VERIFIED | Present in README/report; current local frontend/backend work. Current HEAD alone lacks uncommitted chatbot files. |
| Assessed chatbot commit and instructor-accessible current artifacts | FAILED | HEAD `3a31777445071e51159e965c98e0ac41da6f0f88` is storage checkpoint; chatbot remains uncommitted. Missing assessed commit explicitly marked. No checkpoint/push authorized. |
| Instructor can open every artifact without requesting access | UNVERIFIED | 37 local report/archive/README file links resolve; remote/instructor access not tested. New artifacts are local, not established as published. Historical Part 1 public access is not proof of current Part 2 access. |
| Screen-recorded Part 2 demo and URL | FAILED | No new recording or video URL. [Demo script](chatbot-demo-script.md) exists but is not a recording; its live-pending wording also needs updating. |
| AI disclosure, actual prompts, genuine failed/revised approach | VERIFIED | [Disclosure](chatbot-ai-evidence.md), [selected prompt excerpts](../prompts/12-chatbot-actual-evidence.md), [real failed SQL/revised prompt history](chatbot-live-followup.md). Application model is exact. Coding-agent snapshot is explicitly unknown, not invented; student should supply it if independently known. |
| Credentials/private data excluded from publication candidates | VERIFIED | Configured credential byte values and key-pattern scan found zero matches in tracked/nonignored candidates and existing frontend build; `.env`, real SQLite, captures and build ignored. No tracked secrets/database files. Scoped scan does not certify unseen Git history or a future recording. |
| Course upload and deadline compliance | UNVERIFIED | No submission receipt/access to course submission. Revised due date is October 8, 2026 11:59 PM Eastern; audit is October 9. No assumption about extensions, previous uploads or late policy. |

## Fresh live expected versus observed

Success question: “Compare saved hotels in ZIP 06109 for 1 room from 2026-10-10 to 2026-10-12 under $350 total for the stay.” Exact proposed SQL and bound parameters are in the saved UI transcript. Read-only validation and independent record verification passed. Retrieved Comfort Inn rows:

| Night | Simulated rate | Rooms |
|---|---:|---:|
| 2026-10-10 | $200 | 15 |
| 2026-10-11 | $100 | 20 |

Expected: two nights, checkout October 12 excluded, one room, $200 + $100 = $300, minimum 15 rooms, qualifies under $350. Observed: frontend displayed exactly those facts and a meets-requirements recommendation; `hotel_query` and `hotel_answer` completed under OpenAI / `gpt-4.1-mini-2025-04-14`.

Negative question: same explicit ZIP/dates/room count with **$1 total**. Expected: same two retrieved rows, no qualifying hotel, no invented lower cost. Observed: “No saved hotels match this stay, room count and budget”; card shows $300, minimum 15 rooms, “Outside the requested budget.” Both model stages completed and validation passed. This is a real no-match decision over retrieved rows, not an empty mock response.

## Commands and repeat results

Run from repository root. Fresh results saved in `docs/chatbot-audit-evidence/`:

```sh
backend/.venv/bin/python -m pytest backend/tests -q --junitxml=docs/chatbot-audit-evidence/backend.xml
npm --prefix frontend run lint
npm --prefix frontend run build
backend/.venv/bin/python -m pip check
npm --prefix frontend ls --depth=0
```

Observed: **349 passed in 1.67s**; lint clean; build 33 modules in 215ms; pip reports no broken requirements; npm package inventory valid. Logs: [backend](chatbot-audit-evidence/backend.log), [lint](chatbot-audit-evidence/lint.log), [build](chatbot-audit-evidence/build.log).

Fixture evidence scripts were copied to `.capture/final-audit-2026-10-09/`, changing only output destination from `docs/chatbot-verification-evidence` to `docs/chatbot-audit-evidence` and rejection evidence date to October 9, preserving historical outputs. Exact execution:

```sh
backend/.venv/bin/python .capture/final-audit-2026-10-09/chatbot-verification.py
backend/.venv/bin/python .capture/final-audit-2026-10-09/chatbot-rejected-evidence.py
```

To repeat later use the original documented scripts in `docs/browser-checks/`; they always create isolated databases (their evidence outputs will be refreshed). Fresh [success](chatbot-audit-evidence/mock-success.json), [no-match](chatbot-audit-evidence/mock-no-match.json), [insufficient](chatbot-audit-evidence/mock-insufficient.json) all HTTP 200 with expected status, two labeled mocked model requests, real local retrieval and unchanged SQLite. Rejected DELETE, Assignment 1 read, and multiple statements all `query_rejected` with identical before/after schema, records and hashes.

Manual browser: reload localhost:5173; search Boston (four joined rows), search Aspen (no-results message); send success and negative questions above; expand evidence after each. No warn/error console entries returned after these checks. Successful UI responses observed; no new comprehensive HTTP network capture performed. Existing services were reused and left running; none started or stopped for this audit.

## Diff, preservation and limitations

Reviewed all tracked diff and new application boundaries; inventory of new implementation, tests and evidence is in [repository review](chatbot-audit-evidence/repository-review.json). Tracked application changes are six backend configuration settings, chat route/middleware registration, and App.vue import/navigation/component insertion. Discovery/storage/booking implementation files and dependency manifests are unchanged by the chatbot diff. Existing uncommitted work preserved.

[Preservation proof](chatbot-audit-evidence/preservation.json): real `data/wayfinder.sqlite3` SHA256 before and after is `d8ef4ef671355aff0be4894a3ce1880e877a6cd408e6e5289548324dcd5a2c5b`. Assignment 1 snapshot counts: hotels 8, trips 12, users 6, bookings 6, metadata 1. Entire database byte identity covers saved records as well. Archived Part 1 report equals `git show HEAD:report.md` byte-for-byte, in the same directory for link resolution; all original mockup hashes pass. [37 local link checks](chatbot-audit-evidence/links.json) have no missing target files; external links and Markdown anchors are not comprehensively validated by this check.

Known practical limits: maximum 50 returned rows/24 KiB and bounded query work can reject larger saved datasets instead of returning misleading partial results. Conservative intent grammar requests clarification outside supported phrasing. Query wall-time enforcement is cooperative; no concurrency/load stress test. Proposed/canonical retrieval use separate connections, so concurrent saves can cause fail-closed mismatches. No exhaustive arbitrary-prompt, cross-browser or screen-reader certification. Live tests show this account/model worked at observation time, not future availability.

## Remaining student actions and focused follow-ups

1. Update current report/README/demo-script live status and link this audit's real success/no-match traces and fresh verification; retain old evidence as dated history. Repair prompt: “Reconcile current submission documents with docs/chatbot-final-audit.md; remove contradictory absent-key claims, preserve the Part 1 archive, and keep recording/commit/access explicitly missing.”
2. Record the running application using the script: local save/remove/persistence, successful live chat, SQL/records/answer evidence, no-match, and labeled controlled rejected-query/no-mutation proof. Add the actual video URL; check frames for keys/private information.
3. Separately authorize a reviewed checkpoint/push; record the assessed chatbot commit and publish its required linked artifacts. No commit was created by this audit.
4. Verify repository, images, evidence and video access as an instructor would see them, without an access request. Add immutable assessed-commit links where appropriate.
5. Submit the final report through the course system and confirm its receipt and applicable deadline arrangements. This audit does not submit or assert full completion.
