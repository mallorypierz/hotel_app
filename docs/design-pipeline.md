# Design Note

The Vue frontend owns the city input, Search button, request states, and results table. FastAPI validates `GET /api/hotels?city=...` and carries JSON between Vue and Python. Python reads `hotels.csv` and `trips.csv`, joins them through `hotel_id`, and filters the joined stays by city.

## File Map

```text
hotel_app/
├── AGENTS.md                  # Project rules and workflow triggers
├── README.md                  # Project overview, stack, and setup guidance
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI application and routes
│   │   ├── models.py          # API and hotel data models
│   │   └── repository.py      # Mock-data loading and search logic
│   ├── tests/test_hotels.py   # Focused hotel-search tests
│   └── requirements.txt       # Python dependency versions
├── data/
│   ├── hotels.csv             # Sample hotel details
│   └── trips.csv              # City stays joined through hotel_id
├── docs/
│   ├── design-pipeline.md     # File map and request flow
│   └── verification.md        # Repeatable project checks
├── frontend/
│   ├── src/
│   │   ├── components/        # City search and hotel table components
│   │   ├── App.vue            # Search screen and request state
│   │   └── main.js            # Vue entry point
│   ├── package.json           # Frontend dependencies and scripts
│   ├── package-lock.json      # Locked frontend dependency graph
│   └── vite.config.js         # Vue plugin and API development proxy
├── handoffs/
│   ├── create-handoff.md      # Prompts for creating and resuming handoffs
│   └── current.md             # Current state for the next contributor
└── prompts/
    ├── 01-project-boundary.md       # Architecture and scope
    ├── 02-hotel-search.md           # Connected search feature
    ├── 03-repeatable-verification.md # Repeatable checks
    ├── 04-visual-redesign.md        # Reference-led UI work
    ├── 05-booking-history.md        # Booking history feature
    ├── 06-version-recover-share.md  # Git milestone workflow
    ├── 07-durable-context.md        # Context refresh workflow
    └── 08-part-1-city-search.md     # Submitted Part 1 requirements
```

Local generated directories such as `backend/.venv/`, `frontend/node_modules/`, and `frontend/dist/` are omitted from the map.

## Request Flow

```text
User
  |
  | city search input
  v
Vue screen (frontend/)
  |
  | HTTP request
  v
FastAPI route (backend/)
  |
  | validated input
  v
Python CSV join / mock data
  |
  | result
  v
FastAPI response
  |
  | JSON result
  v
Vue screen
  |
  v
User
```

Store sample application data in `data/`. Record only major, reusable project prompts in sequentially numbered files under `prompts/`.
