# Chatbot provider research — OpenAI API

Researched October 8, 2026 (Eastern). Documentation and design only: no model
requests, credential inspection, dependency changes or application implementation.
This extends [the audited plan](chatbot-plan.md). The student explicitly selected
OpenAI as the only provider; Gemini, OpenRouter and Nemotron are out of scope.

## Provider and exact model decision

Use **`gpt-4.1-mini-2025-04-14`** for both requests, through the Responses API.
The current official catalog lists this dated snapshot, Responses support and
Structured Outputs support. It lists standard text prices of **$0.40 input,
$0.10 cached input and $1.60 output per million tokens**; the free usage tier is
unsupported. The alias `gpt-4.1-mini` exists, but this project will pin the dated
snapshot. [Official model page](https://developers.openai.com/api/docs/models/gpt-4.1-mini)

Design judgment: a small, bounded SQL/answer task warrants an inexpensive
documented model with a fixed snapshot. This is not a claim that it is the latest
or best model, or that its SQL is safe or accurate without verification. Keep
the selected ID explicit in configuration and evidence. If unavailable or
inadequate in tests, report the issue; do not silently switch model/provider.
Catalog availability is established; this student's project access, balance,
rate limits and successful live calls are **not verified**.

Illustrative cost calculation, not measured usage: across both requests,
4,000 uncached input tokens and 1,000 output tokens cost
`4000 × 0.40 / 1000000 + 1000 × 1.60 / 1000000 = $0.0032`.
One hundred such interactions would be $0.32, excluding retries and any other
usage. Actual input includes instructions, schema and records. Record returned
usage separately for each call. No caching discount, free credits, or subscription
entitlement is assumed. Use standard foreground text requests without paid
hosted tools. Recheck prices before a later deployment or large run.

## HTTP request and response contract

Send backend HTTPS `POST https://api.openai.com/v1/responses` with
`Content-Type: application/json` and `Authorization: Bearer <server key>`.
Use `model`, `instructions`, and `input`; inspect the returned `output` array
for assistant messages and `output_text` content rather than assuming its first
element contains the answer. SDK `output_text` is a convenience property, not
the raw REST parsing contract. [Text generation guide](https://developers.openai.com/api/docs/guides/text)

The server loads the key from an environment variable; it never enters browser
code or query parameters. [Authentication reference](https://developers.openai.com/api/reference/overview#authentication)

Proposed common body fields: pinned `model`, task-specific `instructions`,
`input: [{"role":"user","content":"<question or serialized data envelope>"}]`,
`store: false`, `stream: false`, and `max_output_tokens: 1800`.
Do not use conversation IDs, `previous_response_id`, hosted tools or background
jobs: the backend explicitly constructs each request. The response carries status,
output and usage; reject incomplete/failed responses before interpreting results.
[Responses create reference](https://developers.openai.com/api/reference/cli/resources/responses/methods/create)

Use strict Structured Outputs through
`text.format = {type: "json_schema", name: "hotel_query", strict: true, schema: ...}`.
Its supported JSON Schema subset requires an object root, required properties
and `additionalProperties: false`; nullable properties can express optional
values. Handle refusals and incomplete output separately. Schema adherence does
not establish factual correctness or safe SQL.
[Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs)

Project proposal for request 1's schema (to finalize before implementation):

```json
{
  "type": "object",
  "properties": {
    "kind": {"type": "string", "enum": ["query", "clarification"]},
    "sql": {"type": ["string", "null"]},
    "parameters": {
      "type": "array",
      "items": {"type": ["string", "integer", "number", "null"]}
    },
    "clarification": {"type": ["string", "null"]}
  },
  "required": ["kind", "sql", "parameters", "clarification"],
  "additionalProperties": false
}
```

Use positional `?` SQLite parameters. Pydantic additionally enforces consistent
branches, sizes and parameter counts; no execution for clarification. Future
contract work must include machine-checkable stay intent (dates, room count,
budget meaning) so valid-but-wrong SQL cannot pass merely by returning JSON.
For request 2 propose a strict object with `status` (answer/no_matches/
insufficient_data), `answer`, and `hotel_ids`; check IDs against retrieved rows.
These are proposed schemas, not live-tested API responses.

We choose a structured proposal returned as data, not a tool with automatic
database access. The backend alone validates and executes SQL. Keep SQL
authorization, query-only connection, bounded execution and stay semantics from
the plan even when the model returns perfectly formatted JSON.

## Exactly what leaves the backend

| Stage | Data sent to OpenAI | Data kept local |
| --- | --- | --- |
| Request 1: propose SQL | Original bounded question; relevant schema names/types/relationships; allowed query rules; simulated-data and date/budget rules; output schema. | All database rows, database file/path, sample users/bookings, credentials, browser storage and unrelated files. |
| Local retrieval | No network request. Backend validates the proposal and executes a restricted local SELECT. | SQLite and execution authority stay on this machine. |
| Request 2: grounded answer | Original question again; bounded relevant retrieved records; verified stay context/aggregates; row-limit/completeness metadata; simulated-data warning; grounding instructions and answer schema. | Nonmatching/unneeded rows, whole tables/database, sample travelers/bookings, secrets and unrelated chat history. |

Request 1 schema concerns only `saved_hotels`, `saved_hotel_locations` and
`demo_hotel_nights` as documented in the plan. No example real rows are needed.
Propose an exposed column allowlist focused on hotel ID/name/address,
ZIP/locality/country, stay date, rate cents and rooms available. Geographic
coordinates exist in storage but are not needed for the initial ZIP/date/cost
questions; do not expose them to this chatbot unless a later requirement needs
them. Do not advertise excluded columns as queryable.

For request 2, hotel IDs, names, relevant location labels and nightly values may
leave the machine only when retrieved for the question; omit addresses unless
needed for identification. Proposed limits: question 2,000 characters, up to
50 retrieved rows and 24 KiB serialized records, at most 14 requested nights.
An oversized or incomplete evidence set must be narrowed or clearly labeled;
never imply an exhaustive comparison after truncation. Final limits belong in
the mockup/API contract. Include nightly rows or checked aggregates sufficient
to verify the total; checkout is excluded and absent nights are not available.

This means the existing Comfort Inn's edited simulated values could be sent in
request 2 for a matching question. **None were sent in this research step.**
Treat questions and hotel text as untrusted data. Ask users to omit personal or
payment information; the original question itself is transmitted.

Set `store: false` on both calls. This is not a promise of zero retention:
OpenAI documents abuse-monitoring retention up to 30 days by default and
separate application-state/caching rules. API data is not used for training by
default unless the customer opts in. Do not claim this project has approved
Zero Data Retention. [Data controls](https://developers.openai.com/api/docs/guides/your-data)

## Rate limits, timeout and failure design

Limits depend on the model and account/project; inspect the student's Limits
dashboard privately later rather than hardcoding catalog tiers. Relevant response
headers include `Retry-After`, `x-ratelimit-remaining-requests`,
`x-ratelimit-remaining-tokens`, and their reset headers. Temporary rate limiting
and overload can require delay; quota/billing errors need user action instead.
Bounded exponential backoff with jitter is appropriate if retries are introduced.
[Rate-limit guide](https://developers.openai.com/api/docs/guides/rate-limits)

Distinguish invalid requests/authentication/access errors, temporary 429 rate
errors, exhausted-credit/spend-limit 429 errors, 5xx failures and network timeout.
Inspect sanitized status/type/code, not status alone. The error guide documents
timeout handling but does not establish a universal service completion deadline
for this project. [Error guide](https://developers.openai.com/api/docs/guides/error-codes)

Project decisions, not OpenAI guarantees:

- Start with zero automatic retries: at most two model calls per completed
  question. Failed first call/query stops before call 2; failed call 2 displays
  failure, never an invented answer. A user retry may incur another charge.
- Propose 20-second socket-operation timeout per provider call and a 45-second
  overall backend deadline; frontend waits slightly longer (50 seconds).
  Standard-library socket timeout is not a total wall-clock deadline: implement
  deadline-aware bounded reads, check remaining budget before call 2, and verify
  timeout behavior. Do not promise cancellation of remote billing on disconnect.
- Bound provider body reads (proposed 256 KiB), output tokens and SQL work. One
  in-flight question per UI. Respect a valid Retry-After before user retry;
  never silently shorten a server-directed wait to fit an automatic retry.
- Log request ID, stage, status and token counts for diagnosis; redact headers,
  raw provider errors and unnecessary question/record content. A missing key or
  inaccessible model yields a safe configuration/access error, no fallback.
- Use mocks for quota, timeout, refusal, invalid JSON/schema, incomplete output,
  unsafe SQL and second-call failure. Later make a small intentional live test
  and document both successful model calls separately from mocks.

## Private backend configuration — planned, not yet implemented

No OpenAI variables are currently read by application code. These proposed names
will be added to backend configuration during implementation:

| Name | Purpose / proposed value |
| --- | --- |
| `OPENAI_API_KEY` | Secret project API key, set privately by the student. |
| `OPENAI_MODEL` | `gpt-4.1-mini-2025-04-14`; enforce explicitly, no fallback. |
| `OPENAI_TIMEOUT_SECONDS` | `20`; backend transport setting, not a provider SLA. |
| `OPENAI_MAX_OUTPUT_TOKENS` | `1800` per call, validated by backend. |

Private preparation instructions:

1. In the [OpenAI API dashboard](https://platform.openai.com/), choose/create
   the intended project, inspect billing and limits, and create its API key.
   Verify model access when implementation is ready; do not post the key in chat.
2. Privately edit the existing project-root `.env` in your local editor. Add
   `OPENAI_API_KEY` with your secret and the nonsecret settings above. Preserve
   `GEOAPIFY_API_KEY` and all existing configuration. Do not run an `echo` command
   containing the key or capture the editor in recordings.
3. Check tracking using `git check-ignore .env` and `git ls-files .env` without
   reading values: the first should identify `.env`; the second should be empty.
   Never place these variables in frontend `.env`, `VITE_*`, source, reports,
   screenshots or command-line arguments. No tracked file should contain a key.
4. After implementation, the existing `python-dotenv` pattern will load the
   root file; process environment takes precedence. Restart only the project's
   backend to pick up changes. Retain documented TLS verification and this Mac's
   `SSL_CERT_FILE=/etc/ssl/cert.pem` startup setting; never disable verification.
5. Later verify configured/unconfigured status without exposing the value, then
   one live question. Account access and a successfully configured key are not
   established by this document or by merely defining environment variables.

## Dependencies and next step

Reuse installed Pydantic 2.13.5/python-dotenv 1.2.3 and Python
`urllib.request`, `urllib.error`, `json`, `ssl`, `socket`, `time` and `sqlite3`.
An OpenAI SDK is unnecessary for two bounded HTTP requests. Implement transport
in a separate backend adapter so Geoapify behavior remains frozen. Keep response
parsing, error handling and limits explicit because SDK conveniences are absent.

No install command is proposed; no dependency was added, removed or upgraded.
If later tests establish a package is needed, first inspect installed/locked
versions, explain the exact proposed package/version, command, purpose and files,
obtain student approval, then install and verify only that change.

Next: create the early chatbot mockup and finalize the contract, then implement
the read-only retrieval boundary before the two-request adapter/orchestration.
No README run instructions change yet because application setup is unchanged.

## Research verification and limitations

All official source pages linked in the technical sections were opened on
October 8, 2026. General Responses create links failed in the research browser;
the official CLI create reference and text/Structured Outputs guides were
accessible and used instead. Markdown page variants also failed to render;
HTML sources were used. No successful live API call is claimed.

Only documentation is edited. The earlier plan/handoff work remains preserved.
No .env contents read, credentials requested, data sent to a model, tests rerun,
services restarted, database writes, commit or push. Code tests are unchanged;
the prior 166-test/lint/build baseline remains historical evidence for this step.
