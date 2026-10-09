"""Bounded, non-streaming OpenAI Responses transport; no database access or retries."""
from dataclasses import dataclass
import json
import math
import socket
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler, HTTPSHandler
from pydantic import ValidationError
from . import config

MODEL = 'gpt-4.1-mini-2025-04-14'
ENDPOINT = 'https://api.openai.com/v1/responses'
MAX_BODY = 256 * 1024
MAX_INPUT = 48 * 1024
MESSAGES = {
    'unconfigured': 'The chatbot is not configured. Set the backend OpenAI key.',
    'configuration': 'The chatbot model or limits are not configured correctly.',
    'access_denied': 'OpenAI access is unavailable. Check backend project access.',
    'quota_exceeded': 'OpenAI billing or usage quota needs attention.',
    'provider_limited': 'OpenAI is temporarily limited. Try again later.',
    'provider_timeout': 'The model request timed out. Please retry.',
    'provider_failed': 'The model request could not be completed. Please retry.',
    'invalid_model_response': 'The model returned an incomplete or invalid response.',
    'provider_refusal': 'The model could not answer this question. Please rephrase it.',
}


class ModelError(Exception):
    def __init__(self, code, retry_after=None):
        self.code, self.retry_after = code, retry_after
        super().__init__(MESSAGES[code])


@dataclass
class ModelReply:
    value: object
    usage: dict
    response_id: str | None
    model: str = MODEL


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward credentials to a redirected host.


def _open(request, timeout):
    opener = build_opener(_NoRedirect(), HTTPSHandler(context=ssl.create_default_context()))
    return opener.open(request, timeout=timeout)


def check_configuration():
    if not config.OPENAI_API_KEY:
        raise ModelError('unconfigured')
    try:
        timeout = float(config.OPENAI_TIMEOUT_SECONDS)
        tokens = int(config.OPENAI_MAX_OUTPUT_TOKENS)
        if config.OPENAI_MODEL != MODEL or not math.isfinite(timeout) or not 1 <= timeout <= 20 or not 256 <= tokens <= 1800:
            raise ValueError
    except (TypeError, ValueError):
        raise ModelError('configuration') from None
    return timeout, tokens


def _json(raw):
    def reject_constant(value):
        raise ValueError('Nonfinite JSON')
    def unique_pairs(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError('Duplicate JSON key')
            value[key] = item
        return value
    return json.loads(raw, parse_constant=reject_constant, object_pairs_hook=unique_pairs)


def _read(response, deadline):
    parts, size = [], 0
    while True:
        if time.monotonic() >= deadline:
            raise ModelError('provider_timeout')
        chunk = response.read1(min(4096, MAX_BODY + 1 - size))
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_BODY:
            raise ModelError('invalid_model_response')
        parts.append(chunk)
    if time.monotonic() >= deadline:
        raise ModelError('provider_timeout')
    return b''.join(parts)


def _http_error(error):
    retry = error.headers.get('Retry-After', '') if error.headers else ''
    retry = int(retry) if retry.isascii() and retry.isdigit() and len(retry) <= 6 else None
    try:
        payload = _json(error.read(8192))
        details = payload.get('error', {})
        code = details.get('code', '') if isinstance(details, dict) else ''
    except (ValueError, OSError, AttributeError, RecursionError):
        code = ''
    finally:
        error.close()
    if error.code in (401, 403, 404):
        return ModelError('access_denied')
    if code in ('insufficient_quota', 'credit_balance_exhausted', 'organization_spend_limit_exceeded',
                'project_spend_limit_exceeded', 'organization_usage_limit_exceeded'):
        return ModelError('quota_exceeded')
    if error.code in (429, 503):
        return ModelError('provider_limited', retry)
    return ModelError('provider_failed')


def request_structured(instructions, payload, contract, name, deadline):
    timeout, tokens = check_configuration()
    if time.monotonic() >= deadline:
        raise ModelError('provider_timeout')
    body = {'model': MODEL, 'instructions': instructions,
            'input': [{'role': 'user', 'content': json.dumps(payload, ensure_ascii=False, allow_nan=False)}],
            'store': False, 'stream': False, 'max_output_tokens': tokens,
            'text': {'format': {'type': 'json_schema', 'name': name, 'strict': True,
                                'schema': contract.model_json_schema()}}}
    encoded = json.dumps(body, ensure_ascii=False, allow_nan=False).encode('utf-8')
    if len(encoded) > MAX_INPUT:
        raise ModelError('invalid_model_response')
    request = Request(ENDPOINT, data=encoded, method='POST',
                      headers={'Authorization': 'Bearer ' + config.OPENAI_API_KEY,
                               'Content-Type': 'application/json'})
    try:
        call_deadline = min(deadline, time.monotonic() + timeout)
        with _open(request, min(timeout, max(0.01, deadline-time.monotonic()))) as response:
            raw = _read(response, call_deadline)
        result = _json(raw)
        if result.get('model') != MODEL or result.get('status') != 'completed':
            raise ModelError('invalid_model_response')
        texts = []
        for item in result.get('output', []):
            if item.get('type') != 'message':
                raise ModelError('invalid_model_response')
            if item.get('role') != 'assistant':
                raise ModelError('invalid_model_response')
            for part in item.get('content', []):
                if part.get('type') == 'refusal':
                    raise ModelError('provider_refusal')
                if part.get('type') != 'output_text':
                    raise ModelError('invalid_model_response')
                texts.append(part['text'])
        if len(texts) != 1:
            raise ModelError('invalid_model_response')
        value = contract.model_validate(_json(texts[0]))
        usage = result.get('usage') or {}
        safe_usage = {k: v for k, v in usage.items() if k in ('input_tokens', 'output_tokens', 'total_tokens')
                      and type(v) is int and 0 <= v <= 10_000_000}
        response_id = result.get('id')
        if not isinstance(response_id, str) or len(response_id) > 128 or not response_id.isascii():
            response_id = None
        return ModelReply(value, safe_usage, response_id)
    except HTTPError as error:
        raise _http_error(error) from None
    except (TimeoutError, socket.timeout):
        raise ModelError('provider_timeout') from None
    except URLError as error:
        code = 'provider_timeout' if isinstance(error.reason, (TimeoutError, socket.timeout)) else 'provider_failed'
        raise ModelError(code) from None
    except (ValueError, TypeError, KeyError, AttributeError, ValidationError, UnicodeError, RecursionError):
        raise ModelError('invalid_model_response') from None
    except OSError:
        raise ModelError('provider_failed') from None
