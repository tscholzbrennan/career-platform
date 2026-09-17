import json
from pathlib import Path
from typing import Any, Dict

from app.config import settings


def load_fallback_profile() -> Dict[str, Any]:
    path = Path(settings.FALLBACK_PROFILE_PATH)
    if not path.exists():
        return {
            "headline": "Data & AI Engineer",
            "summary": "Career-focused data and AI professional building impactful products and insights.",
            "location": "Remote",
            "email": "hello@example.com",
            "linkedin_url": "https://www.linkedin.com",
            "github_url": "https://github.com",
            "resume_url": "/resume",
            "contact_links": {
                "email": "hello@example.com",
                "linkedin": "https://www.linkedin.com",
                "github": "https://github.com",
            },
            "featured_projects": [
                {"title": "Demand Forecasting Dashboard"},
                {"title": "AI Research Briefing Tool"},
            ],
            "degraded_mode": True,
            "source": "fallback",
        }

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
        payload["degraded_mode"] = True
        payload["source"] = "fallback"
        return payload
