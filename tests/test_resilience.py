from fastapi.testclient import TestClient

from app.main import app


def test_fallback_profile_available():
    client = TestClient(app)
    response = client.get('/api/profile')
    assert response.status_code == 200
    payload = response.json()
    assert 'headline' in payload
    assert 'contact_links' in payload
