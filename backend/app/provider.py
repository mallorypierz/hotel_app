"""Bounded JSON transport with sanitized provider failures and no retries/logging."""
import json
import re
from http.client import HTTPException
from urllib.error import HTTPError, URLError


class ProviderRequestError(Exception):
    """Provider failure safe to report without request details."""


class MissingConfigurationError(ProviderRequestError):
    """The backend key is absent."""


class ProviderLimitedError(ProviderRequestError):
    def __init__(self, retry_after=None):
        super().__init__('Provider is temporarily limited.')
        self.retry_after = retry_after


def limited_error(status, headers, payload=None):
    # A generic 403 is not evidence of quota exhaustion. Only explicit signals
    # qualify; unknown error bodies remain generic failures.
    message = payload.get('message', '') if isinstance(payload, dict) else ''
    explicit = isinstance(message, str) and any(phrase in message.lower() for phrase in (
        'quota exceeded', 'quota exhausted', 'rate limit exceeded',
        'too many requests', 'daily limit exceeded',
    ))
    if status == 429 or (status != 200 and explicit):
        delay = headers.get('Retry-After') if headers else None
        delay = delay if isinstance(delay, str) and re.fullmatch(r'[0-9]{1,6}', delay) else None
        raise ProviderLimitedError(delay) from None


def request_json(url, opener):
    try:
        with opener(url, timeout=10) as response:
            status = response.status
            headers = getattr(response, 'headers', {})
            limited_error(status, headers)
            payload = json.load(response)
            limited_error(status, headers, payload)
            if status != 200:
                raise ProviderRequestError('Geocoding provider request failed.')
            return payload
    except HTTPError as error:
        # Consume only a bounded error body, never echo it or the request URL.
        try:
            payload = json.loads(error.read(8192))
        except (OSError, HTTPException, ValueError):
            payload = None
        finally:
            error.close()
        limited_error(error.code, error.headers, payload)
        raise ProviderRequestError('Geocoding provider request failed.') from None
    except (URLError, OSError, HTTPException, ValueError):
        raise ProviderRequestError('Geocoding provider request failed.') from None
