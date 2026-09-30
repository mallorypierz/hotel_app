# Assignment 2, Part 1 — Research and design decisions

**Access and observation date: September 29, 2026 (Eastern).** Research completed before live hotel/map implementation. Read alongside [the acceptance plan](live-hotel-plan.md). Decisions below guide the early mockup and API contract; they are not claims of implemented or tested application behavior.

## Method and evidence labels

- **Observed:** interacted with a public application in the desktop browser and inspected its accessibility tree or rendered screenshot.
- **Documented:** read the linked official documentation; did not exercise that capability in our application.
- **Adopted decision:** a project choice informed by the assignment, observations, or documentation, still requiring implementation and verification.

The two applications were OpenStreetMap and Google Maps. No account settings, bookings, saved places, or reviews were changed. Generic test queries were used, not the student's location. Browser personalization may affect Google results. No account identifiers or private browser details are included here. Screenshots were inspected in-session but are not saved as submission artifacts; the reproducible action log below is the research evidence.

## 1. Existing application inspection

### OpenStreetMap — observed

Source: [OpenStreetMap search](https://www.openstreetmap.org/search?query=02108%2C%20United%20States), accessed September 29, 2026.

| Action/area | Actual observation |
| --- | --- |
| Enter `02108, United States`, then Go | Loading text appeared, followed by a postcode result identifying Beacon Hill/Boston/Massachusetts/U.S.; the leading zero remained visible. |
| Select that result | Screenshot showed a highlighted sidebar row and a red map pin at Boston. The result and map stayed together. Reverse marker-to-list selection was not tested. |
| Missing information | The postcode row contained geographic context, with no hotel price or street address. This was a postcode result, not a test of an incomplete hotel record. |
| Search `zzzxqv-no-such-place-928374` | Loading feedback changed to “No results found”; the viewport remained around Boston. No provider outage was induced. |

Useful: visible geographic hierarchy helps confirm the intended location. Weakness for this assignment: general free-text search does not communicate a five-digit U.S.-only contract. A retained viewport after failure needs clear context. **Adopt:** explicit ZIP label/example, named search center, highlighted selection, and no stale hotel markers after a new unsuccessful search.

### Google Maps — observed

Source: [Google Maps hotel search](https://www.google.com/maps/search/hotels+near+02108/), accessed September 29, 2026.

| Action/area | Actual observation |
| --- | --- |
| Search `hotels near 02108` | Results appeared beside the map, with hotel cards, date/guest controls, ratings, prices, and sponsored entries. |
| Select The Bostonian Hotel Boston from the list | Screenshot showed its highlighted card, hotel details, and highlighted map price marker. |
| Click another visible map price marker | The selected detail heading changed to Boston Marriott Long Wharf. Automatic scrolling/highlighting of its original list row was not verified. |
| Missing information | One official-site offer showed “Get price” instead of a numeric amount. No missing-name/address record was observed. |
| Search `zzzxqv-no-such-place-928374` | The interface said it could not find the query and suggested checking spelling or adding geographic context. No network failure was induced. |

Useful: selection remains identifiable across list, details, and map. Weakness for this project: booking controls and sponsored offers add clutter and imply data our discovery API does not supply. **Adopt:** a simpler shared selection, honest unavailable-field labels, and actionable feedback. Do not copy prices, ratings, or booking controls into live discovery.

### What these inspections do not establish

Neither application was tested under a service outage, quota exhaustion, offline mode, or a screen reader. No conclusion is drawn about their general missing-field policy from one example. Competitor selection behavior is inspiration, not evidence that our required two-way synchronization works. No source-only product feature is presented above as an observed interaction.

## 2. Official geocoding documentation

Source: [Geoapify Forward Geocoding API](https://apidocs.geoapify.com/docs/geocoding/), accessed September 29, 2026. **Documented:** structured `postcode`, `type=postcode`, `filter=countrycode:us`, and `format=json` support this lookup. The response exposes postcode, country code, coordinates, and result type; some fields may be absent. A country bias is not a country restriction.

**Adopted request shape (backend only):**

```text
GET https://api.geoapify.com/v1/geocode/search
postcode=<five-digit string>&type=postcode&filter=countrycode:us&format=json&limit=5
Authentication is added privately by FastAPI; no key is included in this example.
```

**Assignment-driven validation:** trim the input, then require five ASCII digits; never convert to an integer. Accept a postcode candidate only if its returned ZIP equals the requested string and its country is U.S., with finite valid coordinates. Check postcode-level result semantics in the API-contract stage. No usable matching location means no Places request; a mismatched result must never become a substitute center. Treat malformed provider data separately from a legitimate unresolved ZIP. Existing code supplies much of this foundation; see the plan's audit.

## 3. Places search, radius, and limits

Source: [Geoapify Places API](https://apidocs.geoapify.com/docs/places/), accessed September 29, 2026. **Documented:** `accommodation.hotel` is the specific hotel category; the broader accommodation category includes other lodging. A circle filter constrains results; proximity bias orders them. A page supports up to 500 places and `offset` pagination. GeoJSON positions use longitude before latitude. These limits do not promise exhaustive coverage.

**Adopted request shape (backend only):**

```text
GET https://api.geoapify.com/v2/places
categories=accommodation.hotel
filter=circle:<longitude>,<latitude>,5000
bias=proximity:<longitude>,<latitude>
limit=20
Authentication is added privately by FastAPI.
```

**Decision:** one page, at most 20 returned hotels, with no automatic pagination in Part 1. Show the configured cap; when reached, say additional places may exist, not that more definitely exist. Even below the cap, do not claim complete inventory. The center is exactly the validated postcode point. Do not replace the circle with a ZIP boundary, current viewport, traveler geolocation, or proximity bias alone. Coverage and category membership may omit real hotels; geographic records are not evidence of bookable rooms.

## 4. Data honesty and missing fields

These are **project decisions required by the assignment**, not assumptions about competitor or provider guarantees:

- Define an external-place model independent of `HotelStay` and its required nightly price. Keep the provider's identifier, available name/address, and validated coordinates.
- Use “Name not provided” or “Address not provided” when appropriate. Never derive a hotel name from a ZIP or substitute the postcode-center coordinates for missing hotel coordinates.
- Require usable identity and coordinates for synchronized entries. Define a transparent partial-response policy in the contract: report omitted unusable records; if the response cannot produce trustworthy records, show a data error rather than a successful empty search.
- Use one `selectedPlaceId` for list and map. Duplicate names are not sufficient identity. Label markers and list entries consistently; selected state must remain visible without relying solely on color.
- Do not invent prices, ratings, room availability, booking confirmations, or hotel records. Preserve sample booking behavior in its clearly separate section.

## 5. Leaflet and coordinate conversion

Sources: [Leaflet quick start](https://leafletjs.com/examples/quick-start/) and [Leaflet reference](https://leafletjs.com/reference.html), accessed September 29, 2026. **Documented:** Leaflet supports tile layers, markers, popups, event handlers, and circles measured in meters. Direct `L.marker`/`setView` calls use `[latitude, longitude]`; this reverses the provider request/GeoJSON order. Leaflet needs its CSS and a map container with a defined height. Popup strings are HTML, so provider text must not be inserted as raw markup.

The reference documents keyboard-focusable markers, Enter activation, marker alternative text, and keyboard map navigation. **Adopt:** semantic list buttons, descriptive marker names, visible focus, and one selection handler for list/marker actions. Use a distinct center indicator and a 5,000-meter circle; a `circleMarker` sized in pixels is not a distance boundary. Test conversion with known coordinates, bidirectional selection, and keyboard operation. No Leaflet installation occurred during research.

## 6. Tile provider, attribution, and credentials

**Proposed tile provider for the local classroom demo:** OpenStreetMap standard raster tiles at `https://tile.openstreetmap.org/{z}/{x}/{y}.png`. This documented endpoint requires no client API key. Leaflet's [quick start](https://leafletjs.com/examples/quick-start/) uses it directly. Source: [OSMF Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/), accessed September 29, 2026.

**Documented operating conditions:** keep linked “© OpenStreetMap contributors” visible on the map, including mobile layouts; use HTTPS, normal browser identification and a valid Referer; honor HTTP caching. If caching headers cannot be interpreted, retain tiles for at least seven days. Do not disable caches by default, bulk-download, prefetch areas, or offer offline tile downloads. Requests should serve the current interactive viewport. Access may be blocked for violations; treat this shared service as a limited demo dependency, not guaranteed infrastructure.

**Adopt:** use normal browser tile loading, retain attribution, and make the tile URL configurable. For automated repeated checks, stub tile requests instead of driving large map scans. If imagery fails, preserve the textual hotel results and show a map-specific error. Verify actual localhost Referer behavior before declaring the integration ready.

**Separate credential decision:** no frontend tile credential is planned. The existing Geoapify geocoding/Places key stays in backend `.env`, ignored and untracked. Never put it in `VITE_*`, client bundles, tile URLs, browser requests, screenshots, or exception text. If a keyed tile service is chosen later, review its official client-use rules and create a separate restricted browser-intended key; document allowed origins/referrers and permitted use before integration. That change must never reuse the backend secret.

## 7. Geoapify usage, pricing, and attribution

Sources accessed September 29, 2026:

- [Pricing](https://www.geoapify.com/pricing/): Free plan lists 3,000 credits/day and up to 5 requests/second. The quota is credits, not a promise of 3,000 complete two-call hotel searches. It requires attribution, including a follow-link to Geoapify near the supplied information.
- [Pricing details](https://www.geoapify.com/pricing-details/): geocoding costs one credit; a Places request with a limit of 20 or fewer costs one credit. **Planning estimate:** a successful two-request search with our proposed cap uses two credits, excluding unrelated activity. Do not infer larger-page costs from that estimate.
- [Terms and Conditions](https://www.geoapify.com/terms-and-conditions/) (page labeled February 2, 2024, Version 5): users must monitor limits; overloading infrastructure and bypassing metering, including spreading requests across accounts/projects to evade limits, are prohibited. OpenStreetMap attribution is required and Geoapify attribution is mandatory on the Free plan. Availability is not guaranteed.

**Adopted controls:** submit only on Search/Enter; validate locally first; allow one pending search; do not request on keystrokes, selection, pan, or zoom. Make one geocoding request and, only if resolved, one Places request. Keep timeouts and suppress stale responses. Do not auto-retry failures in a loop. Provide an explicit Retry action and honor any retry delay; test rate-limit responses using mocks instead of exhausting quota. Check account usage manually around live demonstrations. No paid plan, account creation, or settings change is needed for this research.

Place a visible “Powered by Geoapify” link near live results plus the required source attribution. The map's tile credit does not replace API data attribution. Keep live requests sparse and use controlled provider responses for repeated tests.

## 8. States to show in the early mockup

These are proposed interface messages and behavior, not observed provider responses.

| State | Proposed treatment |
| --- | --- |
| Initial | Labeled ZIP input, `02108` example, Search button, concise radius explanation. |
| Loading | Announce the requested ZIP; disable repeat submission; do not present old hotels as new results. |
| Invalid input | Explain that five digits are required; make no provider call. |
| Unresolved ZIP | Say the requested U.S. ZIP could not be located; invite another ZIP. No fallback center. |
| Results | Name the returned ZIP center; show count and cap, honest fields, linked attribution, selected list/map state. |
| No nearby results | Say no hotels were returned for this search; retain center/radius context without implying there are no hotels in reality. |
| Failed request | Say search could not be completed; preserve input and offer retry. Distinguish this from a successful empty result. |
| Tile failure | Explain that map imagery is unavailable while keeping successfully retrieved hotel information usable. |

The mockup should show desktop list/map adjacency and a stacked narrow-screen arrangement, with keyboard focus and selection annotations. It must precede implementation and preserve the original design for comparison.

## Completion and limitations

Research inspected two actual applications and current official technical, pricing, usage, and tile-policy sources. No dependencies were installed and no application code or data changed. No live Geoapify request or quota test was made in this stage. Sources were read on the date above; plan terms and documentation can change and should be rechecked if implementation occurs substantially later. Browser findings describe this session only. Our own hotel/map functionality remains unimplemented and unverified.

Next: create the early mockup, then CHECK installed dependencies and obtain approval for any exact installation before TAKE ACTION and VERIFY. The persistent shortlist remains outside Part 1.
