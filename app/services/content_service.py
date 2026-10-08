import logging
from datetime import datetime

from app.db import SessionLocal
from app.models import Education, Experience, Project, Skill

logger = logging.getLogger(__name__)

_DATE_FORMATS = ("%b %Y", "%B %Y", "%Y-%m", "%Y")


def _parse_month(value):
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime((value or "").strip(), fmt)
        except ValueError:
            continue
    return datetime.min


def _query(load, default):
    # Pages must keep rendering when the database is unavailable, so a failed
    # read degrades to an empty result instead of a 500.
    db = None
    try:
        db = SessionLocal()
        return load(db)
    except Exception:
        logger.exception("Content query failed; serving an empty result")
        return default
    finally:
        if db is not None:
            db.close()


def get_experiences():
    return _query(
        lambda db: sorted(db.query(Experience).all(), key=lambda item: _parse_month(item.start_date), reverse=True),
        [],
    )


def get_education():
    return _query(lambda db: db.query(Education).order_by(Education.id).all(), [])


def get_skills_by_category():
    def load(db):
        grouped = {}
        for skill in db.query(Skill).order_by(Skill.id).all():
            grouped.setdefault(skill.category, []).append(skill.name)
        return grouped

    return _query(load, {})


def get_projects():
    return _query(lambda db: db.query(Project).order_by(Project.id.desc()).all(), [])


def get_project_by_slug(slug: str):
    return _query(lambda db: db.query(Project).filter(Project.slug == slug).first(), None)
