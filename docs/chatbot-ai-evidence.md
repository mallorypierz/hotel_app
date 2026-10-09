# Chatbot AI disclosure and evidence log

Prepared October 8, 2026. This report and implementation were AI-assisted. The
student supplied requirements, boundaries and staged prompts; Codex performed
repository reading, research, design artifacts, code/test changes, verification
and draft documentation. Final student review/submission remains necessary.
[Selected actual prompt excerpts](../prompts/12-chatbot-actual-evidence.md) link
instructions to implementation and observed checks.

## Tools and model provenance

| Tool | Known model/version | Use and limits |
| --- | --- | --- |
| Codex desktop coding assistant | Current task's system identifies a GPT-6-based agent; exact backend snapshot and per-turn model routing are not exposed. **Do not infer a more specific ID.** | Planning, research synthesis, mockup renderer/code, Python/Vue implementation, test orchestration, debugging and report drafting |
| Earlier Part 1 Codex session | Student-confirmed “GPT-6 Astra, medium reasoning” in the preserved Part 1 disclosure | Historical setting only; not evidence of the model used in current chatbot work |
| Application's selected OpenAI Responses API | Exact configured/pinned `gpt-4.1-mini-2025-04-14` for both requests | Intended SQL proposal and grounded recommendation selection. No live API call verified; configured identifier is not evidence that this model executed. |
| Controlled model-response mocks | **No LLM runs** | Fixed structured query/answer outputs; fake response IDs and usage are test values, not real provider telemetry. They exercise real transport parsing/controller/SQLite logic locally. |
| Web research tool | No separate model identity exposed | Consulted official sources during dated research; links and inaccessible-page limitations retained in research notes |
| Python/Pillow documentation renderer | Non-LLM code; existing bundled Pillow | Created original static mockup PNGs with illustrative content; no image-generation model was used |
| Shell/Python/sqlite3/pytest, npm/ESLint/Vite | Non-LLM verification tools | Filesystem/source inspection, isolated database checks, test/build output; no dependency addition for chatbot |
| Playwright with existing Chrome | Non-LLM browser automation | Keyboard/state/layout/injection and regression checks; controlled provider responses labeled; no claim of live successful chat |

No additional student AI use has been attested for Part 2. The prior Part 1
statement about additional tools is historical and is not generalized to this
submission. No Nemotron/Gemini configuration or model use is claimed.

## Dated work and genuine revisions

| October 8 stage | Actual work / observed correction | Evidence |
| --- | --- | --- |
| Audit/research | Read existing storage/schema and revised brief; selected one backend provider and standard-library transport | [Plan](chatbot-plan.md), [research](chatbot-research.md) |
| Early mockup | Saved v1 desktop/mobile/state images before implementation. Draft glyph and evidence consistency edits recorded during design review | [Design notes](chatbot-design.md); originals remain unchanged |
| Read-only boundary | First suite: 85 passed, 5 failed. This SQLite build omitted the DB name on empty-column COUNT authorization events. Revised only that approved-table case; rerun 90 passed, full suite 256 passed | [Retrieval verification](chatbot-retrieval-verification.md), [tests](../backend/tests/test_chat_queries.py) |
| Backend test fixture | Injected record-name change initially happened after the byte-preservation snapshot, causing one teardown failure. Moved fixture setup before the snapshot; did not weaken preservation assertions | [Backend verification](chatbot-backend-verification.md), fixture in [test_chat.py](../backend/tests/test_chat.py) |
| Query/answer design revision | Early mockup illustrated aggregate SQL. Implemented raw nightly retrieval with independent completeness/arithmetic checks and structured recommendation IDs/reasons to avoid duplicate totals and unsupported factual prose | [Design changes](chatbot-design-changes.md), [stay logic](../backend/app/chat_stays.py) |
| Frontend accessibility failure | Initial browser check showed native-disabled Send lost keyboard focus during loading. Replaced native disabled with aria-disabled plus synchronous submission guard; rerun passed. Initial 70 formatting warnings were also resolved | [Frontend verification](chatbot-frontend-verification.md), [current browser results](chatbot-verification-evidence/chatbot-browser.json) |
| Verification-only pass | Historical discovery harness adapter initially omitted required local-result fields, causing a timeout. Corrected only disposable verification fixture shape; 16 scenarios passed. Application source unchanged | [Verification and correction](chatbot-verification.md), [results](chatbot-verification-evidence/discovery-browser.json) |
| Submission assembly | Archived Part 1 byte-for-byte, assembled controlled traces/expectations and demo script, freshly captured three rejected queries with schema/table/hash equality | [Preservation](chatbot-verification-evidence/part1-report-preservation.json), [rejected evidence](chatbot-verification-evidence/rejected-queries.json) |

These are actual failed or revised approaches recorded during work, not failures
invented for the rubric. No unrecorded model response, successful live call,
screen recording, assessed commit or public-access result is supplied.

## Responsibility and remaining evidence

The student should review generated code, explanations and claims, privately
configure the real provider, record a genuine two-request workflow and negative
case, authorize an assessed checkpoint when ready, and confirm artifact access.
Missing live/video/commit/access items remain prominent in report.md. Reports,
traces and screenshots contain no keys, private booking records or .env content.
The fixed fixture is fictitious; the real saved hotel's simulated values are
identified separately as read-only expectations, not successful model output.

## Subsequent live verification

The student later configured credentials and purchased credits. Three actual
OpenAI attempts exposed invalid clause ordering, unnecessary clarification, then
a successful two-call answer. Exact known executing model: gpt-4.1-mini-2025-04-14.
[Live follow-up and actual evidence](chatbot-live-followup.md) supersede earlier
no-live-call statements. Prompt guidance was revised without weakening SQL checks.
