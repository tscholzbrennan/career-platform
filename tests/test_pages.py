from fastapi.testclient import TestClient

from app.main import app


def test_homepage_renders_headline():
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == 200
    assert 'headline' in response.text.lower() or 'profile' in response.text.lower()


def test_project_pages_load():
    client = TestClient(app)
    response = client.get('/projects')
    assert response.status_code == 200
