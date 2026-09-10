# 02 — Build and Connect Hotel Search

Purpose: Implement the first complete frontend-to-backend feature using joined CSV data and a small, reviewable API surface.

## Copyable prompt

```text
Read AGENTS.md, README.md, docs/design-pipeline.md, docs/verification.md, and handoffs/current.md, then inspect the existing frontend, backend, and CSV data before editing. Build a city-search vertical slice. Python must read hotels.csv and trips.csv and join their records through hotel_id. FastAPI must validate the city query and return matching joined stays. Vue must provide one city input, a Search button, a plain table with clear labels, and a clear no-results message. Preserve the frontend/backend boundary, do not change dependencies, run backend tests and frontend lint/build, and check a successful and no-results search in the browser.
```
