from pathlib import Path
import runpy

import pytest

from backend.app import config
from backend.app.main import app, get_health


@pytest.mark.parametrize('setting, configured', [
    ('', False),
    ('GEOAPIFY_API_KEY=\n', False),
    ('GEOAPIFY_API_KEY="   "\n', False),
    ('GEOAPIFY_API_KEY=sample-test-key\n', True),
])
def test_config_and_health(tmp_path, monkeypatch, setting, configured):
    helper = tmp_path / 'backend' / 'app' / 'config.py'
    helper.parent.mkdir(parents=True)
    helper.write_text(Path(config.__file__).read_text())
    (tmp_path / '.env').write_text(setting)
    monkeypatch.delenv('GEOAPIFY_API_KEY', raising=False)
    monkeypatch.chdir(helper.parent)
    loaded = runpy.run_path(str(helper))
    monkeypatch.setattr(config, 'GEOAPIFY_API_KEY', loaded['GEOAPIFY_API_KEY'])
    assert get_health() == {
        'status': 'ok',
        'geoapify': 'key is configured' if configured else 'key is not configured',
    }
    assert any(route.path == '/api/health' and 'GET' in route.methods for route in app.routes)
