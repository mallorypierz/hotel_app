# Assignment 2, Part 1 — proposed checkpoint and review

Prepared September 29, 2026. **No staging, commit or push was performed.**
Assessed code SHA: **PENDING**. Current branch: `main`; current HEAD
`eb256a3ac5cc08be4029e6e3354099c3ce903163` belongs to the previous assignment.
It must not be presented as this feature's assessed version.

## Review scope and findings

Reviewed the complete tracked working-tree diff, including the accumulated
handoff, and inventoried all untracked additions. Reviewed the proposed new
backend/Vue sources, tests, verification scripts/results and documentation in
this work sequence. Existing screenshot/mockup evidence was cross-checked with
its recorded purpose; selected screenshots were visually inspected. Unrelated
legacy videos were inventoried for exclusion, not watched or reclassified as
Part 1 evidence. Final link/archive/index checks are recorded in
[preparation checks](submission-preparation-checks.json).

- `.gitignore` protects local environment files; no credential values belong in
  the checkpoint. Recheck ignored/untracked status before staging.
- New discovery modules are separate from sample models/storage; sample database
  source/data files have no feature changes. No schema/auth/payment additions.
- Frontend manifest/lockfile add approved Leaflet 1.9.4; no other locked package
  change was found. Pre-existing `python-dotenv` remains unpinned, as documented.
- The earlier ZIP foundation (`config.py`, `geocoding.py`, tests, health/demo
  routes, dotenv requirement, Vue ZIP panel and ZIP evidence) is uncommitted but
  required by the current feature/README. Include it explicitly rather than
  accidentally omitting an import or silently treating it as already published.
- Sample source changes label the workflows separately and mount discovery;
  booking component/database/controller sources remain unchanged.
- D1 is a local SVG plus one HTML link. Its original failed smoke evidence and
  successful correction remain in the checkpoint, with no rewritten history.
- Historical research/plan sections describe their stage at the time; later
  handoff/verification sections supersede pending implementation statements.
- The new report is intentionally pending assessed SHA/video/access/submission.
  It is not a false final submission claim.

## Browser-operated Boston / Aspen gate

September 29, 2026, about 20:48 Eastern, local app on 8010/5173. The agent
operated the actual search field using CUA's in-app browser, submitted each
search, and inspected rendered results/accessibility state; this was not only
an API assertion or a replay of old screenshots. The configured Chrome browser
integration was unavailable, so the available in-app browser was used.

| Action | Expected | Observed | Result |
| --- | --- | --- | --- |
| Enter Boston and submit sample search | Four joined trip rows with labels | Harbor Lantern Hotel / Maple Square Inn, four distinct offered trips; Hotel, City, State, Nightly rate, Trip, Check in/out, Book a stay columns | PASS |
| Replace with Aspen and submit | Clear no-result message | “No stays matched”; spelling/another-search guidance | PASS |
| Read browser error/warning log | No errors attributable to these actions | Empty returned error/warning list | PASS |

Evidence: [Boston](submission-review-boston.png), [Aspen](submission-review-aspen.png).
An initial input automation action did not submit the reactive value; clearing
and retyping through the browser control, then pressing Enter, produced the
verified result. No application repair was required. Other visible discovery/
ZIP-demo content is not counted as new controlled evidence in this sample-only
review. No booking mutation occurred. No checkpoint was created.
If source changes before the actual checkpoint, repeat this gate and review the
new complete/staged diff. These checks do not authorize automatic publication.

## Proposed exact file set

The [newline-delimited manifest](live-hotel-checkpoint-files.txt) is a **review
proposal**, not a command that has been executed. It includes this preparation's
artifacts and the referenced evidence below. A later authorized checkpoint may
stage only reviewed paths after a fresh status check; avoid `git add .` and
broad globs. Existing tracked prior-assignment files remain in repository history
without being changed or re-added. Review the staged diff and secret exclusions
before committing, then capture the real commit SHA and publish only when authorized.

### Application, configuration and dependency records

- `.gitignore`
- `backend/app/config.py`
- `backend/app/discovery.py`
- `backend/app/discovery_models.py`
- `backend/app/geocoding.py`
- `backend/app/main.py`
- `backend/app/provider.py`
- `backend/requirements.txt`
- `backend/tests/test_config.py`
- `backend/tests/test_demo_zip_route.py`
- `backend/tests/test_discovery.py`
- `backend/tests/test_geocoding.py`
- `frontend/index.html`
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/public/favicon.svg`
- `frontend/src/App.vue`
- `frontend/src/components/DiscoveryForm.vue`
- `frontend/src/components/DiscoveryList.vue`
- `frontend/src/components/DiscoveryMap.vue`
- `frontend/src/components/HotelDiscovery.vue`
- `frontend/src/components/ZipLookupPanel.vue`
- `frontend/src/composables/useDiscovery.js`
- `frontend/src/style.css`

### Reports, project instructions, handoff and actual prompts

- `AGENTS.md`
- `README.md`
- `handoffs/current.md`
- `prompts/10-live-hotel-search.md`
- `prompts/11-live-hotel-actual-evidence.md`
- `report-previous-assignment-part2.md`
- `report.md`

### Research, design, verification and submission documents

- `docs/live-hotel-ai-evidence.md`
- `docs/live-hotel-checkpoint-files.txt`
- `docs/live-hotel-checkpoint.md`
- `docs/live-hotel-demo-script.md`
- `docs/live-hotel-design.md`
- `docs/live-hotel-plan.md`
- `docs/live-hotel-research.md`
- `docs/live-hotel-verification.md`
- `docs/zip-lookup.md`

### Executable/check-result evidence

- `docs/browser-checks/d1-favicon-results.json`
- `docs/browser-checks/d1-favicon.cjs`
- `docs/browser-checks/d1-regression-results.json`
- `docs/browser-checks/d1-regression.cjs`
- `docs/browser-checks/discovery-live-results.json`
- `docs/browser-checks/discovery-live.cjs`
- `docs/browser-checks/discovery-results.json`
- `docs/browser-checks/discovery.cjs`
- `docs/browser-checks/smoke-baseline.json`
- `docs/browser-checks/smoke-bookings-results.json`
- `docs/browser-checks/smoke-bookings.cjs`
- `docs/browser-checks/smoke-extended-results.json`
- `docs/browser-checks/smoke-extended.cjs`
- `docs/browser-checks/smoke-followup-results.json`
- `docs/browser-checks/smoke-followup.cjs`
- `docs/browser-checks/smoke-integrity-results.json`
- `docs/browser-checks/smoke-provider-results.json`
- `docs/browser-checks/smoke-provider.py`
- `docs/browser-checks/smoke-restart-results.json`
- `docs/browser-checks/smoke-restart.cjs`
- `docs/render-live-hotel-mockup.py`
- `docs/submission-preparation-checks.json`

### Screenshot and original mockup evidence

- `docs/d1-controlled-controlled-desktop.png`
- `docs/d1-controlled-controlled-mobile.png`
- `docs/d1-controlled-tile-failure.png`
- `docs/d1-fresh-load.png`
- `docs/live-hotel-mockup-v1.png`
- `docs/live-hotel-states-v1.png`
- `docs/live-hotel-ui-controlled-desktop.png`
- `docs/live-hotel-ui-controlled-mobile.png`
- `docs/live-hotel-ui-live-02108.png`
- `docs/live-hotel-ui-tile-failure.png`
- `docs/smoke-booking-cleanup.png`
- `docs/smoke-booking-created.png`
- `docs/smoke-booking-refreshed.png`
- `docs/smoke-booking-restarted.png`
- `docs/smoke-live-02108.png`
- `docs/smoke-live-16802.png`
- `docs/smoke-live-320.png`
- `docs/smoke-sample-aspen.png`
- `docs/smoke-sample-boston.png`
- `docs/smoke-simulated-empty.png`
- `docs/smoke-simulated-invalid.png`
- `docs/smoke-simulated-loading.png`
- `docs/smoke-simulated-mismatched_postcode.png`
- `docs/smoke-simulated-non_us.png`
- `docs/smoke-simulated-provider_failure.png`
- `docs/smoke-simulated-quota.png`
- `docs/smoke-simulated-rate_limit.png`
- `docs/smoke-simulated-selection-mobile.png`
- `docs/smoke-simulated-tile-failure.png`
- `docs/smoke-simulated-unresolved.png`
- `docs/submission-review-aspen.png`
- `docs/submission-review-boston.png`
- `docs/zip-02108.png`
- `docs/zip-16802.png`

## Preserve outside this checkpoint

These pre-existing untracked legacy artifacts are **not selected**; leave them
in place, do not delete or stage them as a side effect:

- `docs/part2-boston.png`
- `docs/part2-created.png`
- `docs/part2-demo.m4v`
- `docs/part2-refresh.png`
- `docs/part2-restarted.png`
- `docs/wayfinder-ui-demo.m4v`

The already tracked `docs/part2-student-demo.mov` and old report artifacts remain
unchanged in the repository. The root-level report archive preserves their
original links; none is repurposed as the new demo.

Always exclude `.env`/local credentials, `data/*.sqlite3*`, `backend/.venv/`,
`frontend/node_modules/`, `frontend/dist/`, caches and unrelated workspace files.
No live Part 1 recording has yet been supplied, so no guessed video path is staged.
The manifest is not permission to install, rewrite history, commit or push.

## Remaining release and submission work

1. Student reviews/authorizes the explicit file set, then checkpoint/publish the
   assessed implementation and evidence. Record the real full SHA and verify it
   is present in the accessible repository.
2. Record and supply the new feature demo using [the script](live-hotel-demo-script.md),
   with date/duration/version and clearly labeled simulated segments if any.
3. Verify instructor access to every linked artifact and the full recording.
4. Replace pending report fields and use immutable, working URLs for standalone
   Canvas Markdown. Add a documentation-only follow-up checkpoint if necessary;
   retain the correct assessed code SHA rather than inventing a self-referencing SHA.
5. Upload the completed `report.md` to Canvas and verify the receipt.

No publication or submission was performed in this preparation.


Post-preparation change: the student requested one ZIP search field. App.vue now
mounts only live discovery for ZIP input; legacy ZIP component/API source remains
preserved in the proposed file set. The prior manual gate predates this change;
repeat complete diff review and Boston/Aspen browser checks before checkpoint.


## Authorized Part 1 checkpoint gate — 2026-09-29 21:09 EDT

Student explicitly requested final review, Boston/Aspen rechecks, commit and push.
Reviewed tracked changes and selected new application/test artifacts against the
96-path checkpoint manifest and earlier evidence review. No blocking defect
found. The exact local credential was scanned without printing it: no match in
selected files; `.env` ignored and untracked. Previous report archive still
matches pre-checkpoint HEAD byte-for-byte; all selected Markdown local links
resolve. Six unrelated legacy media files remain excluded. Remote main matched
local pre-checkpoint HEAD; no history rewrite is needed.

| Check/action | Expected | Observed | Result |
| --- | --- | --- | --- |
| Backend pytest suite | All tests pass | 124 passed in 0.40s | PASS |
| Frontend lint | Exit 0 | Exit 0 | PASS |
| Frontend build | Exit 0 | 26 modules, 194 ms; exit 0 | PASS |
| Browser: type Boston in sample search and press Enter | Four labeled joined trip rows | Harbor Lantern Hotel and Maple Square Inn, four trip rows; hotel/city/state/rate/trip/check-in/check-out/booking labels | PASS |
| Browser: replace with Aspen and press Enter | No-result feedback | “No stays matched” | PASS |
| Browser warning/error log | Empty | Empty returned list | PASS |

Reused healthy existing services on 8010/5173 and left them running. No booking
mutation or new live provider search in this gate; existing user discovery
results were preserved. No new screenshots taken; prior screenshots remain
historical evidence. Full live/controlled discovery smoke was not repeated.
The first local credential-scan command used system Python without dotenv and
stopped with ModuleNotFoundError; rerunning with the documented backend virtual
environment passed. No dependency installation or source repair was needed.

This gate authorizes the requested checkpoint operation, not a completed Canvas
submission. Record the real assessed SHA after commit in a documentation follow-up.
