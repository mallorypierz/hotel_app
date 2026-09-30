# Assignment 2, Part 1 — Sequential prompts

Paste these prompts into Codex one at a time, in order. Review each result before proceeding. These prompts are a workflow, not evidence that the work has been completed. The brief lists Part 1 as due September 29, 2026, at 11:59 PM Eastern.

The existing project already has Geoapify ZIP geocoding. This assignment adds live nearby hotels and a synchronized Leaflet map. The older “Part 1” and “Part 2” checkpoints describe the previous sample-data assignment. Preserve them. The persistent live-hotel shortlist belongs to Assignment 2, Part 2 and is out of scope here.

## 1. Audit the project and establish Part 1 scope

```text
Prepare this repository for Assignment 2, Part 1: Live Hotel Search and Map. Read AGENTS.md, README.md, handoffs/current.md, the existing ZIP lookup code and tests, and the Git diff before editing. Preserve all unrelated and uncommitted work. Identify what already works and what is missing against the assignment brief.

Create docs/live-hotel-plan.md with an acceptance checklist: five-digit U.S. ZIP input preserving leading zeros; exact matching U.S. postcode resolution; Geoapify hotels within 5 km of the returned postcode point; synchronized Vue list and Leaflet map; honest provider fields; loading, results, invalid input, unresolved ZIP, empty results, and failed-request states; protected credentials; research, early mockup, verification, video, and report evidence.

Update AGENTS.md narrowly to distinguish this assignment from the earlier checkpoints and allow public Geoapify location data for this feature. Document MVC responsibilities and the dependency loop: CHECK the installed environment, explain the exact proposed installation and obtain student approval before TAKE ACTION, then VERIFY. Keep the existing verification loop and sample booking behavior. Do not implement the shortlist, real booking, payments, authentication, or deployment. Record the new scope in handoffs/current.md without erasing prior history. Do not change application behavior yet.
```

## 2. Research before implementation

```text
Complete the research stage for Assignment 2, Part 1 before implementing it. Inspect at least two existing hotel or location-search applications for ZIP/location input, list-and-map selection, missing information, and error feedback. Distinguish interactions you actually inspected from features described by sources.

Read current official Geoapify Geocoding documentation on postcode lookup and U.S. filtering, Places documentation on hotel categories and radius filters, Geoapify usage/pricing terms, and Leaflet documentation. Investigate a suitable tile provider's attribution, usage rules, and credential requirements. Save links, access dates, useful patterns, weaknesses, and adopted design decisions in docs/live-hotel-research.md.

Document exact postcode matching, the 5,000-meter radius and coordinate order, provider result limits, missing fields, request-volume control, and map attribution. Do not claim an exhaustive hotel inventory or bookable rooms. Keep the backend key out of browser configuration. If tiles require a client key, document its intended public use and restrictions separately. Do not install dependencies or change application code in this stage.
```

## 3. Create the early mockup

```text
Using the research, create an early annotated mockup for Assignment 2, Part 1 before implementation. Save a viewable image in docs/ and explain it in docs/live-hotel-design.md. Show desktop and narrow-screen arrangements with a labeled ZIP field, Search button, returned ZIP center, hotel list, Leaflet map, selected hotel in both views, and visible attribution.

Include sketches or annotations for initial, loading, results, invalid-input, unresolved-ZIP, no-nearby-hotels, and failed-request states. Explain that the radius is 5 km around Geoapify's returned postcode point, not the traveler's position or every address in the ZIP area. Show honest handling of missing names or addresses, keyboard selection, and result-limit wording. Keep existing sample bookings visually separate from live hotel discovery. Do not add live-hotel prices, ratings, availability, or booking buttons. Preserve this original mockup so later design changes can be documented. Show me the mockup when complete.
```

## 4. Check dependencies and settle the API design

```text
Prepare the implementation using the plan, research, and early mockup. Check installed frontend/backend packages and lockfiles. Reuse existing packages and the existing ZIP geocoding where suitable. If Leaflet or another dependency is needed, explain the exact package, version, installation command, purpose, and files affected, then wait for my approval before installing or upgrading it. After approval, install only the approved packages and verify the installation.

Document a small API contract and MVC plan in docs/live-hotel-plan.md: Vue owns display and selection; FastAPI owns validated routing; Python provider/controller logic owns geocoding and Places requests; Pydantic models define the response. Keep live external places separate from the sample Hotel model that requires a nightly rate. Include provider place IDs, available names/addresses, validated coordinates, search center, radius, and documented limit metadata. Define distinct invalid-input, unresolved-ZIP, empty-success, and provider-error responses. No shortlist or SQLite schema changes in this part.
```

## 5. Implement and verify the backend

```text
AutoLoop: Implement the Assignment 2, Part 1 backend using the agreed contract and existing environment. Accept ZIP codes as five-digit strings so 02108 retains its zero. Reuse or extend the existing geocoding logic to require the requested postcode and U.S. country code; never substitute a different location. Only after successful resolution, request Geoapify hotels within 5,000 meters of that returned point using the documented category and geographic filter.

Return genuine provider IDs and available hotel fields with validated coordinates. Handle missing fields honestly. Apply and document a result limit without claiming exhaustive coverage. Use timeouts and safe errors for missing configuration, provider failures, malformed responses, and quota/rate-limit responses. Failures must not become successful empty lists. Keep the key in the backend's local .env; verify .env is ignored and untracked without displaying its contents or key-bearing URLs.

Add meaningful isolated backend tests using controlled provider responses for leading zeros, mismatched/non-U.S. geocoding, radius/coordinate-order request construction, populated and empty results, missing fields, and provider failures. Avoid unnecessary live calls. Run backend tests and record exact results and limitations in docs/live-hotel-verification.md. Preserve the existing sample-data and ZIP demonstration endpoints. Update startup instructions if needed.
```

## 6. Implement the Vue list and Leaflet map

```text
AutoLoop: Implement the Assignment 2, Part 1 Vue interface from the early mockup, using the approved dependencies and verified backend contract. Use small Composition API components and an accessible text ZIP input. Call FastAPI for geocoding and Places; never expose the backend API key in frontend configuration, browser requests, or logs.

Show live hotels in a list and Leaflet map. Use the provider place ID as the shared selection identity: selecting a list item highlights its marker, and selecting a marker identifies and reveals the corresponding list item. Make selection operable with a keyboard. Show the returned ZIP center and explain the 5 km radius. Keep map attribution visible and follow the researched tile-provider policy.

Implement distinct loading, results, invalid-input, unresolved-ZIP, no-nearby-results, and request-failure feedback. Prevent stale responses or old markers from appearing to belong to a new search. Show available provider fields only, using honest missing-field labels; do not invent prices, ratings, room availability, or confirmations. Clearly separate existing sample bookings from live discovery. Provide usable narrow-screen layout and tile-loading failure feedback. Run frontend lint/build, exercise the interaction in the browser, and document changes from the original mockup and verification results.
```

## 7. Verify Part 1 and correct defects

```text
Run the smoke test, extending it for Assignment 2, Part 1. In this verification pass, do not change source code. Read README.md and docs/verification.md, then run backend tests, frontend lint, and frontend build. Reuse healthy running services on ports 8010 and 5173; if starting the backend on this Mac, use the documented SSL_CERT_FILE setting. Leave already-running services running.

In the browser, verify live searches for 16802 and 02108, leading-zero preservation, the returned U.S. ZIP center, correspondence between API hotels and list/markers, selection in both directions, keyboard operation, responsive layout, attribution, and loading feedback. Use controlled test responses or request interception for invalid/unresolved ZIP, mismatched-country/postcode resolution, no hotels, provider failure, and quota/rate-limit errors. Do not exhaust the live API or depend on a fixed live result count. Label simulated checks clearly. Check for console/API errors and unintended credential exposure without printing secrets. Regression-check Boston's four sample trip rows, Aspen's no-results message, and the existing sample booking workflow.

Record input/action, expected result, observed result, pass/fail, live ZIP and observation date, screenshots, and limitations in docs/live-hotel-verification.md. Separate live observations from simulated tests and mark untested items honestly. If a defect is found, report a focused repair prompt; do not claim completion until the correction and relevant rechecks pass.
```

If defects are reported, paste this before continuing:

```text
AutoLoop: Fix the verified Assignment 2, Part 1 defects just reported. State the acceptance checks, make the smallest in-scope corrections, rerun the failing checks and affected regressions, and update the verification record. Stop after five correction cycles or when dependency, scope, or data-model approval is required. Preserve an honest record of the failed approach and correction for the AI evidence log.
```

## 8. Prepare the demonstration and submission

```text
Prepare the Assignment 2, Part 1 submission from actual evidence. Preserve the previous assignment report before updating report.md, and keep its relative artifact links working. Include repository access, assessed-commit status, exact startup/configuration instructions without secrets, linked research and original early mockup, later design changes, verification results and limitations, and the screen-recorded demonstration link when available.

Create docs/live-hotel-demo-script.md with a short recording sequence: start the app, perform a live ZIP search including a leading-zero example, explain the returned center and 5 km radius, select a hotel from the list and then from the map, show honest provider data, demonstrate input/error feedback, and show responsive/keyboard use. Mark any simulated error demonstration clearly. Tell me what I need to record and supply; do not fabricate a video or use the previous assignment's recording as evidence for this feature.

Create an AI disclosure and evidence log identifying each tool, the specific model where known, and its use. If a model cannot be verified, ask me rather than inventing it. Link selected actual prompt excerpts to changes, verification, and decisions, including at least one genuine failed or revised approach. Do not invent failures.

Review the complete diff and manually verify successful Boston and no-results Aspen searches before any Git checkpoint, as required by AGENTS.md. Prepare a clear list of files for the Part 1 checkpoint, preserving unrelated work; do not commit or push in this preparation step. Leave the assessed commit explicitly pending until a real checkpoint exists. Provide the remaining checklist: checkpoint/publish assessed code, record and link the demo, verify instructor access to every linked artifact, replace pending report fields, and upload the completed report.md to Canvas. Do not claim the assignment is submitted or complete while those items remain.
```

After reviewing the report and recording your demo, you can explicitly request a checkpoint and publication of the reviewed Part 1 files. Confirm the assessed code commit is available to the instructor and referenced by the final report before uploading it.
