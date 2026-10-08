import re

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text

from app.db import SessionLocal
from app.main import app
from app.migrations import ensure_columns
from app.models import Profile

PAGES = ["/", "/about", "/experience", "/projects", "/resume", "/contact"]


def _set_profile(**fields):
    db = SessionLocal()
    try:
        profile = db.query(Profile).first()
        for key, value in fields.items():
            setattr(profile, key, value)
        db.commit()
    finally:
        db.close()


def test_every_page_title_and_brand_carry_the_name():
    client = TestClient(app)
    for path in PAGES:
        html = client.get(path).text
        title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
        assert "Test Person" in title, path
        assert re.search(r'class="brand"[^>]*>\s*Test Person\s*<', html), path


def test_home_heading_is_the_name_and_email_is_a_mailto_link():
    html = TestClient(app).get("/").text
    assert re.search(r"<h1>\s*Test Person\s*</h1>", html)
    assert 'href="mailto:test.person@example.com"' in html


def test_footer_names_the_person():
    html = TestClient(app).get("/about").text
    assert "© 2026 Test Person" in html


def test_resume_button_downloads_the_pdf():
    html = TestClient(app).get("/resume").text
    assert re.search(r'href="/static/resume/test-resume.pdf"[^>]*\bdownload\b', html)


def test_resume_button_hidden_when_resume_url_points_back_at_the_page():
    _set_profile(resume_url="/resume")
    html = TestClient(app).get("/resume").text
    assert "Download resume" not in html


def test_linkedin_links_use_the_profile_url():
    client = TestClient(app)
    for path in ["/", "/contact"]:
        html = client.get(path).text
        assert 'href="https://www.linkedin.com/in/test-person"' in html, path
        assert 'href="https://www.linkedin.com"' not in html, path


def test_migration_adds_new_columns_to_existing_tables(tmp_path):
    legacy = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}")
    with legacy.begin() as conn:
        conn.execute(text("CREATE TABLE profiles (id INTEGER PRIMARY KEY, headline VARCHAR(255))"))
        conn.execute(text("CREATE TABLE experiences (id INTEGER PRIMARY KEY, role_title VARCHAR(255))"))
        conn.execute(text("INSERT INTO experiences (role_title) VALUES ('Old role')"))
    ensure_columns(legacy)
    ensure_columns(legacy)  # safe to run twice
    profile_columns = {c["name"] for c in inspect(legacy).get_columns("profiles")}
    assert {"full_name", "seeking", "about", "highlights"} <= profile_columns
    with legacy.connect() as conn:
        assert conn.execute(text("SELECT category FROM experiences")).scalar() == "work"
