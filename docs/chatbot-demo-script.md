# Revised Part 2 demonstration script

Prepared October 8, 2026. This is the planned demonstration guide. The student
subsequently supplied a [recording, published October 9](https://github.com/mallorypierz/hotel_app/releases/tag/assignment2-part2-demo-2026-10-09)
(replacement recording: approximately 55 seconds). Publication/access verified; full correspondence with
this script has not been reviewed. The steps below remain the original guide.

## Prepare privately, before recording

Read [report status](../report.md) and [verification](chatbot-verification.md).
Privately configure the backend-only key/model according to README, then restart
only this project's services. Do not show `.env`, key-bearing terminal history,
provider dashboards, personal browser tabs or raw headers. Verify the actual
assessed commit after an authorized checkpoint; if none exists, say “uncommitted
working tree” instead of showing the old storage SHA as the chatbot commit.

Use a separate isolated demo database for save/remove demonstrations so existing
student records stay intact. Run the fixed-fixture loader and isolated startup
commands in the verification document. The fixture is simulated and all provider
responses captured by that loader are mocks. End that segment, stop its server,
then deliberately start the normal app against actual saved hotels for the live
segment. Never use a mocked browser route or an empty-key test server during a
segment labeled live. Do not run two backends on port 8010.

No duration/rubric compliance is assumed; adjust timing to the supplied course
requirements. Suggested order:

## 1. Identify the app, version and boundaries

Show the application and actual assessed commit/working-tree status. Say:
“Wayfinder preserves ZIP discovery, the synchronized list/map and sample bookings.
Part 2 saves hotel records locally and answers questions about simulated nightly
data. It does not make real reservations.” Show the simulated-data label.

## 2. Local saving, duplicate protection, removal and persistence

Clearly label **isolated demo data**. Search a ZIP with no saved matches and show
the discovery response/list/map and attribution. State whether discovery is a
real Geoapify request or a controlled response; never imply controlled hotel
names are live results. Add one hotel, show Saved locally, and repeat search to
show local-first results. Explain that duplicate identity is prevented and edited
nightly values are retained. Existing [controlled tests](chatbot-verification.md)
prove duplicate API requests; do not manufacture additional click behavior.

Refresh; saved hotel/nights remain. Restart the isolated backend and refresh;
show the same records. Save a second test hotel, remove it, refresh/restart, and
show it remains absent. Limit removal to records created for this segment.
Show Boston's four joined sample rows and Aspen's no-results feedback. Briefly
show sample booking history if time permits; any demonstration mutations belong
only in the isolated database.

## 3. Successful LIVE chatbot question — recording pending

Switch explicitly to the normal backend and actual saved hotels, with configured
OpenAI credentials. Announce “Live OpenAI request; simulated hotel rates.” Confirm
provider/model remains OpenAI / `gpt-4.1-mini-2025-04-14`. Use the actual saved
records, not the fixed fixture, and inspect them before stating expectations.
Verified live October 9 (recheck saved data before recording), use:

> Which saved hotels in 06109 have one room from 2026-10-10 to 2026-10-12 for $350 total or less?

Show typing and Send, loading, then the actual result. If data is unchanged,
Comfort Inn should total $300 ($200 + $100), checkout Oct 12 excluded, minimum
15 rooms. These are **expected**, not prerecorded observed results. If the call
fails, retain its safe error and label this live attempt unsuccessful. Do not
replace it with a mock screenshot or switch providers/models.

## 4. Expand the evidence panel

Open **How this answer was produced** with keyboard or pointer. Show the original
question, actual proposed SQL and bound dates/ZIP, validation outcome, all retrieved
nightly records, completeness/truncation and exact provider/model. Explain first
request → proposed SQL → local read-only retrieval → second request with question
and records → grounded answer. Both completed model stages should be visible.

Read the two requested nightly values and room counts; compare their sum/minimum
to the displayed total/availability. Show that no checkout-night price is included.
Explain the recommendation reason and saved-subset limitation. Keep the evidence
readable long enough to inspect; no editable SQL or Execute button is present.

## 5. LIVE no-match or insufficient-data case — recording pending

For unchanged actual saved data, ask:

> Which saved hotels in 06109 have one room from 2026-10-10 to 2026-10-12 for $1 total or less?

Expected: no_matches because $300 exceeds $1; record the actual answer and both
stages. Alternatively request Oct 14–16, 2026, one room: Oct 15 is not stored,
so availability/full cost cannot be assumed. Explain any difference using the
retrieved evidence. Capture genuine observed output, not the expectation alone.

## 6. CONTROLLED rejected-query check

Transition visibly to “Controlled security check — fixed fixture, no live model
call, disposable database.” From the project root run:

```sh
backend/.venv/bin/python docs/browser-checks/chatbot-rejected-evidence.py
```

Show the three proposals (write, unauthorized booking read, multiple statements),
`query_rejected` results, per-attempt before/after SHA256 and unchanged-table/schema
flags. The script creates a temporary DB from the fixed fixture and deletes it
on exit. Do not paste destructive SQL into a live database client. The chatbot
UI deliberately has no arbitrary SQL execution interface.

## 7. Close and publish evidence honestly

Show report links to dated research, original early mockup, design changes,
fixture, verification and AI log. State any live failure or unverified access.
Stop only services started for the demonstration unless asked to leave them up.
After reviewing the actual recording for secrets/readability, add its real URL,
recorded date, duration and assessed code version to report.md. Verify public or
instructor-authorized access without claiming to impersonate the instructor.
Do not fill any missing URL/commit with a placeholder that looks real.
