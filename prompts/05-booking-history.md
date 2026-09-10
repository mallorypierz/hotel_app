# 05 — Add and Review Booking History

Purpose: Add a transparent mock booking record and history experience, then review it for correctness and maintainability.

## Copyable prompt

```text
Read AGENTS.md, README.md, the design and verification documents, handoffs/current.md, and the existing booking flow. Inspect the current models, routes, mock data, and Vue state before editing. Add booking history as a small end-to-end feature: retain simulated booking creation through POST /api/bookings, provide a simple FastAPI endpoint for listing mock bookings, and show a clear Vue history view with hotel, room, dates, guest count, total, confirmation identifier, and status. Use Pydantic models and sample data only; do not add authentication, payment processing, external booking services, or database complexity unless explicitly requested. Keep calculations in Python and presentation in Vue, handle empty/error/loading states, and preserve the confirmation flow. Add focused backend and frontend checks, verify that a simulated booking appears once with correct calculated values, review the diff for duplicated records, unstable identifiers, hardcoded component data, and accidental sensitive information, then run the documented verification and report any unverified area.
```
