# 03 — Add Repeatable Verification

Purpose: Make the application checks consistent, documented, and easy for another contributor to rerun.

## Copyable prompt

```text
Read AGENTS.md, README.md, docs/verification.md, and the available frontend and backend scripts before changing anything. Inspect the implemented features and turn their existing checks into a concise repeatable verification workflow without changing dependencies unless approval is obtained. Keep docs/verification.md aligned with the actual commands. Verify backend tests and API startup; frontend lint, build, and startup; hotel search; hotel details; room selection; simulated booking; and confirmation only where those features exist. Confirm that searches return expected mock results and that there are no browser-console or API errors. Do not claim unavailable checks passed: record the exact command, result, failure evidence, and every unverified area. Make only small verification or documentation changes and preserve unrelated application behavior.
```
