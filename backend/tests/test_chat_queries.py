"""Boundary checks on disposable SQLite databases, never the student's records."""
import hashlib
import json
import sqlite3

import pytest

from backend.app import chat_controller, chat_queries as queries, database
from backend.app.chat_models import QueryProposal
from backend.app.chat_queries import RetrievalError


def snapshot(path):
    with sqlite3.connect(path) as db:
        schema = db.execute('SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name').fetchall()
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return schema, {t: db.execute('SELECT * FROM "' + t.replace('"', '""') + '" ORDER BY rowid').fetchall() for t in tables}


@pytest.fixture
def local_db(tmp_path, monkeypatch):
    path = tmp_path / 'hotel ? # audit.sqlite3'
    database.initialize(path)
    with database.connection(path) as db:
        for hotel_id, name in [('a', 'Example Birch'), ('b', None), ('c', 'Missing night')]:
            db.execute('INSERT INTO saved_hotels VALUES (?, ?, NULL, 41, -72)', (hotel_id, name))
            db.execute("INSERT INTO saved_hotel_locations VALUES (?, '06109', 'us', 'Wethersfield', 41, -72)", (hotel_id,))
        db.execute("INSERT INTO saved_hotel_locations VALUES ('a', '06108', 'us', NULL, 41, -72)")
        db.executemany('INSERT INTO demo_hotel_nights VALUES (?, ?, ?, ?)', [
            ('a', '2026-10-10', 12000, 3), ('a', '2026-10-11', 14000, 2),
            ('b', '2026-10-10', 10000, 0), ('b', '2026-10-11', 10000, 5),
            ('c', '2026-10-10', 9000, 9)])
    monkeypatch.setattr(database, 'DATABASE', path)
    original = snapshot(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    yield path
    # Applies after EVERY test, including every malicious query and work overflow.
    assert snapshot(path) == original
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest


def run(sql, parameters=None):
    return chat_controller.retrieve({'sql': sql, 'parameters': parameters or []})


def test_join_aggregation_and_stay_nights(local_db):
    sql = '''SELECT h.hotel_id, h.name, COUNT(*) AS nights,
        SUM(n.nightly_rate_cents) AS total_cents, MIN(n.rooms_available) AS min_rooms
        FROM saved_hotels h JOIN demo_hotel_nights n USING(hotel_id)
        WHERE n.stay_date >= ? AND n.stay_date < ?
        AND EXISTS (SELECT 1 FROM saved_hotel_locations l
                    WHERE l.hotel_id=h.hotel_id AND l.postcode=?)
        GROUP BY h.hotel_id, h.name
        HAVING COUNT(*)=? AND MIN(n.rooms_available)>=? AND SUM(n.nightly_rate_cents)<=?
        ORDER BY total_cents, h.hotel_id'''
    params = ['2026-10-10', '2026-10-12', '06109', 2, 1, 35000]
    result = run(sql, params)
    assert result.records == [dict(hotel_id='a', name='Example Birch', nights=2,
                                   total_cents=26000, min_rooms=2)]
    assert result.row_count == 1 and result.row_limit == 50
    assert result.result_bytes == len(json.dumps({'columns': result.columns, 'records': result.records},
                                                 ensure_ascii=False, separators=(',', ':')).encode())
    params[-1] = 25000
    assert run(sql, params).records == []


def test_allowed_columns_null_case_and_bound_injection(local_db):
    assert run('select NAME, address from SAVED_HOTELS where hotel_id=?;', ['b']).records == [dict(name=None, address=None)]
    assert run('SELECT count(*) AS count FROM saved_hotels').records == [{'count': 3}]
    assert run('SELECT locality, country_code, postcode FROM saved_hotel_locations WHERE postcode=?', ['06108']).records == [
        dict(locality=None, country_code='us', postcode='06108')]
    assert run('SELECT hotel_id FROM saved_hotels WHERE name=?', ["'; DELETE FROM saved_hotels; --"]).records == []
    assert run("SELECT coalesce(name, ?) AS name FROM saved_hotels WHERE hotel_id=?", ['Unknown', 'b']).records == [{'name': 'Unknown'}]
    assert run("SELECT '?' AS marker, ? AS value /* ? :ignored */ -- ?\n", [7]).records == [{'marker': '?', 'value': 7}]


@pytest.mark.parametrize('sql', [
    'DELETE FROM saved_hotels', "UPDATE demo_hotel_nights SET rooms_available=0",
    "INSERT INTO saved_hotels(hotel_id,latitude,longitude) VALUES('evil',0,0)",
    'DROP TABLE bookings', 'ALTER TABLE saved_hotels ADD COLUMN evil TEXT',
    'CREATE TABLE evil(x)', 'CREATE TEMP TABLE evil(x)', 'CREATE VIEW evil AS SELECT * FROM users',
    "ATTACH DATABASE ':memory:' AS evil", 'DETACH DATABASE main', 'VACUUM',
    "VACUUM INTO 'evil.sqlite3'", 'REINDEX', 'ANALYZE', 'BEGIN', 'COMMIT',
    'PRAGMA query_only=OFF', 'PRAGMA writable_schema=ON', 'PRAGMA table_info(users)',
    'SELECT * FROM pragma_table_info(\'users\')',
    'SELECT * FROM hotels', 'SELECT count(*) FROM trips',
    'SELECT 1 FROM users', 'SELECT booking_id FROM bookings', 'SELECT version FROM metadata',
    'SELECT name FROM sqlite_master', 'SELECT sql FROM main.sqlite_schema',
    'SELECT latitude FROM saved_hotels', 'SELECT longitude FROM saved_hotel_locations',
    'SELECT * FROM saved_hotels', 'SELECT rowid FROM saved_hotels',
    'SELECT hotel_id FROM saved_hotels WHERE latitude > 0',
    'SELECT hotel_id FROM saved_hotels ORDER BY longitude',
    'SELECT hotel_id FROM saved_hotels UNION SELECT user_id FROM users',
    'SELECT name, (SELECT display_name FROM users LIMIT 1) FROM saved_hotels',
    "SELECT load_extension('/tmp/evil')", "SELECT readfile('/etc/passwd')",
    "SELECT writefile('/tmp/evil','x')", 'SELECT sqlite_version()',
    'SELECT randomblob(1000000000)', 'SELECT zeroblob(1000000000)',
    "SELECT printf('%1000000000s', 'x')", 'SELECT group_concat(name) FROM saved_hotels',
    'SELECT name FROM saved_hotels; DELETE FROM saved_hotels',
    'SELECT name FROM saved_hotels; SELECT name FROM saved_hotels',
    'SELECT name FROM saved_hotels; -- comment\n PRAGMA query_only=OFF',
    'EXPLAIN SELECT name FROM saved_hotels',
    'WITH c AS (SELECT name FROM saved_hotels) SELECT * FROM c',
    'WITH RECURSIVE c(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM c) SELECT * FROM c',
    'SELECT * FROM (WITH RECURSIVE c(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM c) SELECT * FROM c)',
    'SELECT name FROM saved_hotels WHERE hotel_id=:id',
    'SELECT name FROM saved_hotels WHERE hotel_id=?1',
    'SELECT name FROM saved_hotels WHERE hotel_id=?',
    'SELECT name AS same, hotel_id AS same FROM saved_hotels',
    "SELECT x'FF' AS value", 'SELECT 1e999 AS value',
    'SELECT this is invalid',
])
def test_rejects_unsafe_sql_without_mutation(local_db, sql):
    with pytest.raises(RetrievalError) as error:
        run(sql)
    assert error.value.code == 'query_rejected'
    assert str(error.value) == queries.ERROR_MESSAGES['query_rejected']
    assert str(local_db) not in str(error.value)


@pytest.mark.parametrize('payload', [
    {}, {'sql': 'SELECT 1'}, {'sql': 'SELECT 1', 'parameters': [], 'path': '/elsewhere'},
    {'sql': 'SELECT 1', 'parameters': [], 'row_limit': 10000},
    {'sql': 123, 'parameters': []}, {'sql': '', 'parameters': []},
    {'sql': '   ', 'parameters': []}, {'sql': 'SELECT\x00 1', 'parameters': []},
    {'sql': 'SELECT ' + 'a'*8192, 'parameters': []},
    {'sql': 'SELECT ' + 'é'*4096, 'parameters': []},
    {'sql': 'SELECT ?', 'parameters': [True]}, {'sql': 'SELECT ?', 'parameters': [b'x']},
    {'sql': 'SELECT ?', 'parameters': [{'key': 1}]}, {'sql': 'SELECT ?', 'parameters': ['x'*2049]},
    {'sql': 'SELECT ?', 'parameters': ['é'*1025]}, {'sql': 'SELECT ?', 'parameters': [2**63]},
    {'sql': 'SELECT ?', 'parameters': [float('inf')]}, {'sql': 'SELECT ?', 'parameters': [float('nan')]},
    {'sql': 'SELECT ?', 'parameters': None}, {'sql': 'SELECT ?', 'parameters': ('x',)},
    {'sql': 'SELECT ?', 'parameters': [1]*33},
])
def test_strict_proposals_fail_before_open(local_db, monkeypatch, payload):
    def forbidden_connect(*args, **kwargs):
        pytest.fail('Invalid proposal reached database connection')
    with monkeypatch.context() as m:
        m.setattr(queries.sqlite3, 'connect', forbidden_connect)
        with pytest.raises(RetrievalError) as error:
            chat_controller.retrieve(payload)
    assert error.value.code == 'invalid_proposal'


def test_revalidates_constructed_model(local_db):
    bad = QueryProposal.model_construct(sql='SELECT ?', parameters=[True])
    with pytest.raises(RetrievalError, match='format is invalid'):
        chat_controller.retrieve(bad)


def test_row_limit_independent_of_sql_limit(local_db):
    base = 'SELECT a.hotel_id FROM saved_hotels a, saved_hotels b, saved_hotels c, saved_hotels d'
    for suffix in ['', ' LIMIT -1', ' LIMIT 1000000000']:
        with pytest.raises(RetrievalError) as error:
            run(base + suffix)
        assert error.value.code == 'query_limit'
    assert run(base + ' LIMIT 50').row_count == 50


def test_payload_limit_accounts_for_utf8_and_no_partial_return(local_db):
    # Allowed concat operator; every scalar fits SQLite's limit, combined rows do not.
    sql = 'SELECT ? AS text FROM saved_hotels a, saved_hotels b, saved_hotels c'
    with pytest.raises(RetrievalError) as error:
        run(sql, ['界'*600])
    assert error.value.code == 'query_limit'


def test_vm_work_bound_even_when_result_has_limit_one(local_db):
    sql = 'SELECT count(*) AS total FROM ' + ', '.join(f'saved_hotels h{i}' for i in range(14)) + ' LIMIT 1'
    with pytest.raises(RetrievalError) as error:
        run(sql)
    assert error.value.code == 'query_limit'


def test_deadline_interrupts_query(local_db, monkeypatch):
    sql = 'SELECT count(*) FROM ' + ', '.join(f'saved_hotels h{i}' for i in range(8))
    clock = iter([0, 0, 0] + [10]*100)
    monkeypatch.setattr(queries.time, 'monotonic', lambda: next(clock, 10))
    with pytest.raises(RetrievalError) as error:
        run(sql)
    assert error.value.code == 'query_limit'


def test_expensive_value_and_expression_limits(local_db):
    for sql in ["SELECT " + ' || '.join(['?']*20),
                'SELECT ' + ', '.join(f'{i} AS c{i}' for i in range(25)),
                'SELECT ' + '+'.join(['1']*50)]:
        with pytest.raises(RetrievalError):
            run(sql, ['x'*2000]*20 if '?' in sql else [])


def test_preflight_rejection_never_steps_original(local_db, monkeypatch):
    original_connect = sqlite3.connect
    traces = []
    def traced_connect(*args, **kwargs):
        db = original_connect(*args, **kwargs)
        db.set_trace_callback(traces.append)
        return db
    with monkeypatch.context() as m:
        m.setattr(queries.sqlite3, 'connect', traced_connect)
        for sql in ['SELECT name FROM saved_hotels; SELECT 2',
                    'SELECT name FROM saved_hotels WHERE EXISTS(SELECT 1 FROM users)',
                    "SELECT load_extension('evil')"]:
            with pytest.raises(RetrievalError):
                run(sql)
    assert not any(t.lstrip().upper().startswith('SELECT') for t in traces)


def test_native_layers_block_writes_without_prefix_filter(local_db):
    with sqlite3.connect(local_db.as_uri()+'?mode=ro', uri=True) as db:
        queries._configure(db)
        assert db.execute('PRAGMA query_only').fetchone()[0] == 1
        assert not db.getconfig(sqlite3.SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION)
        db.set_authorizer(queries._authorize)
        for sql in ["UPDATE demo_hotel_nights SET rooms_available=0", 'PRAGMA query_only=OFF',
                    "ATTACH ':memory:' AS other", 'SELECT count(*) FROM bookings',
                    'SELECT latitude FROM saved_hotels', 'SELECT randomblob(1)']:
            with pytest.raises(sqlite3.DatabaseError):
                db.execute(sql)
        db.set_authorizer(None)
        with pytest.raises(sqlite3.OperationalError, match='readonly'):
            db.execute('DELETE FROM demo_hotel_nights')  # query_only + mode=ro
        db.execute('PRAGMA query_only=OFF')
        with pytest.raises(sqlite3.OperationalError, match='readonly'):
            db.execute('DELETE FROM demo_hotel_nights')  # mode=ro alone


def test_missing_database_not_created(tmp_path, monkeypatch):
    path = tmp_path/'absent.sqlite3'
    monkeypatch.setattr(database, 'DATABASE', path)
    with pytest.raises(RetrievalError) as error:
        run('SELECT name FROM saved_hotels')
    assert error.value.code == 'storage_unavailable'
    assert not path.exists()


def test_lock_is_bounded_and_safe(local_db):
    db = sqlite3.connect(local_db)
    try:
        db.execute('BEGIN EXCLUSIVE')
        with pytest.raises(RetrievalError) as error:
            run('SELECT name FROM saved_hotels')
        assert error.value.code == 'storage_unavailable'
    finally:
        db.rollback()
        db.close()
