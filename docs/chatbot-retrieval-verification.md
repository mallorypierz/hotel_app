# Read-only chatbot retrieval boundary

Implemented and verified October 8, 2026 (Eastern), before any LLM integration.
Acceptance: an untrusted SQL proposal can read only approved saved-hotel columns
within enforced work/result bounds; it cannot modify SQLite or read Assignment 1
tables. **Passed on the local Python 3.12.5 / SQLite 3.45.3 environment.**

## Scope and contracts

- [chat_models.py](../backend/app/chat_models.py): strict Pydantic input/output.
- [chat_queries.py](../backend/app/chat_queries.py): syntax contract, native
  authorization, resource limits, local execution and fixed safe errors.
- [chat_controller.py](../backend/app/chat_controller.py): internal retrieval
  dispatch using the existing server-configured database path.
- [test_chat_queries.py](../backend/tests/test_chat_queries.py): 90 isolated
  tests, including parameterized malicious proposals and preservation checks.

No route was added: there is deliberately no public raw-SQL endpoint. Later
chat routes must dispatch through a separate controller and this boundary,
rather than adding provider logic or SQL execution to routes or Vue. Existing
routes, storage controllers, migrations, frontend and dependencies are unchanged.

The only accepted proposal shape is an object with both fields, no extras:

```json
{
  "sql": "SELECT hotel_id, name FROM saved_hotels WHERE hotel_id=?",
  "parameters": ["example-provider-id"]
}
```

Only positional anonymous `?` bindings are supported. Strings retain leading
zeros and exact identity. Parameters are a JSON array of string, signed 64-bit
integer, finite float or null; booleans, binary data, objects and nested arrays
are rejected. Even preconstructed Pydantic model instances are revalidated.
The proposal cannot set a path, authorization policy, deadline or result limit.

Only statements beginning with SELECT (case-insensitive, leading whitespace
allowed) are accepted. Joins, subqueries, EXISTS, grouping, ordering and bounded
compound SELECTs can be used subject to native authorization. Initial v1 excludes
WITH/CTEs, EXPLAIN proposals, leading comments and named/numbered parameters.
Comments within a SELECT and quoted strings containing marker-like text are
supported. SQLite preparation and single-statement execution validate SQL;
the small lexical check is not the security boundary.

## Data permissions

| Table | Allowed columns |
| --- | --- |
| saved_hotels | hotel_id, name, address |
| saved_hotel_locations | hotel_id, postcode, country_code, locality |
| demo_hotel_nights | hotel_id, stay_date, nightly_rate_cents, rooms_available |

Coordinates, implicit rowid, sample hotels/trips/users/bookings/metadata,
schema tables, attached databases, views and table-valued PRAGMA access are
excluded. A denied read in WHERE, ORDER BY, a subquery or UNION is still denied;
column restrictions are not limited to the projected output list.

Allowed functions: count, sum, min, max, avg, coalesce, ifnull, nullif, lower,
upper, length and like. All other functions/actions are denied by default.
No extensions, custom functions, file access or remote tools are registered.
The authorizer returns DENY, never IGNORE (which could silently replace data
with NULL). SQLite also reports table-only reads for COUNT/EXISTS with an empty
column name; only approved tables receive permission for that special case.
[SQLite authorization documentation](https://www.sqlite.org/c3ref/set_authorizer.html)

## Protection layers and bounds

Every retrieval creates and closes a fresh URI `mode=ro` connection, without
calling initialization/migrations or the existing writable connection helper.
The path is selected by backend code, encoded with `Path.as_uri()`, and never
accepted from the proposal. A missing file is not created. Configure query_only,
defensive mode, untrusted schema, disabled views, disabled double-quoted string
fallback and disabled extension loading before installing a default-deny
authorizer. This Python build lacks `enable_load_extension()`, so the supported
`setconfig(SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION, False)` explicitly disables it.
This implementation requires Python 3.12 and the SQLite config capabilities
available in the audited runtime; other builds are not yet verified.

First compile `EXPLAIN <proposal>` through the restricted connection. This lets
SQLite authorize access, check bindings and reject multiple statements before
stepping the original query. Keep the same authorizer installed during actual
execution and possible re-preparation. Never use executescript. A trace test
confirms prohibited/multiple-statement proposals never execute their original
SELECT. [Python SQLite reference](https://docs.python.org/3.12/library/sqlite3.html)

| Limit | Value / outcome |
| --- | --- |
| Proposal SQL | 8,192 UTF-8 bytes; empty/NUL-containing text rejected |
| Bindings | 32 maximum; each string at most 2,048 UTF-8 bytes |
| SQLite value/row length | 32 KiB |
| Result columns | 24; duplicate names rejected; each name at most 128 UTF-8 bytes |
| Expression depth / compound terms | 32 / 8 |
| Compiled VM program | 25,000 operations |
| Attachments / SQLite worker threads | 0 / 0 |
| Execution work | Approximately 100,000 VM steps, checked every 100 |
| Deadline / database lock wait | 0.5 seconds cooperative deadline / 0.1 seconds busy timeout |
| Result rows | 50, independent of proposed LIMIT; a 51st row rejects the entire result |
| Serialized evidence payload | 24 KiB for compact UTF-8 JSON of columns + records; includes JSON escaping |

Use a progress callback during preparation/execution and deadline checks before
execution, during collection and at completion. Returning nonzero from the
callback interrupts work. [SQLite progress documentation](https://www.sqlite.org/c3ref/progress_handler.html)

Do not return partial records on any failure or overflow. Result records allow
only finite JSON scalar values; binary output is rejected. Successful results
include columns, records, row_count, row_limit and result_bytes. An explicit SQL
LIMIT may select a subset; success does not mean all saved hotels were examined.
In particular, row_limit is a safety cap, not a claim about inventory completeness.

Fixed error codes/messages: `invalid_proposal`, `query_rejected`, `query_limit`,
`storage_unavailable`. They contain no raw SQL, parameters, SQLite errors or
filesystem paths. Invalid proposals fail before opening a connection. Native
authorization rejects forbidden proposals at preparation; safe SELECTs that
exceed runtime/result bounds are interrupted/discarded after bounded read work.
Future HTTP code must expose only these safe messages, not exception internals.

## AutoLoop record and expected versus observed

1. Initial implementation and targeted suite: **85 passed, 5 failed in 0.71s**.
   COUNT-only and cross-join tests were rejected prematurely. Inspection of an
   isolated SQLite callback showed `(SQLITE_READ, 'saved_hotels', '', None, None)`:
   this runtime omits the database name for a table-only read.
2. **Correction cycle 1:** permit that empty-column, omitted-database event only
   for the three approved tables. Ordinary column reads still require `main`.
   A fresh connection has no temp tables/attachments and cannot create them.
3. Targeted rerun: **90 passed in 0.65s**. Full regression: **256 passed in 1.08s**.
   Stop: acceptance met; no additional correction cycle or dependency change.

| Input/check | Expected | Observed |
| --- | --- | --- |
| Isolated fixture: 06109, Oct 10–12, 2026, one room, $350 total | Only Example Birch qualifies: 2 nights, 26000 cents, minimum 2 rooms; unavailable and missing-night hotels excluded | Exact expected row |
| Same query at $250 total | Zero eligible rows | Empty records |
| A hotel associated with two ZIPs | ZIP EXISTS avoids doubling total/nights | Still 26000 cents / 2 nights |
| Null metadata, mixed-case SQL, exact ZIP and parameter injection string | Preserve NULL and strings; bind injection as data | Passed |
| Writes/schema changes, ATTACH/DETACH, PRAGMAs, views, sample/schema table reads, excluded columns/functions, compound injection | Safe rejection, no mutation | Passed |
| Invalid types, huge/nonfinite parameters, extra path/limit fields, constructed invalid model | Reject before connection | Passed |
| 81-row cross join, absent LIMIT, LIMIT -1 and LIMIT 1000000000 | Reject over 50 rows; no partial output | query_limit; LIMIT 50 returns 50 |
| 27 rows containing 1,800-byte UTF-8 strings | Reject payload over 24 KiB | query_limit |
| Huge cross-join COUNT with LIMIT 1 | Limit cannot bypass work budget | Interrupted with query_limit |
| Controlled clock crossing deadline | Stop with safe limit error | Passed (mocked time, not a latency benchmark) |
| Excessive value/expression/column size | Reject within native limits | Passed |
| Remove authorizer and attempt write with query_only; then disable query_only and attempt write | Read-only storage remains effective | Both attempts fail readonly |
| Missing file / exclusive database lock | No file creation; safe bounded failure | storage_unavailable |
| Snapshot after each fixture-based test | Every table's rows and complete schema unchanged; byte hash unchanged | Passed, including each malicious proposal |

Fixtures are created only in pytest temporary databases with supplied sample
CSV seeds plus labeled test hotels. The real local database is not used by the
new tests. The student database SHA-256 before implementation and after all
tests is unchanged:
`e7d83319033ee45c131fd8a9722ca492a1bc65638aa4b4b01d23ef4a29952c16`.

Repeat from the project root, using installed dependencies:

```sh
backend/.venv/bin/python -m pytest backend/tests/test_chat_queries.py -q
backend/.venv/bin/python -m pytest backend/tests -q
```

## Limits of this verification / next work

This is a SQL safety and retrieval boundary, not a semantic guarantee that a
model chose the right query. Constants/expressions and safe but incorrect joins
can still be proposed. The future controller must validate extracted stay intent,
date coverage, totals and answer grounding; the successful stay query here is
a labeled deterministic test, not LLM-generated SQL.

The work/deadline controls are cooperative SQLite limits, not a process-isolated
hard memory/time sandbox. They do not preempt every native operation or OS I/O
at an exact wall-clock instant. The database file/schema is trusted local app
storage; malicious replacement files or filesystem tampering are outside scope.
No frontend/browser, service restart, live OpenAI, live Geoapify, recording or
instructor-access checks were performed. Existing frontend was not changed;
lint/build were not repeated. No dependencies, secrets, real data, commit or push
changed. The next stage is backend intent/orchestration and provider integration,
with separate routes and mocked/live evidence as specified in the plan.
