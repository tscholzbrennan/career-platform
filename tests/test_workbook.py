from datetime import date

from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.formatting import duration_months
from app.main import app
from app.models import Experience


def test_duration_counts_both_end_months():
    assert duration_months("May 2018", "Aug 2024") == 76
    assert duration_months("May 2025", "Aug 2025") == 4


def test_duration_runs_to_today_when_current():
    assert duration_months("Aug 2023", None, today=date(2026, 10, 8)) == 39


def test_duration_is_blank_for_unparseable_dates():
    assert duration_months("sometime", "later") is None


def test_experience_page_shows_months_and_total_for_work():
    db = SessionLocal()
    try:
        db.query(Experience).delete()
        db.add_all([
            Experience(role_title="Job A", company_name="A Co", start_date="May 2025", end_date="Aug 2025",
                       summary="a", bullet_points=["a"], category="work"),
            Experience(role_title="Job B", company_name="B Co", start_date="May 2018", end_date="Aug 2024",
                       summary="b", bullet_points=["b"], category="work"),
        ])
        db.commit()
    finally:
        db.close()
    html = TestClient(app).get("/experience").text
    assert ">76<" in html and ">4<" in html
    assert "80 months" in html
