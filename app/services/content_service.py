import logging
from datetime import datetime

from app.db import SessionLocal
from app.formatting import parse_month
from app.models import Education, Experience, Project, Skill

logger = logging.getLogger(__name__)


class ContentUnavailable(Exception):
    """A content read failed, so the caller can't tell "none" from "unknown"."""


def _load(load):
    db = None
    try:
        db = SessionLocal()
        return load(db)
    except Exception as exc:
        logger.exception("Content query failed")
        raise ContentUnavailable from exc
    finally:
        if db is not None:
            db.close()


def _query(load, default):
    # Pages must keep rendering when the database is unavailable, so a failed
    # read degrades to an empty result instead of a 500.
    try:
        return _load(load)
    except ContentUnavailable:
        return default


def get_experiences():
    return _query(
        lambda db: sorted(db.query(Experience).all(), key=lambda item: parse_month(item.start_date) or datetime.min, reverse=True),
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


# Project reads raise ContentUnavailable instead of degrading: an empty list
# would tell visitors there are no projects when the truth is "unknown".
def get_projects():
    return _load(lambda db: db.query(Project).order_by(Project.id.desc()).all())


def get_project_by_slug(slug: str):
    return _load(lambda db: db.query(Project).filter(Project.slug == slug).first())
