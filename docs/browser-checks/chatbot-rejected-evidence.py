"""Controlled rejection evidence. Only a new temporary DB; never student records."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.app import database
from backend.app.chat_queries import execute_query, RetrievalError
from backend.tests.test_chat_queries import snapshot
from backend.app.chat_models import QueryProposal

fixture = json.loads(Path('data/chatbot-fixture.json').read_text())
Path('.capture').mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='chatbot-rejection-', dir='.capture') as work:
    path = Path(work)/'isolated.sqlite3'
    database.initialize(path)
    with database.connection(path) as db:
        for h in fixture['hotels']:
            db.execute('INSERT INTO saved_hotels VALUES(?,?,NULL,41,-72)', (h['hotel_id'], h['name']))
            for zipcode in h['postcodes']:
                db.execute("INSERT INTO saved_hotel_locations VALUES(?,?,'us','Example locality',41,-72)", (h['hotel_id'], zipcode))
            db.executemany('INSERT INTO demo_hotel_nights VALUES(?,?,?,?)', [(h['hotel_id'], *n) for n in h['nights']])
    baseline = snapshot(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    cases = []
    for sql in ['DELETE FROM saved_hotels', 'SELECT booking_id FROM bookings', 'SELECT name FROM saved_hotels; DELETE FROM saved_hotels']:
        try:
            execute_query(QueryProposal(sql=sql, parameters=[]), path)
            raise AssertionError('Rejected query unexpectedly succeeded')
        except RetrievalError as error:
            assert error.code == 'query_rejected'
            after = hashlib.sha256(path.read_bytes()).hexdigest()
            assert snapshot(path) == baseline and after == digest
            cases.append({'proposal': {'sql': sql, 'parameters': []}, 'expected': 'query_rejected', 'observed': error.code, 'all_table_contents_and_schemas_unchanged': True, 'before_sha256': digest, 'after_sha256': after})
    output={'label':'CONTROLLED fixed-fixture rejection check — no live model call; new temporary database only', 'date':'2026-10-08', 'fixture':'data/chatbot-fixture.json', 'cases':cases}
    Path('docs/chatbot-verification-evidence/rejected-queries.json').write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps(output, indent=2))
