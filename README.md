# Career Platform

A recruiter-focused personal career website built with FastAPI and SQLite.

## Local setup

1. Create a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Start the app:
   `uvicorn app.main:app --reload`
4. Visit `http://localhost:8000`.

## Environment

Copy `.env.example` to `.env` and adjust values if needed.

## Fallback profile behavior

The site keeps a visible public profile even when the SQLite database is unavailable by serving a cached JSON snapshot from `data/fallback-profile.json`.
