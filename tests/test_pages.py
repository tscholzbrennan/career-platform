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
