# Assignment 2, Part 1 — student recording script

Status: **new screen recording required; no video/link supplied yet.** Aim for
about 2½–3 minutes; confirm the instructor's actual time limit rather than
assuming the previous assignment's limit applies. Use the real checkpoint
version once published. Prior `part2-student-demo.mov`, `part2-demo.m4v`, and
`wayfinder-ui-demo.m4v` are not evidence for this feature.

## Before recording

1. Review [report startup/configuration](../report.md#exact-setup-and-startup).
   Configure the backend privately; do not display `.env` or the provider key.
2. Start/reuse FastAPI on 8010 using the documented `SSL_CERT_FILE=/etc/ssl/cert.pem`
   setting on this Mac, and Vite on 5173. Keep both terminals available so the
   recording can briefly show successful startup, without configuration contents.
3. Open `http://127.0.0.1:5173/`. Make text readable and keep attribution visible.
   Have the assessed SHA handy. Use ordinary browsing for the live segment; no
   intercepted live results. Do not promise a particular hotel count.

## Short sequence and narration

| Approximate time | Screen action | Explain |
| --- | --- | --- |
| 0:00–0:20 | Show successful app startup/localhost and identify feature/version | “Assignment 2, Part 1: live hotel discovery. Bookings below are separate sample workflows.” State recording date and assessed commit. |
| 0:20–0:45 | Enter `02108` in the text ZIP input; submit with Enter; show loading then results | “The leading zero is preserved. FastAPI resolves the exact U.S. postcode before requesting nearby hotels.” |
| 0:45–1:05 | Point to returned ZIP/locality/US, center marker and circle | “This is 5 km around the provider's returned postcode point—not my location or the entire ZIP boundary. Up to 20 records; coverage varies.” |
| 1:05–1:30 | Select a hotel list button, then a different marker (zoom if overlapping) | Show both highlighted states and matching list-row reveal. “Both views identify the same provider place.” |
| 1:30–1:50 | Inspect a name/address, or an actual missing-field label if present; point to credits | “These are provider location fields, not room offers. No invented prices, ratings or availability. Missing text is labeled.” Do not manufacture a missing field in the live segment. |
| 1:50–2:10 | Replace ZIP with `2108`; submit | Show invalid-input feedback and cleared prior results. “Four digits are rejected before a provider request.” This is real local validation, not a simulated provider outage. |
| 2:10–2:40 | Restore `02108` (one deliberate live request), use Tab/Enter/Space on list/marker; resize to about 390 px | Show visible focus, matching selection, map above list and readable attribution. Keep enough time to show the selected list row. |
| 2:40–3:00 | Briefly show Sample stays & bookings, then conclude | “These sample reservations are separate from live places.” Optionally show Boston's four rows or Aspen's no-results state if time permits. |

An optional `16802` live search can replace a repeated `02108` search; it is not
necessary to generate repeated requests solely for the recording. If the provider
fails during recording, describe the actual failure rather than presenting old
results as new. Retry only after any displayed delay.

## Optional error segment — must be labeled simulated

If the rubric requires unresolved/no-hotels/provider/quota demonstrations beyond
invalid input, use a separately prepared controlled browser session based on
[the recorded test fixtures](browser-checks/smoke-provider-results.json) and
[verification script](browser-checks/smoke-extended.cjs). These scripts use an
existing external Playwright/Chrome runtime and are verification tools, not a
production “demo mode”. Do not install tools or change application source just
to create the clip without the project's dependency review.

Display and say **“SIMULATED — controlled response, no live provider outage”**
for the entire intercepted segment. Show the appropriate unresolved, empty,
request-error or temporary-limit response; explain how it differs from live
success. Do not exhaust actual quota or change credentials. Do not claim the
live provider produced the fixture. If no controlled segment is recorded, say
these cases were verified through the linked controlled tests instead.

## What the student must supply

- A **new** screen-recorded file or playable instructor-accessible URL for this
  Part 1 feature, not a previous assignment recording.
- Recording date, duration, assessed code SHA/version, and whether any segment
  used interception; identify the simulated time range if present.
- Confirmation that audio/text is understandable, no credential is visible, and
  the complete recording plays with the instructor's permissions.
- The instructor's actual recording limit/rubric if it differs from this suggested
  sequence. No instructor access or video completion is assumed.

After the recording is supplied, insert its real link/metadata in [report.md](../report.md),
verify access and then finish the submission checklist. No video is generated or
claimed by this script document.
