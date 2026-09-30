# AI disclosure and evidence log — Assignment 2, Part 1

Prepared September 29, 2026 from the actual conversation and repository evidence.
This log describes assistance and observed checks; it does not assert a student
recording, instructor approval, publication, or submission.

## Model and responsibility

**Codex desktop: GPT-6 Astra, medium reasoning**, confirmed by the student in
this conversation as “gpt 6 astra medium”; see [P6](../prompts/11-live-hotel-actual-evidence.md#p6--student-model-confirmation).
The exact setting was requested rather than guessed. This is student-confirmed
model provenance, not an independent backend attestation for each historical
call. Earlier research/mockup activities have saved artifacts, but no per-stage
model receipt; the log does not invent another model for them.

AI assistance contributed implementation drafts, controlled tests and browser
checks, debugging, documentation, the checkpoint proposal, and this report.
The student supplied requirements/scope, approved the recorded Leaflet change,
and must review the assessed code/report, record the demo, confirm any additional
AI use, authorize publication and submit. Automated passing tests are evidence
within their documented coverage, not a substitute for instructor review.
No additional outside AI tool was identified in the student's model reply;
if another tool was used, the student should add its name/model/task before submission.

## Tools and their actual use

| Tool / environment | Model, if applicable | Use and provenance |
| --- | --- | --- |
| OpenAI Codex desktop assistant | GPT-6 Astra, medium (student-confirmed) | Planning, code/test drafts, review, interpretation and documentation; actual excerpts linked below |
| Shell/terminal via Codex execution tools; Git, rg, file readers, Python/Node | Not generative models | Read source/handoff/diffs, inspect dependencies and ignore/index state, edit files, run local services/checks; no commit/push in preparation |
| Python pytest and controlled urllib responses | Not AI | Isolated backend validation, safe errors, request order/parameters and sample-data regressions; 124-test smoke result |
| npm, ESLint, Vite; installed Vue/Leaflet | Not AI | Dependency audit/approved Leaflet 1.9.4 installation earlier; lint/build; application execution. No new dependency during backend/UI repair or report preparation |
| Existing Playwright runtime and installed Chrome, invoked by Node scripts | Not AI | Real-browser assertions, controlled response/tile interception, screenshots, live ZIP observations, sample booking checks. Runtime is external to application dependencies |
| Codex computer-use/browser controls (CUA), in-app browser | Uses the assistant setting above; no separate model asserted | Submission-preparation Boston/Aspen UI actions and accessibility-tree inspection; selected Chrome integration was unavailable, so the available in-app browser was used |
| Browser research of OpenStreetMap/Google Maps and official provider documentation | Earlier precise model/tool variant not independently logged | Saved [research](live-hotel-research.md) reports observed interactions, sources/access dates and untested interactions. This does not imply a new research run during submission preparation |
| Web retrieval tool | Not a separately identified generative model | Submission-preparation attempt to read the repository URL returned a cache miss; no instructor/public access conclusion was fabricated |
| Python/Pillow renderer | Not AI image generation | Existing [mockup source](render-live-hotel-mockup.py) creates the original annotated static layout/state boards; these are mockups with labeled placeholders, not live results |
| Image viewer / screenshots | Not AI generation | Visual inspection of mockups and selected browser evidence; PNG artifacts reflect static design or labeled real/controlled browser states |
| User clarification and clock tools | No separate model | Requested exact model setting; dated evidence consistently in UTC/Eastern |
| Geoapify Geocoding/Places, OpenStreetMap tiles, Leaflet | Data/library services, not AI models | Runtime geographic data, imagery and rendering; backend-only credentials and separate visible credits |

No AI-generated video, voice, hotel records, prices, ratings, availability, or
reservation confirmations were used as live-feature evidence. The mockup was
rendered with code, not an image-generation model. No subagent work is claimed
for this recorded implementation/verification sequence.

## Prompt → decision/change → evidence

| Actual prompt excerpt | Decision/change | Evidence |
| --- | --- | --- |
| [P1: exact five-digit U.S. ZIP; failures not empty success](../prompts/11-live-hotel-actual-evidence.md#p1--backend-implementation) | Strict postcode/type/country match before Places; separate models, cap and safe errors | [Contract](live-hotel-plan.md), [tests](../backend/tests/test_discovery.py), [verification](live-hotel-verification.md) |
| [P2: shared provider ID; keyboard and stale protection](../prompts/11-live-hotel-actual-evidence.md#p2--vue-interface) | Small Composition API components; shared selection and version/abort handling | [Design log](live-hotel-design.md), [controlled results](browser-checks/discovery-results.json) |
| [P3: verification only; simulated failures](../prompts/11-live-hotel-actual-evidence.md#p3--verification-without-repair) | Two deliberate live searches; upstream/route/browser failure fixtures; no source repair in smoke pass | [Live/simulated results](browser-checks/smoke-extended-results.json), [source/database integrity](browser-checks/smoke-integrity-results.json) |
| [P4: repair the actual favicon defect](../prompts/11-live-hotel-actual-evidence.md#p4--approved-focused-d1-repair) | Local SVG + explicit document icon link, no dependency | [Original failure](browser-checks/smoke-followup-results.json), [fresh-load pass](browser-checks/d1-favicon-results.json), [regressions](browser-checks/d1-regression-results.json) |
| [P5: preserve report; commit pending](../prompts/11-live-hotel-actual-evidence.md#p5--submission-preparation) | Byte-identical root-level archive, pending fields, explicit staging proposal | [Archived report](../report-previous-assignment-part2.md), [current report](../report.md), [checkpoint review](live-hotel-checkpoint.md) |

[Sequential prompt guide](../prompts/10-live-hotel-search.md) is a workflow artifact;
it is not labeled a full transcript. Actual excerpts above are from messages
visible in this conversation. No hidden/internal reasoning is presented as evidence.

## Genuine failed or revised approaches

1. **Backend traceback sanitation:** initial integration run had 121 passed and
   3 failed. The shared transport left a literal endpoint visible on a traceback
   source line, violating existing no-URL assertions. Separating URL construction
   from the call line preserved tests and produced 124 passed in 0.37s. No real
   secret was displayed. [Recorded initial failure and correction](live-hotel-verification.md).
2. **Leaflet initialization / keyboard:** browser testing found marker DOM
   access before the initial map view and absent explicit Enter activation for
   custom markers. Setting the view first and handling Enter corrected these;
   later controlled checks passed. These are recorded source defects, not
   invented examples. [Design changes](live-hotel-design.md).
3. **Smoke-test harness revisions:** an exact-label locator missed the traveler
   combobox; role/name lookup worked. A cleanup check incorrectly expected U006
   to be empty even though two original bookings existed. Verification was
   corrected to compare created IDs and the database baseline, preserving the
   original records. [Initial failure](browser-checks/smoke-extended-results.json),
   [booking pass](browser-checks/smoke-bookings-results.json),
   [mistaken empty-history check](browser-checks/smoke-restart-results.json),
   [baseline comparison](browser-checks/smoke-integrity-results.json).
4. **D1 actual favicon failure:** fresh app loading requested a missing
   `/favicon.ico` and logged 404. The verification-only pass reported it without
   changing source. A subsequent authorized AutoLoop added a local SVG and
   document reference. At 20:44 Eastern the actual `/favicon.svg` response was
   200 `image/svg+xml`, with no fallback request or fresh-load console/page errors;
   16 controlled regressions passed. Original failed JSON remains linked above.

No failing approach was invented for this log. Passing corrections are tied to
specific checks, not generalized claims that the application is flawless.

## Evidence limits and disclosure sign-off

Live and simulated observations are labeled in [verification](live-hotel-verification.md).
No screen-reader/physical-device/full security audit or instructor-access
verification is claimed. The previous assignment recording is not reused for
Part 1. The new demo, assessed commit, publication and Canvas submission are
pending. The student must confirm that this log captures any additional tools
used outside the recorded work and review the final report before submitting.


## Final evidence update — September 29, 2026

Student replied “no AI” when asked about additional AI tools; this is recorded
as no additional tools reported, retaining the earlier explicit Codex GPT-6
Astra/medium disclosure for this work. Supplied screen recording is student
content, not generated video. Native macOS AVFoundation/Swift inspected metadata
and frames and transcoded a sharing copy; avconvert attempts were revised because
outputs remained large. Python urllib with the documented CA bundle verified
public GitHub artifacts and research links. No new model or dependency added.
Assessed code is published; recording and access review are documented in
[final evidence](live-hotel-final-access.md). Canvas upload remains outstanding.
