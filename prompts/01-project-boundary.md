# 01 — Create the Project Boundary

Purpose: Establish the repository structure, responsibilities, constraints, and approval boundaries before feature work begins.

## Copyable prompt

```text
Read AGENTS.md, README.md, and the existing documentation, then inspect the project structure and Git state. Confirm the project root and establish a clear boundary for the Expedia-style hotel booking replica: Vue owns screens and user interactions in frontend/; Python owns calculations and backend logic in backend/; FastAPI carries requests and results between them; and sample data belongs in data/. Keep frontend and backend separate, prefer small focused changes, preserve unrelated work, and do not add, remove, or upgrade dependencies without approval. Do not add authentication, real payments, external booking APIs, or unnecessary database complexity. Document any setup or architecture changes in the root README and report the exact files changed and checks performed.
```
