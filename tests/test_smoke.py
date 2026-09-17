from fastapi.testclient import TestClient

from app.main import app


def test_core_pages_render():
    client = TestClient(app)
    for path in ['/', '/about', '/projects', '/resume', '/contact']:
        response = client.get(path)
        assert response.status_code == 200
