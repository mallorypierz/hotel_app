"""Verification only: creates a NEW isolated fixture DB; captures mocked HTTP workflows.
Run from project root: backend/.venv/bin/python docs/browser-checks/chatbot-verification.py
Never initializes or writes the student's database. No real provider requests.
"""
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pytest
from backend.app import database, config, llm_provider
from backend.tests.test_chat import query_decision, QUESTION
from backend.tests.test_local_hotels import LocalClient
from backend.tests.test_chat_queries import snapshot

out = Path('docs/chatbot-verification-evidence')
out.mkdir(exist_ok=True)
Path('.capture/chatbot-verification').mkdir(parents=True, exist_ok=True)
work = Path(tempfile.mkdtemp(prefix='chatbot-verification-', dir='.capture')).resolve()
path = work/'isolated.sqlite3'
assert not path.exists()
database.initialize(path)
fixture = json.loads(Path('data/chatbot-fixture.json').read_text())
with database.connection(path) as db:
    for h in fixture['hotels']:
        db.execute('INSERT INTO saved_hotels VALUES(?,?,NULL,41,-72)', (h['hotel_id'], h['name']))
        for zipcode in h['postcodes']:
            db.execute("INSERT INTO saved_hotel_locations VALUES(?,?,'us','Example locality',41,-72)", (h['hotel_id'], zipcode))
        db.executemany('INSERT INTO demo_hotel_nights VALUES(?,?,?,?)', [(h['hotel_id'], *n) for n in h['nights']])
Path('.capture/chatbot-verification/runtime.json').write_text(json.dumps({'database': str(path)}))
before = snapshot(path)
hash_before = hashlib.sha256(path.read_bytes()).hexdigest()
for name, question, expected in [
    ('success', QUESTION, 'answer'),
    ('no-match', '06108, 2026-10-10 to 2026-10-12, one room, $250 total', 'no_matches'),
    ('insufficient', '06109, 2026-10-11 to 2026-10-14, one room, $350 total', 'insufficient_data'),
]:
    calls = []
    def mock_open(request, timeout):
        payload = json.loads(request.data)
        calls.append(payload)  # body only, never authorization headers
        if len(calls) == 1:
            result = query_decision(question).model_dump()
        else:
            inputs = json.loads(payload['input'][0]['content'])
            eligible = [h for h in inputs['checked_hotels'] if h['eligible']]
            result = {'status': inputs['status'], 'recommendations': [{'hotel_id': eligible[0]['hotel_id'], 'reason': 'lowest_total'}] if eligible else []}
        return io.BytesIO(json.dumps({'model': llm_provider.MODEL, 'status': 'completed', 'id': 'MOCK-verification',
          'output': [{'type': 'message', 'role': 'assistant', 'content': [{'type': 'output_text', 'text': json.dumps(result)}]}],
          'usage': {'input_tokens': 100, 'output_tokens': 50}}).encode())
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(database, 'DATABASE', path)
        patch.setattr(config, 'OPENAI_API_KEY', 'MOCK-only')
        patch.setattr(llm_provider, '_open', mock_open)
        response = LocalClient().post('/api/chat', json={'question': question})
    data = response.json()
    assert response.status_code == 200 and data['status'] == expected
    assert len(calls) == 2
    assert json.loads(calls[1]['input'][0]['content'])['retrieved_records'] == data['evidence']['retrieved_records']
    if name == 'success':
        facts = {h['hotel_id']: h for h in data['hotels']}
        assert facts['demo-birch']['total_cents'] == 26000
        assert facts['demo-river']['total_cents'] == 30000
        assert '$260.00' in data['answer']
        assert all(r['stay_date'] != '2026-10-12' for r in data['evidence']['retrieved_records'])
    assert snapshot(path) == before and hashlib.sha256(path.read_bytes()).hexdigest() == hash_before
    (out/f'mock-{name}.json').write_text(json.dumps({'label': 'CONTROLLED MOCK HTTP — not live OpenAI; real isolated SQLite retrieval', 'question': question, 'expected_status': expected, 'http_status': response.status_code, 'model_requests': calls, 'response': data, 'database_unchanged': True}, indent=2)+'\n')
    print(name, response.status_code, data['status'], 'two mocked HTTP requests; SQLite unchanged')
print('New isolated database recorded in .capture/chatbot-verification/runtime.json')
