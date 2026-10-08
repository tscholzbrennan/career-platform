import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.copy_database import TargetNotEmpty, copy_database
from app.db import DATABASE_URL, Base, SessionLocal
from app.models import Experience, Profile, Project, Skill


def _project(id, slug):
    return Project(id=id, title=slug.title(), slug=slug, summary="s", description="d", role="r",
                   tech_stack=["SQL", "Python"], tags=[], metrics=["m1"], featured=1)


@pytest.fixture
def source_url(tmp_path):
    url = f"sqlite:///{tmp_path / 'source.db'}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(Profile(id=1, full_name="Source Person", headline="h", summary="s", email="source@example.org",
                       highlights=["LMU · May 2027", "Dean's List"]))
        db.add_all([_project(5, "five"), _project(9, "nine")])
        db.add(Experience(id=3, role_title="Analyst", company_name="Co", start_date="2024-01", summary="s",
                          bullet_points=["did a thing"], impact_notes=[], skills=["SQL"], category="work"))
        db.add(Skill(id=2, name="SQL", category="Data"))
        db.commit()
    engine.dispose()
    return url


def test_copy_refuses_non_empty_target(source_url):
    # The autouse fixture has already seeded the target.
    with pytest.raises(TargetNotEmpty):
        copy_database(source_url, DATABASE_URL)


def test_copy_replaces_target_with_source_rows(source_url):
    counts = copy_database(source_url, DATABASE_URL, replace=True)
    assert counts["profiles"] == 1 and counts["projects"] == 2 and counts["experiences"] == 1
    db = SessionLocal()
    try:
        profile = db.query(Profile).one()
        assert profile.full_name == "Source Person"
        assert profile.highlights == ["LMU · May 2027", "Dean's List"]
        assert [p.slug for p in db.query(Project).order_by(Project.id)] == ["five", "nine"]
        assert db.query(Experience).one().bullet_points == ["did a thing"]
    finally:
        db.close()


def test_new_rows_after_copy_get_the_next_id(source_url):
    copy_database(source_url, DATABASE_URL, replace=True)
    db = SessionLocal()
    try:
        project = Project(title="New", slug="new", summary="s", description="d", role="r")
        db.add(project)
        db.commit()
        assert project.id == 10
    finally:
        db.close()
