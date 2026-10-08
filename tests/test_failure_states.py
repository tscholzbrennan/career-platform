import json
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

import app.services.content_service as content_service
import app.services.profile_service as profile_service
from app.db import SessionLocal
from app.main import app
from app.models import Project
from app.services.fallback_profile import load_fallback_profile

PAGES = ["/", "/about", "/experience", "/projects", "/resume", "/contact"]


def _broken_session():
    raise OperationalError("SELECT 1", {}, Exception("database is locked"))


@pytest.fixture
def database_down(monkeypatch):
    monkeypatch.setattr(content_service, "SessionLocal", _broken_session)
    monkeypatch.setattr(profile_service, "SessionLocal", _broken_session)
    snapshot = {
        "full_name": "Snapshot Person",
        "headline": "Snapshot headline",
        "summary": "Snapshot summary.",
        "location": "Los Angeles, CA",
        "email": "snapshot@example.org",
        "resume_url": "/static/resume/snapshot.pdf",
        "contact_links": {"email": "snapshot@example.org", "linkedin": "https://www.linkedin.com/in/snap",
                          "github": "https://github.com/snap"},
        "featured_projects": [{"title": "Snapshot Project", "slug": "snapshot-project", "summary": "Snap."}],
    }
    with open(os.environ["FALLBACK_PROFILE_PATH"], "w", encoding="utf-8") as handle:
        json.dump(snapshot, handle)


def test_every_page_still_renders_when_the_database_is_down(database_down):
    client = TestClient(app)
    for path in PAGES:
        response = client.get(path)
        assert response.status_code == 200, path
        assert "Snapshot Person" in response.text, path


def test_visitors_never_see_the_internal_fallback_banner(database_down):
    html = TestClient(app).get("/").text
    assert "fallback snapshot" not in html.lower()


def test_home_shows_snapshot_projects_when_the_database_is_down(database_down):
    html = TestClient(app).get("/").text
    assert "Snapshot Project" in html


def test_resume_download_survives_a_database_outage(database_down):
    html = TestClient(app).get("/resume").text
    assert 'href="/static/resume/snapshot.pdf"' in html


def test_built_in_fallback_is_the_real_person_not_a_placeholder():
    data = load_fallback_profile()  # no snapshot file exists in the test environment
    text = json.dumps(data)
    assert data["full_name"] == "Tristan Scholz-Brennan"
    assert "example.com" not in text
    assert "Data & AI Engineer" not in text
    assert 'https://www.linkedin.com"' not in text


def test_unknown_project_is_a_real_404_page():
    response = TestClient(app).get("/projects/does-not-exist")
    assert response.status_code == 404
    assert "text/html" in response.headers["content-type"]
    assert 'href="/projects"' in response.text
    assert "<title>Page not found · Test Person</title>" in response.text


def test_unknown_route_is_an_html_404_page():
    response = TestClient(app).get("/no-such-page")
    assert response.status_code == 404
    assert "text/html" in response.headers["content-type"]
    assert 'href="/"' in response.text


def test_unknown_api_route_stays_json():
    response = TestClient(app).get("/api/nope")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_empty_project_list_has_a_helpful_empty_state():
    db = SessionLocal()
    try:
        db.query(Project).delete()
        db.commit()
    finally:
        db.close()
    client = TestClient(app)
    assert "Featured projects" not in client.get("/").text
    projects_html = client.get("/projects").text
    assert "github.com/test-person" in projects_html.split("<main>")[1]
