import json
from pathlib import Path

from app.config import settings
from app.db import SessionLocal
from app.models import Profile, Project
from app.services.profile_service import _profile_to_dict


def update_profile_summary(headline: str, summary: str):
    db = SessionLocal()
    try:
        profile = db.query(Profile).first()
        if profile is None:
            profile = Profile(
                headline=headline,
                summary=summary,
                email='hello@example.com',
                location='Remote',
            )
            db.add(profile)
        else:
            profile.headline = headline
            profile.summary = summary
        db.commit()

        projects = db.query(Project).filter(Project.featured == 1).order_by(Project.id).all()
        data = _profile_to_dict(profile, projects)
        data["degraded_mode"] = True
        data["source"] = "fallback"

        path = Path(settings.FALLBACK_PROFILE_PATH)
        path.parent.mkdir(exist_ok=True)
        with path.open('w', encoding='utf-8') as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)

        return profile
    finally:
        db.close()
