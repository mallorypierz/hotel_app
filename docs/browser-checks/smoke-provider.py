"""Generate browser failure fixtures through the real ASGI route, offline."""
import io
import json
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from backend.app import config, discovery, geocoding
from backend.tests.test_discovery import center, request

cases = {}
for name in ('mismatched_postcode', 'non_us', 'unresolved', 'empty', 'provider_failure', 'rate_limit', 'quota'):
    calls = {'geocoding': 0, 'places': 0}
    def geo_open(url, timeout):
        calls['geocoding'] += 1
        result = center()
        if name == 'mismatched_postcode':
            result['postcode'] = '02109'
        if name == 'non_us':
            result['country_code'] = 'ca'
        response = io.BytesIO(json.dumps({'results': [] if name == 'unresolved' else [result]}).encode())
        response.status = 200
        return response
    def places_open(url, timeout):
        calls['places'] += 1
        if name in ('provider_failure', 'rate_limit', 'quota'):
            status = {'provider_failure': 500, 'rate_limit': 429, 'quota': 403}[name]
            message = 'quota exceeded' if name == 'quota' else 'controlled failure'
            raise HTTPError('https://controlled.invalid/', status, 'controlled',
                            {'Retry-After': '2'}, io.BytesIO(json.dumps({'message': message}).encode()))
        response = io.BytesIO(b'{"features": []}')
        response.status = 200
        return response
    with patch.object(config, 'GEOAPIFY_API_KEY', 'controlled-only'), patch.object(geocoding, 'urlopen', geo_open), patch.object(discovery, 'urlopen', places_open):
        status, body, headers = request()
    expected = 404 if name in ('mismatched_postcode', 'non_us', 'unresolved') else 200 if name == 'empty' else 502 if name == 'provider_failure' else 503
    assert status == expected
    assert calls['places'] == (0 if expected == 404 else 1)
    cases[name] = {'status': status, 'body': body, 'headers': {k.decode(): v.decode() for k,v in headers.items() if k.lower() == b'retry-after'}, 'calls': calls}
Path('docs/browser-checks/smoke-provider-results.json').write_text(json.dumps(cases, indent=2)+'\n')
print('PASS: 7 simulated provider scenarios; mismatched/non-US/unresolved made no Places calls.')
