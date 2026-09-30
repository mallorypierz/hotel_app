# Public API ZIP demonstration — September 24, 2026

## Implementation

The backend loads the project-root .env through python-dotenv. The key stays
in the backend and .env is Git-ignored. No key or .env contents are included here
or in the screenshots.

GET /api/health returns:
```json
{"status":"ok","geoapify":"key is configured"}
```
This status describes configuration; the successful live requests below also
establish that Geoapify accepted the key during verification.

GET /api/demo/zip-location defaults to ZIP 16802. The optional postcode query
parameter accepts exactly five ASCII digits, including leading zeros.
For example: http://127.0.0.1:8010/api/demo/zip-location?postcode=02108

Vue starts with 16802 in an editable ZIP input. Clicking Look up ZIP sends the
entered value to FastAPI, which requests real Geoapify data. The result table
contains ZIP code, locality, country, latitude, and longitude. The form includes
loading feedback and safe error messages. Invalid ZIP values are rejected before
provider access. Missing configuration returns 503, unresolved ZIPs 404, provider
failures 502, and invalid query values 422.

The controller in backend/app/geocoding.py requests Geoapify forward geocoding
with type=postcode, filter=countrycode:us, and format=json. It requires a matching
postcode, U.S. country code, and finite coordinates within valid bounds.
Provider URLs and exception details are never returned to the browser.

## Verification

- Backend: 55 tests passed in 0.34s. Provider unit tests use mocks; live checks
  are recorded separately below.
- Frontend lint passed without warnings; production build passed (17 modules).
- Direct backend URL test using curl: GET /api/demo/zip-location returned HTTP
  200 with postcode 16802, locality State College, country us, latitude
  40.803167822, longitude -77.861384958.
- Browser: submitted default ZIP 16802 and observed the five labeled table
  columns with that live response.
- Browser: changed input to 02108 and submitted; observed Boston, US,
  latitude 42.357581412, longitude -71.065946589, with the leading zero retained.
- Browser console: no warnings or errors during successful ZIP checks.
- Running health endpoint: HTTP 200, key is configured.
- The original 502 was caused by this Python installation missing its default
  trusted CA bundle. Starting with SSL_CERT_FILE=/etc/ssl/cert.pem resolved it;
  certificate verification remains enabled. See README for the launch command.
- Opening port 8010 directly in the in-app browser was blocked by that browser.
  The direct URL was verified with curl; frontend browser requests succeeded
  through Vite's /api proxy.
- No dependencies added or upgraded in this completion step.

## Submission evidence

Use either screenshot (both were visually inspected; neither contains a key):

- [ZIP 16802 screenshot](zip-16802.png)
- [Entered ZIP 02108 screenshot](zip-02108.png)

Suggested Canvas statement:

> The backend health check reports status "ok" and Geoapify "key is configured".
> I tested the backend URL with ZIP 16802 and used the Vue ZIP input to request
> real Geoapify location data. The screenshot shows the entered ZIP and returned
> location table. The API key is kept in the backend and is excluded from this
> submission.

Upload one screenshot and the statement to Canvas. The student must still
complete/confirm the TA or instructor demonstration and submit the evidence.
No Canvas submission was made by the coding agent.

Not tested: physical mobile devices, other browsers, or Canvas access.
