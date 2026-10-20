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

Projects are the exception. If project rows can't be read, `/`, `/projects` and `/projects/<slug>` return `503` and show "Projects temporarily unavailable" next to the profile, instead of showing stale or sample projects. They come back on the next request once the database recovers, without a restart.

## Decisions

### SQLite as the first database

The spec asked for a relational database, ideally Postgres. The first version used SQLite instead:

- The app had one writer (the owner) and low read traffic, so SQLite's single-writer limit didn't matter.
- The whole database is one file. It ran on the laptop and the Azure VM with no database server to install, secure or patch, and it moved to the VM with a single `scp`.
- The `sqlite3` CLI could check the copy independently, and hashing the file proved that the laptop and VM copies matched.
- The models go through SQLAlchemy, so changing engines later meant changing `DATABASE_URL`, not rewriting queries.

Trade-off: the data lived on the VM's disk with no managed backups, and only one process could write safely. When the site moved to Railway, where the container filesystem doesn't persist between deploys, it switched to managed PostgreSQL (see `docs/superpowers/plans/2026-10-08-railway-postgres-migration.md`). SQLite is still the local default.
