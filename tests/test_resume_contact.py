from fastapi.testclient import TestClient

from app.main import app


def test_resume_and_contact_pages_work():
    client = TestClient(app)
    for path in ['/resume', '/contact']:
        response = client.get(path)
        assert response.status_code == 200
