"""MOCKED OpenAI transport tests. No external requests or real credentials."""
import io
import json
import socket
import time
from urllib.error import HTTPError, URLError

import pytest
from backend.app import config, llm_provider as provider
from backend.app.chat_contracts import AnswerDecision


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setattr(config,'OPENAI_API_KEY','mock-secret-not-a-real-key')
    monkeypatch.setattr(config,'OPENAI_MODEL',provider.MODEL)
    monkeypatch.setattr(config,'OPENAI_TIMEOUT_SECONDS','20')
    monkeypatch.setattr(config,'OPENAI_MAX_OUTPUT_TOKENS','1800')
    def no_network(*args,**kwargs):
        pytest.fail('Test attempted an unmocked network call')
    monkeypatch.setattr(provider,'_open',no_network)


def call():
    return provider.request_structured('Trusted instructions',{'question':'Mock question'},
                                       AnswerDecision,'hotel_answer',time.monotonic()+45)


def envelope(value=None):
    return {'model':provider.MODEL,'status':'completed','id':'mock-response',
            'output':[{'type':'message','role':'assistant','content':[
                {'type':'output_text','text':json.dumps(value or {'status':'no_matches','recommendations':[]})}]}]}


@pytest.mark.parametrize('field,value,code',[
    ('OPENAI_API_KEY','','unconfigured'), ('OPENAI_MODEL','other-model','configuration'),
    ('OPENAI_TIMEOUT_SECONDS','nan','configuration'), ('OPENAI_TIMEOUT_SECONDS','0','configuration'),
    ('OPENAI_TIMEOUT_SECONDS','21','configuration'), ('OPENAI_MAX_OUTPUT_TOKENS','bad','configuration'),
    ('OPENAI_MAX_OUTPUT_TOKENS','100000','configuration'),
])
def test_invalid_config_before_network(monkeypatch,field,value,code):
    monkeypatch.setattr(config,field,value)
    with pytest.raises(provider.ModelError) as error: call()
    assert error.value.code==code


@pytest.mark.parametrize('status,code,expected',[
    (401,'invalid_api_key','access_denied'),(403,'denied','access_denied'),(404,'model_not_found','access_denied'),
    (429,'rate_limit_exceeded','provider_limited'),(429,'slow_down','provider_limited'),
    (429,'insufficient_quota','quota_exceeded'),(429,'credit_balance_exhausted','quota_exceeded'),
    (429,'project_spend_limit_exceeded','quota_exceeded'),(503,'server_is_overloaded','provider_limited'),
    (500,'server_error','provider_failed'),(400,'bad_schema','provider_failed'),
])
def test_http_errors_are_sanitized_and_not_retried(monkeypatch,status,code,expected):
    calls=[]
    def fail(request,timeout):
        calls.append(request)
        raise HTTPError(provider.ENDPOINT,status,'secret raw reason',{'Retry-After':'12'},
                        io.BytesIO(json.dumps({'error':{'code':code,'message':'mock-secret-not-a-real-key'}}).encode()))
    monkeypatch.setattr(provider,'_open',fail)
    with pytest.raises(provider.ModelError) as error: call()
    assert error.value.code==expected and len(calls)==1
    assert 'mock-secret' not in str(error.value) and 'raw reason' not in str(error.value)
    assert error.value.retry_after==(12 if expected=='provider_limited' else None)


@pytest.mark.parametrize('problem,expected',[
    (socket.timeout('raw'),'provider_timeout'),(URLError(socket.timeout('raw')),'provider_timeout'),
    (URLError('raw network'),'provider_failed'),(OSError('raw OS error'),'provider_failed')])
def test_network_failures(monkeypatch,problem,expected):
    def fail(*args,**kwargs): raise problem
    monkeypatch.setattr(provider,'_open',fail)
    with pytest.raises(provider.ModelError) as error: call()
    assert error.value.code==expected and 'raw' not in str(error.value)


@pytest.mark.parametrize('mutate',[
    lambda d:d.update(status='incomplete'), lambda d:d.update(model='other-model'),
    lambda d:d.update(output=[]), lambda d:d.update(output=[{'type':'function_call'}]),
    lambda d:d['output'][0]['content'][0].update(text='not json'),
    lambda d:d['output'][0]['content'][0].update(text='{"status":"no_matches","status":"answer","recommendations":[]}'),
    lambda d:d['output'][0]['content'][0].update(text='{"status":"no_matches","recommendations":[],"extra":"not allowed"}'),
    lambda d:d.update(usage=['bad']),
])
def test_malformed_output(monkeypatch,mutate):
    data=envelope();mutate(data)
    monkeypatch.setattr(provider,'_open',lambda *args:io.BytesIO(json.dumps(data).encode()))
    with pytest.raises(provider.ModelError) as error: call()
    assert error.value.code=='invalid_model_response'


def test_refusal(monkeypatch):
    data=envelope();data['output'][0]['content']=[{'type':'refusal','refusal':'raw refusal'}]
    monkeypatch.setattr(provider,'_open',lambda *args:io.BytesIO(json.dumps(data).encode()))
    with pytest.raises(provider.ModelError) as error: call()
    assert error.value.code=='provider_refusal'


def test_response_body_limit(monkeypatch):
    monkeypatch.setattr(provider,'_open',lambda *args:io.BytesIO(b'x'*(provider.MAX_BODY+1)))
    with pytest.raises(provider.ModelError) as error: call()
    assert error.value.code=='invalid_model_response'


def test_request_deadline_before_network():
    with pytest.raises(provider.ModelError) as error:
        provider.request_structured('x',{},AnswerDecision,'answer',time.monotonic()-1)
    assert error.value.code=='provider_timeout'


def test_deadline_during_read(monkeypatch):
    clock=iter([0,10])
    monkeypatch.setattr(provider.time,'monotonic',lambda:next(clock,10))
    with pytest.raises(provider.ModelError) as error:
        provider._read(io.BytesIO(b'{}'),5)
    assert error.value.code=='provider_timeout'


def test_redirect_never_forwards_key():
    assert provider._NoRedirect().redirect_request(None,None,302,'',{},'https://example.com') is None


def test_deeply_nested_json_is_safe_error(monkeypatch):
    monkeypatch.setattr(provider,'_open',lambda *args:io.BytesIO(b'['*2000+b']'*2000))
    with pytest.raises(provider.ModelError) as error: call()
    assert error.value.code=='invalid_model_response'
