import re

from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.main import app
from app.models import Education, Experience, Skill
from app.services.content_service import get_experiences


def _main(html):
    return html.split("<main>", 1)[1].split("</main>", 1)[0]


def _add(*rows):
    db = SessionLocal()
    try:
        db.query(Experience).delete()
        db.add_all(rows)
        db.commit()
    finally:
        db.close()


def _experience(title, start, end=None, category="work"):
    return Experience(
        role_title=title, company_name=f"{title} Co", start_date=start, end_date=end,
        summary=f"{title} summary", bullet_points=[f"{title} bullet"], category=category,
    )


def test_experiences_are_newest_first_regardless_of_insert_order():
    _add(_experience("Middle", "May 2018", "Aug 2024"), _experience("Newest", "May 2025", "Aug 2025"),
         _experience("Oldest", "2016-01", "2017-06"))
    assert [e.role_title for e in get_experiences()] == ["Newest", "Middle", "Oldest"]


def test_experience_page_separates_work_from_activities():
    _add(_experience("Job", "May 2025", "Aug 2025"), _experience("Club", "Aug 2023", category="activity"))
    html = TestClient(app).get("/experience").text
    work, activities = html.split("Leadership &amp; activities")
    assert "Job" in work and "Club" not in work
    assert "Club" in activities
    assert "Aug 2023 – Present" in activities


def test_home_states_the_target_role_and_highlights():
    html = TestClient(app).get("/").text
    assert "Seeking full-time analyst roles." in html
    assert "Test University · May 2027" in html and "3.9 GPA" in html


def test_about_page_tells_the_profile_story_not_boilerplate():
    html = _main(TestClient(app).get("/about").text)
    assert "<p>First about paragraph.</p>" in html
    assert "<p>Second about paragraph.</p>" in html
    assert "Helping teams turn data into decisions" not in html
    assert "Test summary." not in html


def test_resume_page_lists_education_and_skills_instead_of_repeating_the_summary():
    db = SessionLocal()
    try:
        db.add(Education(institution="Test University", degree="BBA", dates="May 2027",
                         field_of_study="Analytics", details="GPA 3.9"))
        db.add_all([Skill(name="SQL", category="Programming"), Skill(name="Excel", category="Computer Skills")])
        db.commit()
    finally:
        db.close()
    html = _main(TestClient(app).get("/resume").text)
    assert "Test University" in html and "GPA 3.9" in html
    assert re.search(r"Programming.*SQL", html, re.S)
    assert "Test summary." not in html
