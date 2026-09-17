import json
from pathlib import Path

from app.db import SessionLocal
from app.models import Profile


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

        data = {
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
            "featured_projects": [],
            "degraded_mode": True,
            "source": "fallback",
        }

        path = Path('data/fallback-profile.json')
        path.parent.mkdir(exist_ok=True)
        with path.open('w', encoding='utf-8') as handle:
            json.dump(data, handle, indent=2)

        return profile
    finally:
        db.close()
