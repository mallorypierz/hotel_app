"""Restricted local retrieval. Never initialize, migrate or reuse writable connections."""
from contextlib import closing
import json
import math
from pathlib import Path
import re
import sqlite3
import time

from .chat_models import QueryProposal, QueryRecords, SQL_MAX_BYTES, PARAMETER_LIMIT

ALLOWED_COLUMNS = {
    'saved_hotels': frozenset({'hotel_id', 'name', 'address'}),
    'saved_hotel_locations': frozenset({'hotel_id', 'postcode', 'country_code', 'locality'}),
    'demo_hotel_nights': frozenset({'hotel_id', 'stay_date', 'nightly_rate_cents', 'rooms_available'}),
}
ALLOWED_FUNCTIONS = frozenset({'count', 'sum', 'min', 'max', 'avg', 'coalesce',
                               'ifnull', 'nullif', 'lower', 'upper', 'length', 'like'})
MAX_ROWS = 50
MAX_RESULT_BYTES = 24 * 1024
MAX_VALUE_BYTES = 32 * 1024
MAX_COLUMNS = 24
MAX_VM_STEPS = 100_000
PROGRESS_INTERVAL = 100
DEADLINE_SECONDS = 0.5

ERROR_MESSAGES = {
    'invalid_proposal': 'The query proposal format is invalid.',
    'query_rejected': 'The proposed query is not permitted or is invalid.',
    'query_limit': 'The query exceeded a work or data limit. Narrow the question.',
    'storage_unavailable': 'Saved hotel retrieval is unavailable. Please retry.',
}


class RetrievalError(Exception):
    """Only fixed safe messages cross this boundary; no SQL, paths or engine errors."""
    def __init__(self, code):
        self.code = code
        super().__init__(ERROR_MESSAGES[code])


def _authorize(action, table, column, database_name, source):
    # Reject views/triggers/CTEs and everything not explicitly authorized.
    if source is not None:
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ:
        allowed = ALLOWED_COLUMNS.get(table)
        # SQLite emits column='' for count(*) / EXISTS without reading a value.
        # This SQLite build may also omit the database name for that event.
        # The fresh connection has no attachments/temp tables and cannot add any.
        if allowed is not None and column == '' and database_name in ('main', None):
            return sqlite3.SQLITE_OK
        if allowed is not None and column in allowed and database_name == 'main':
            return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_FUNCTION and column in ALLOWED_FUNCTIONS:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def _check_syntax_contract(proposal):
    """Small format restriction, NOT the authorization boundary (SQLite is that)."""
    # Only bare SELECT proposals in v1. Comments before SELECT and CTEs are excluded.
    if not re.match(r'\s*SELECT\b', proposal.sql, re.IGNORECASE):
        raise RetrievalError('query_rejected')
    # Skip quoted tokens and comments to count only anonymous positional markers.
    tokens = re.finditer(r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|`(?:``|[^`])*`|"
                         r'\[[^\]]*\]|--[^\n]*(?:\n|$)|/\*[\s\S]*?\*/|'
                         r'\?[0-9]*|[:@$][\w]*', proposal.sql)
    count = 0
    for match in tokens:
        token = match.group()
        if token.startswith('?'):
            if token != '?':
                raise RetrievalError('query_rejected')
            count += 1
        elif token[0] in ':@$':
            raise RetrievalError('query_rejected')
    if count != len(proposal.parameters):
        raise RetrievalError('query_rejected')


class _Budget:
    def __init__(self):
        self.deadline = time.monotonic() + DEADLINE_SECONDS
        self.steps = 0
        self.interrupted = False

    def progress(self):
        self.steps += PROGRESS_INTERVAL
        self.interrupted = self.steps >= MAX_VM_STEPS or time.monotonic() >= self.deadline
        return int(self.interrupted)

    def check(self):
        if self.interrupted or time.monotonic() >= self.deadline:
            raise RetrievalError('query_limit')


def _configure(db):
    db.setconfig(sqlite3.SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION, False)
    db.setconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE, True)
    db.setconfig(sqlite3.SQLITE_DBCONFIG_TRUSTED_SCHEMA, False)
    db.setconfig(sqlite3.SQLITE_DBCONFIG_ENABLE_VIEW, False)
    db.setconfig(sqlite3.SQLITE_DBCONFIG_DQS_DML, False)
    db.execute('PRAGMA query_only=ON')
    db.execute('PRAGMA temp_store=MEMORY')
    db.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, SQL_MAX_BYTES + len('EXPLAIN '))
    db.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, MAX_VALUE_BYTES)
    db.setlimit(sqlite3.SQLITE_LIMIT_COLUMN, MAX_COLUMNS)
    db.setlimit(sqlite3.SQLITE_LIMIT_VARIABLE_NUMBER, PARAMETER_LIMIT)
    db.setlimit(sqlite3.SQLITE_LIMIT_EXPR_DEPTH, 32)
    db.setlimit(sqlite3.SQLITE_LIMIT_COMPOUND_SELECT, 8)
    db.setlimit(sqlite3.SQLITE_LIMIT_VDBE_OP, 25_000)
    db.setlimit(sqlite3.SQLITE_LIMIT_ATTACHED, 0)
    db.setlimit(sqlite3.SQLITE_LIMIT_WORKER_THREADS, 0)


def _collect(cursor, budget):
    columns = [item[0] for item in cursor.description]
    if len(set(columns)) != len(columns) or any(len(c.encode('utf-8')) > 128 for c in columns):
        raise RetrievalError('query_rejected')
    records = []
    # Count the exact UTF-8 payload for columns + records, including JSON escaping.
    payload = {'columns': columns, 'records': records}
    for row in cursor:
        budget.check()
        if len(records) >= MAX_ROWS:
            raise RetrievalError('query_limit')
        if any(type(v) not in (str, int, float, type(None)) or
               (type(v) is float and not math.isfinite(v)) for v in row):
            raise RetrievalError('query_rejected')
        records.append(dict(zip(columns, row)))
        if _payload_size(payload) > MAX_RESULT_BYTES:
            raise RetrievalError('query_limit')
    budget.check()
    size = _payload_size(payload)
    if size > MAX_RESULT_BYTES:
        raise RetrievalError('query_limit')
    return QueryRecords(columns=columns, records=records, row_count=len(records), result_bytes=size)


def _payload_size(payload):
    return len(json.dumps(payload, ensure_ascii=False, allow_nan=False,
                          separators=(',', ':')).encode('utf-8'))


def execute_query(proposal: QueryProposal, path: Path) -> QueryRecords:
    """Internal API. Path comes only from trusted backend configuration/tests.

    Authorize an EXPLAIN compilation first: rejected/multiple statements never
    step the original SQL. Keep authorization installed during real execution.
    """
    from pydantic import ValidationError
    try:
        proposal = QueryProposal.model_validate(proposal)
    except (ValidationError, UnicodeError):
        raise RetrievalError('invalid_proposal') from None
    _check_syntax_contract(proposal)
    budget = _Budget()
    try:
        # as_uri escapes ?/# in filenames; no user URI options or automatic creation.
        with closing(sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro',
                                     uri=True, timeout=0.1, isolation_level=None,
                                     cached_statements=0)) as db:
            _configure(db)
            db.set_authorizer(_authorize)
            db.set_progress_handler(budget.progress, PROGRESS_INTERVAL)
            budget.check()
            with closing(db.execute('EXPLAIN ' + proposal.sql, proposal.parameters)):
                pass  # Compile only; never step the proposed query during validation.
            budget.check()
            with closing(db.execute(proposal.sql, proposal.parameters)) as cursor:
                return _collect(cursor, budget)
    except RetrievalError:
        raise
    except MemoryError:
        raise RetrievalError('query_limit') from None
    except sqlite3.Error as error:
        code = getattr(error, 'sqlite_errorcode', 0) & 255
        if budget.interrupted or code in (sqlite3.SQLITE_INTERRUPT, sqlite3.SQLITE_TOOBIG):
            safe_code = 'query_limit'
        elif code in (sqlite3.SQLITE_CANTOPEN, sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED,
                      sqlite3.SQLITE_IOERR, sqlite3.SQLITE_CORRUPT, sqlite3.SQLITE_NOTADB):
            safe_code = 'storage_unavailable'
        else:
            safe_code = 'query_rejected'
        raise RetrievalError(safe_code) from None
    except (OSError, UnicodeError, ValueError):
        raise RetrievalError('storage_unavailable') from None
