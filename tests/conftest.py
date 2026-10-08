import os
import tempfile
from pathlib import Path

# Point the app at a throwaway database and fallback file before app.config is
# imported, so running the suite never rewrites the real career_platform.db.
_TMP_DIR = Path(tempfile.mkdtemp(prefix="career-platform-tests-"))
os.environ["SQLITE_DB_PATH"] = str(_TMP_DIR / "test.db")
os.environ["FALLBACK_PROFILE_PATH"] = str(_TMP_DIR / "fallback-profile.json")

import pytest  # noqa: E402

import app.models  # noqa: E402,F401
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.models import Profile  # noqa: E402
from app.seed import seed_data  # noqa: E402

TEST_PROFILE = {
    "full_name": "Test Person",
    "headline": "Business Analytics student",
    "summary": "Test summary.",
    "location": "Los Angeles, CA",
    "email": "test.person@example.com",
    "linkedin_url": "https://www.linkedin.com/in/test-person",
    "github_url": "https://github.com/test-person",
    "resume_url": "/static/resume/test-resume.pdf",
    "profile_image": "",
    "focus_area": "Business Analytics",
    "seeking": "Seeking full-time analyst roles.",
    "highlights": ["Test University · May 2027", "3.9 GPA"],
    "about": "First about paragraph.\n\nSecond about paragraph.",
}


@pytest.fixture(autouse=True)
def fresh_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.add(Profile(**TEST_PROFILE))
        db.commit()
        seed_data(db)
    finally:
        db.close()
    fallback = Path(os.environ["FALLBACK_PROFILE_PATH"])
    if fallback.exists():
        fallback.unlink()
    yield
