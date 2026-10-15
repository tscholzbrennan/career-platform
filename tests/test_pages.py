from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_homepage_renders_headline():
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == 200
    assert 'Business Analytics student' in response.text


def test_project_pages_load():
    client = TestClient(app)
    response = client.get('/projects')
    assert response.status_code == 200


def test_privacy_page_describes_analytics_and_choices():
    client = TestClient(app)
    response = client.get('/privacy')
    assert response.status_code == 200
    assert '_ga_T6KK7PB43N' in response.text
    assert 'Global Privacy Control' in response.text
    assert 'tools.google.com/dlpage/gaoptout' in response.text


def test_footer_links_to_privacy_page():
    client = TestClient(app)
    response = client.get('/')
    assert '<a href="/privacy">Privacy</a>' in response.text


def test_google_tag_is_gated_behind_consent_on_every_page():
    client = TestClient(app)
    for path in ['/', '/about', '/experience', '/projects', '/resume', '/contact', '/privacy']:
        html = client.get(path).text
        assert html.count('<script src="/static/js/consent.js" defer></script>') == 1, path
        assert html.count('data-consent role="region"') == 1, path
        assert 'googletagmanager.com' not in html, path


def test_consent_script_loads_the_tag_only_once_after_allow():
    script = Path('static/js/consent.js').read_text()
    assert 'G-T6KK7PB43N' in script
    assert 'querySelector(\'script[src*="googletagmanager.com/gtag/js"]\')' in script
    assert 'if (choice === "granted")' in script
