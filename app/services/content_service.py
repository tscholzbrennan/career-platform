from app.db import SessionLocal
from app.models import Experience, Project


def get_experiences():
    db = SessionLocal()
    try:
        return db.query(Experience).order_by(Experience.id.desc()).all()
    finally:
        db.close()


def get_projects():
    db = SessionLocal()
    try:
        return db.query(Project).order_by(Project.id.desc()).all()
    finally:
        db.close()


def get_project_by_slug(slug: str):
    db = SessionLocal()
    try:
        return db.query(Project).filter(Project.slug == slug).first()
    finally:
        db.close()
