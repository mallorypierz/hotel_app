# Startup Prompts

Run these stages in order from the `hotel_app/` root. Stop before installing dependencies, changing scope, or altering Git history unless the user approves.

## 1. Confirm the Project Boundary

Read `AGENTS.md`, `README.md`, `docs/design-pipeline.md`, `docs/verification.md`, and `handoffs/current.md`. Confirm the Git root, branch, HEAD, working-tree status, and frontend/backend/data responsibilities. Do not edit during this stage.

## 2. Check Python and Backend Preparation

Use `backend/.venv/bin/python`. Report the Python version, verify imports for FastAPI, Pydantic, Uvicorn, and pytest, and run `pip check`. Verify standard-library SQLite support with a temporary database that is closed, reopened, read, and removed. If anything is missing, show the exact proposed command and wait for approval before installation.

## 3. Check Node and Vue Preparation

From `frontend/`, report Node and npm versions and run `npm ls --depth=0`. Confirm Vue, Vite, the Vue Vite plugin, ESLint, the Vue ESLint plugin, and browser globals. If anything is missing, show the exact proposed command and wait for approval before installation.

## 4. Verify Part 1

Run the backend tests, frontend lint, and frontend build commands from `docs/verification.md`. Start only missing project services using the documented ports. In the browser, search for `Boston` and confirm four joined trip rows; search for `Aspen` and confirm the no-results message. Check browser-console and API errors. Record expected and observed results, skipped checks, active services, and the next task in `handoffs/current.md`.

Use the `AutoLoop` rules in `AGENTS.md` for an agreed in-scope correction when a check fails.
