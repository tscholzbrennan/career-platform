from fastapi.testclient import TestClient

from app.main import app


def test_about_and_projects_routes_work():
    client = TestClient(app)
    for path in ['/about', '/experience', '/projects']:
        response = client.get(path)
        assert response.status_code == 200
