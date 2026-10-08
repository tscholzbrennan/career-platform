import json
from pathlib import Path
from typing import Any, Dict

from app.config import settings

# Last resort when both the database and the snapshot file are unavailable.
# Keep it to real, public identity so recruiters never see placeholder content.
_BUILT_IN_PROFILE: Dict[str, Any] = {
    "full_name": "Tristan Scholz-Brennan",
    "headline": "Information Systems & Business Analytics student at Loyola Marymount University",
    "summary": (
        "Business Administration student at Loyola Marymount University studying Information Systems "
        "and Business Analytics (May 2027). Seeking full-time Data Analyst and Business Analyst roles."
    ),
    "location": "Los Angeles, CA",
    "email": "Tscholzbrennan@gmail.com",
    "linkedin_url": "https://www.linkedin.com/in/tristan-scholz-brennan-a7a1922a0",
    "github_url": "https://github.com/tscholzbrennan",
    "resume_url": "/static/resume/Tristan-Scholz-Brennan-Resume.pdf",
    "profile_image": "",
    "focus_area": "Information Systems & Business Analytics",
    "seeking": "Seeking full-time Data Analyst and Business Analyst roles starting after graduation in May 2027.",
    "about": None,
    "highlights": [],
    "contact_links": {
        "email": "Tscholzbrennan@gmail.com",
        "linkedin": "https://www.linkedin.com/in/tristan-scholz-brennan-a7a1922a0",
        "github": "https://github.com/tscholzbrennan",
    },
    "featured_projects": [],
}


def load_fallback_profile() -> Dict[str, Any]:
    path = Path(settings.FALLBACK_PROFILE_PATH)
    payload = dict(_BUILT_IN_PROFILE)
    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            payload.update(json.load(handle))
    payload["degraded_mode"] = True
    payload["source"] = "fallback"
    return payload
