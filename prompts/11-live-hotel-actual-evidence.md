# Selected actual prompt excerpts — Assignment 2, Part 1

These are verbatim excerpts from student messages in the implementation,
verification, repair and submission-preparation conversation on September 29,
2026. They are selected excerpts, not a complete transcript. The earlier
[sequential prompt guide](10-live-hotel-search.md) is a prepared workflow and is
not itself proof that every prompt was sent. Earlier preparation/research stages
are evidenced separately by their saved artifacts/handoff.

## P1 — Backend implementation

> Accept ZIP codes as five-digit strings so 02108 retains its zero. Reuse or extend the existing geocoding logic to require the requested postcode and U.S. country code; never substitute a different location.

> Failures must not become successful empty lists.

Applied in [geocoding](../backend/app/geocoding.py),
[discovery controller](../backend/app/discovery.py),
[models](../backend/app/discovery_models.py), and
[controlled tests](../backend/tests/test_discovery.py).
Decision: exact U.S. postcode-level center before Places; separate external
places; unusable pages fail. See [contract](../docs/live-hotel-plan.md) and
[backend verification/correction](../docs/live-hotel-verification.md).

## P2 — Vue interface

> Use the provider place ID as the shared selection identity: selecting a list item highlights its marker, and selecting a marker identifies and reveals the corresponding list item. Make selection operable with a keyboard.

> Prevent stale responses or old markers from appearing to belong to a new search.

Applied in [discovery parent](../frontend/src/components/HotelDiscovery.vue),
[list](../frontend/src/components/DiscoveryList.vue),
[map](../frontend/src/components/DiscoveryMap.vue), and
[request composable](../frontend/src/composables/useDiscovery.js).
Decision: a shared ID with marker/list pressed states; abort plus request-version
checks. [Design refinements](../docs/live-hotel-design.md) and
[controlled browser evidence](../docs/browser-checks/discovery-results.json)
record genuine Leaflet initialization and Enter-handler corrections.

## P3 — Verification without repair

> In this verification pass, do not change source code.

> Use controlled test responses or request interception for invalid/unresolved ZIP, mismatched-country/postcode resolution, no hotels, provider failure, and quota/rate-limit errors. Do not exhaust the live API or depend on a fixed live result count. Label simulated checks clearly.

[Smoke record](../docs/live-hotel-verification.md),
[initial result including failures](../docs/browser-checks/smoke-extended-results.json),
[upstream fixtures](../docs/browser-checks/smoke-provider-results.json), and
[integrity evidence](../docs/browser-checks/smoke-integrity-results.json).
The actual favicon defect was reported without source repair during that pass.
Incorrect test assumptions about a traveler locator/empty history were recorded,
then rechecked correctly; pre-existing booking rows were not deleted.

## P4 — Approved focused D1 repair

> Focus on D1: add and reference a local favicon without new dependencies. Verify its URL returns 200, confirm a fresh browser load has no favicon console error, and rerun frontend lint/build and affected smoke checks using controlled responses.

Applied as one [HTML icon reference](../frontend/index.html) and a
[local SVG](../frontend/public/favicon.svg). [Fresh-load result](../docs/browser-checks/d1-favicon-results.json)
and [16-scenario recheck](../docs/browser-checks/d1-regression-results.json)
close the failure. The earlier `/favicon.ico` 404 evidence remains preserved.

## P5 — Submission preparation

> Preserve the previous assignment report before updating report.md, and keep its relative artifact links working.

> Leave the assessed commit explicitly pending until a real checkpoint exists.

Applied in the byte-identical root-level [previous report](../report-previous-assignment-part2.md),
[new report](../report.md), [recording script](../docs/live-hotel-demo-script.md),
and [explicit checkpoint plan](../docs/live-hotel-checkpoint.md). No checkpoint,
push, video, instructor access or Canvas submission was fabricated.

## P6 — Student model confirmation

Asked for the exact selected Codex model and other AI-tool use. Student replied:

> gpt 6 astra medium

The disclosure records **GPT-6 Astra, medium reasoning**, attributed to this
student confirmation. No model for an unverified separate session is invented.
Additional outside AI tools were not specified in this reply and should be
added by the student if used.


## Student refinement: one ZIP search

> one change: the zip lookup needs to be in the same area of the webpage as the live hotel zip code discovery. there should only be one zip code lookup search box.

Removed the standalone ZIP panel mounting from App.vue and clarified the live
discovery introduction. Preserved legacy endpoint/source. See the dated
[single-form verification](../docs/live-hotel-verification.md) and
[design refinement](../docs/live-hotel-design.md). Lint/build and focused browser
validation passed; no new live-provider claim was made.
