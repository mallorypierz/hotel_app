# 06 — Version, Recover, and Share the Booking Feature

Purpose: Preserve a verified booking milestone in Git and provide a safe recovery and sharing path.

## Copyable prompt

```text
Read AGENTS.md, README.md, docs/verification.md, and handoffs/current.md, then inspect Git status, branch, remotes, and the booking-related diff. Do not discard or overwrite unrelated work. Run the relevant backend tests, frontend lint/build checks, and the booking smoke flow before versioning; stop and report failures that make the milestone unsafe. Stage only the verified booking feature and its directly related tests or documentation, show the staged diff, and create a focused commit only when commit authorization is explicit. Create a clearly named recovery branch or tag only when requested, and verify that it resolves to the intended commit. Never force-push or rewrite shared history. Push or create a shareable review only when a destination remote and explicit sharing authorization exist. Report the commit identifier, recovery reference, remote destination, checks performed, and exact recovery commands; otherwise leave Git state unchanged and explain what approval or remote information is still required.
```
