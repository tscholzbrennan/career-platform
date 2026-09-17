from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Profile, Project
from app.services.fallback_profile import load_fallback_profile


def _profile_to_dict(profile: Profile, projects: List[Project]) -> Dict[str, Any]:
    return {
        "headline": profile.headline,
        "summary": profile.summary,
        "location": profile.location,
        "email": profile.email,
        "linkedin_url": profile.linkedin_url,
        "github_url": profile.github_url,
        "resume_url": profile.resume_url,
        "profile_image": profile.profile_image,
        "focus_area": profile.focus_area,
        "contact_links": {
            "email": profile.email,
            "linkedin": profile.linkedin_url,
            "github": profile.github_url,
        },
        "featured_projects": [
            {"title": project.title, "slug": project.slug, "summary": project.summary}
            for project in projects[:3]
        ],
        "degraded_mode": False,
        "source": "database",
    }


def get_public_profile() -> Dict[str, Any]:
    db: Session | None = None
    try:
        db = SessionLocal()
        profile = db.query(Profile).first()
        if profile is None:
            return load_fallback_profile()

        projects = db.query(Project).filter(Project.featured == 1).order_by(Project.id).all()
        return _profile_to_dict(profile, projects)
    except Exception:
        return load_fallback_profile()
    finally:
        if db is not None:
            db.close()
