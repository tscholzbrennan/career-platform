# Career Platform

A recruiter-focused personal career website built with FastAPI, using PostgreSQL in production (Railway) and SQLite locally.

## Local setup

1. Create a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Start the app:
   `uvicorn app.main:app --reload`
4. Visit `http://localhost:8000`.

## Environment

Copy `.env.example` to `.env` and adjust values if needed.

`DATABASE_URL` selects the database. Leave it unset to use `career_platform.db`.

Run the tests against Postgres with `TEST_DATABASE_URL=postgresql://localhost/career_platform_test pytest`. The tests drop every table, so only local databases are accepted.

## Deploy

Production runs on Railway, built and started with the settings in `railway.json`. The web service's `DATABASE_URL` references the Postgres service.

One-off data copy from SQLite into Postgres:
`python -m app.copy_database --source sqlite:///career_platform.db --target "$DATABASE_PUBLIC_URL"`
It refuses to write into a database that already has rows unless you pass `--replace`.

## Fallback profile behavior

The site keeps a visible public profile even when the database is unavailable by serving a cached JSON snapshot from `data/fallback-profile.json`.
