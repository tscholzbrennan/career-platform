# Move to Railway + PostgreSQL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## Where things stand (inspected 2026-10-08)

| | |
|---|---|
| Live site | `tristaninfo.me` and `www.tristaninfo.me`, both A records pointing to `20.221.247.215` (Azure VM). DNS is on **Cloudflare** (`viddy`/`stephane.ns.cloudflare.com`), and the records are DNS-only (the lookup returns the VM's IP, not a Cloudflare IP). |
| Running code | VM `~/career-platform` on `e9ed51d`, the same as `main`. Service `career-platform` (systemd → uvicorn → nginx, HTTPS by Let's Encrypt). |
| Database | SQLite, `career_platform.db` (tracked in git). Rows: profiles 1, experiences 3, projects 1, skills 12, education 1, media 0, fallback_profile_snapshots 0. |
| DB wiring | `app/db.py` builds the only engine from `sqlite:///{settings.SQLITE_DB_PATH}`. Every service imports `SessionLocal` from there. Startup runs `create_all` → `ensure_columns` (`ALTER TABLE ADD COLUMN`) → `seed_data` (placeholder rows, but only into empty tables). |
| SQLite-only code | `connect_args={"check_same_thread": False}` in `app/db.py`. Nothing else: models use generic `JSON`, `String`, `Integer`, `Date`, and there's no raw SQL besides `ensure_columns`, whose DDL also works on Postgres. |
| Tests | 35 pass on SQLite (`.venv/bin/python -m pytest -q`). `tests/conftest.py` points the app at a temp DB through env vars and **drops and recreates all tables before every test**. |
| Railway | The project exists with a Postgres service and a web service (per the user). The Railway CLI isn't installed on the laptop. The service names, the GitHub link, and the current deploy state are unknown until Task 0. |
| Local Postgres | None (no `psql`, `postgres`, or Docker). Homebrew is available. |

**Goal:** `tristaninfo.me` is served by the Railway web service, reading from Railway Postgres, with the VM's current data. The Azure VM is stopped but kept, so it can be the rollback.

**Architecture:** The app reads one `DATABASE_URL`. If it's unset, the app falls back to the existing SQLite file, so local dev and the default test run don't change. Railway's Postgres URL is normalized to the `postgresql+psycopg://` driver. A one-off copy command moves every table from the VM's SQLite file into Postgres and resets the ID sequences. Railway builds from the GitHub repo using a checked-in `railway.json` start command. Cloudflare DNS moves from the VM's IP to Railway's CNAME target last, so the VM keeps serving until Railway is proven.

```
before: visitor ─▶ Cloudflare DNS (A 20.221.247.215) ─▶ nginx ─▶ uvicorn ─▶ SQLite file
after:  visitor ─▶ Cloudflare DNS (CNAME, flattened) ─▶ Railway edge (TLS) ─▶ web service uvicorn ─▶ Railway Postgres (private network)
```

**Tech Stack:** FastAPI 0.115, SQLAlchemy 2.0.35, psycopg 3 (`psycopg[binary]`), uv (`uv.lock`), Railway (Railpack builder, `railway.json`), Homebrew `postgresql@16` for local tests, Cloudflare DNS.

**Spec:** The user's request in conversation on 2026-10-08: "Inspect my app and plan its move to Railway and PostgreSQL. The Railway project already exists with Postgres and a web service." There's no separate spec file.

## Global Constraints

- Nothing runs until the user says to. Steps marked **(user)** happen in a dashboard (Railway, Cloudflare, Azure portal) or need the user's login.
- The database comes from the env var `DATABASE_URL`. If it's unset, the app uses `sqlite:///{SQLITE_DB_PATH}` (today's behavior). On Railway (`RAILWAY_ENVIRONMENT_NAME` is set), a missing `DATABASE_URL` is a startup error, never a silent SQLite fallback.
- Driver: `psycopg[binary]` (psycopg 3), pinned to an exact version in both `requirements.txt` and `pyproject.toml`/`uv.lock`, like every other dependency.
- The test suite must never connect to Railway. `TEST_DATABASE_URL` must point at `localhost`/`127.0.0.1`, and `conftest.py` refuses anything else.
- The source of truth for the data copy is the **VM's** `career_platform.db`, not the repo copy.
- The VM keeps serving `tristaninfo.me` until Task 5. The VM isn't deleted in this plan, only deallocated in Task 6 after a soak period.
- Content freeze: no edits to the VM's database between Task 3 (copy) and Task 5 (DNS cutover).
- `docs/how-this-site-is-secured.md` has uncommitted user edits and describes the VM. This plan doesn't touch it. Rewriting it for Railway is a follow-up.
- Every task with a live effect ends with an **Undo** block.
- Tick steps and add dated results or deviations in this file while executing.

## Review Focus

1. **Placeholder content goes live on Railway.** If the web service boots against an empty Postgres, `seed_data` writes "Data & AI Engineer… hello@example.com" rows, and they show publicly. Expected: real data is in Postgres before any deploy that has `DATABASE_URL`, and the copy refuses to write into a non-empty target unless told `--replace`. Pinned by `test_copy_refuses_non_empty_target`, plus the ordering of Tasks 3 → 4.
2. **Postgres ID sequences are left at 1 after copying explicit IDs.** The next insert then fails with a duplicate key. Expected: inserting a new row after the copy gets `max(id)+1`. Pinned by `test_new_rows_after_copy_get_the_next_id` (run against local Postgres in Task 2).
3. **Railway's `postgres://` or `postgresql://` URL.** SQLAlchemy rejects `postgres://`, and plain `postgresql://` picks psycopg2, which isn't installed. Expected: both work. Pinned by `tests/test_database_url.py`.
4. **`DATABASE_URL` missing on Railway.** The app would quietly use an SQLite file inside the container, which is wiped on every deploy, and seed placeholders into it. Expected: the deploy fails loudly. Pinned by `test_missing_url_on_railway_is_an_error`.
5. **The test suite aimed at a real database.** `conftest.py` runs `drop_all` before every test. Expected: pointing `TEST_DATABASE_URL` at a non-local host stops the run before anything connects. Pinned by `test_conftest_rejects_remote_test_database`.

---

> **Executed 2026-10-08 (code tasks only, per the user; nothing on Railway was created or changed):** branch `feat/railway-postgres`, commits `ad66ac2` (Task 1), `2a25709` (Task 2), `ae51f29` (Task 3, Steps 1–3). psycopg resolved to **3.3.6**. 45 tests pass on SQLite and on local Postgres 16 (Homebrew, `brew services`). The ID-counter test was watched failing on Postgres first (`3 == 10`) before `setval` was added. The rehearsal copied the repo DB into local Postgres; all 6 pages and the 404 were byte-identical to the SQLite-served site. Step 3 was a push only: no PR and no merge to `main`, since merging may auto-deploy. Task 0 and Task 3 Steps 4–6 onward are not done.

### Task 0: Railway preflight (read-only)

**Files:** none (results get written into this plan's "Where things stand" table).

- [ ] **Step 1 (user): Install and log in to the Railway CLI.**

```bash
brew install railway
railway login
cd ~/Desktop/GITHUB/career-platform && railway link   # pick the existing project, then the web service
```

- [ ] **Step 2: Record the facts the later tasks need.**

```bash
railway status                       # project, environment, linked service
railway variables --service <web>    # does DATABASE_URL already exist? is RAILWAY_ENVIRONMENT_NAME set?
railway variables --service Postgres # confirm DATABASE_URL and DATABASE_PUBLIC_URL exist (don't paste values into the repo)
```

Record the exact Postgres service name (used in `${{<name>.DATABASE_URL}}`), the web service name, and whether `RAILWAY_ENVIRONMENT_NAME` is present.

- [ ] **Step 3 (user, dashboard): Check the web service source.** Settings → Source: is it connected to `tscholzbrennan/career-platform`, and which branch auto-deploys? Has it deployed anything yet?

**Important:** if it auto-deploys `main`, every push to `main` from here on deploys to Railway. That's harmless to the live site (DNS still points at the VM), but it's why Task 4 sets `DATABASE_URL` only after Task 3 has copied the data.

- [ ] **Step 4: Check whether Postgres is already non-empty** (for example, from an earlier deploy that seeded it). This only works after Task 1 adds psycopg. Run it at the start of Task 3, Step 1.

---

### Task 1: Read the database from `DATABASE_URL` (SQLite stays the default)

**Files:**
- Modify: `app/config.py`
- Modify: `app/db.py`
- Modify: `tests/conftest.py`
- Modify: `requirements.txt`, `pyproject.toml`, `uv.lock` (via `uv add`)
- Modify: `.env.example`
- Create: `tests/test_database_url.py`

**Interfaces:**
- Produces: `app.config.resolve_database_url(raw: str, sqlite_path: str, on_railway: bool) -> str`. `Settings.DATABASE_URL: str = ""`. `app.db.engine` is built from the resolved URL. `conftest._test_database_url() -> str`.

- [x] **Step 1: Write the failing tests** in `tests/test_database_url.py`:

```python
import pytest

from app.config import resolve_database_url


def test_unset_url_uses_the_sqlite_file():
    assert resolve_database_url("", "career_platform.db", on_railway=False) == "sqlite:///career_platform.db"


@pytest.mark.parametrize("raw", ["postgres://u:p@h:5432/db", "postgresql://u:p@h:5432/db"])
def test_railway_style_urls_use_psycopg3(raw):
    assert resolve_database_url(raw, "x.db", on_railway=False) == "postgresql+psycopg://u:p@h:5432/db"


def test_explicit_driver_is_left_alone():
    url = "postgresql+psycopg://u:p@h:5432/db"
    assert resolve_database_url(url, "x.db", on_railway=False) == url


def test_explicit_sqlite_url_is_left_alone():
    assert resolve_database_url("sqlite:////tmp/t.db", "x.db", on_railway=False) == "sqlite:////tmp/t.db"


def test_missing_url_on_railway_is_an_error():
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        resolve_database_url("", "career_platform.db", on_railway=True)


def test_conftest_rejects_remote_test_database():
    # Import by the name pytest already registered ("conftest"); importing it as
    # tests.conftest would re-run its env setup mid-session and repoint the suite.
    from conftest import _test_database_url

    with pytest.raises(RuntimeError, match="local"):
        _test_database_url({"TEST_DATABASE_URL": "postgresql://u:p@db.railway.app:5432/railway"}, "/tmp/x.db")
    assert _test_database_url({}, "/tmp/x.db") == "sqlite:////tmp/x.db"
    local = "postgresql://localhost/career_platform_test"
    assert _test_database_url({"TEST_DATABASE_URL": local}, "/tmp/x.db") == local
```

There's no `tests/__init__.py`, so pytest registers the conftest as the top-level module `conftest` (checked 2026-10-08). Don't add an `__init__.py`: that renames the module and breaks this import.

- [x] **Step 2: Run them and confirm they fail.**

Run: `.venv/bin/python -m pytest tests/test_database_url.py -v`
Expected: FAIL with `ImportError: cannot import name 'resolve_database_url'`.

- [x] **Step 3: Implement `app/config.py`.**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Career Platform"
    DATABASE_URL: str = ""
    SQLITE_DB_PATH: str = "career_platform.db"
    FALLBACK_PROFILE_PATH: str = "data/fallback-profile.json"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def resolve_database_url(raw: str, sqlite_path: str, on_railway: bool) -> str:
    # Railway hands out postgres:// or postgresql:// URLs; SQLAlchemy needs the
    # psycopg (v3) driver named explicitly. Unset means local SQLite, except on
    # Railway, where the container disk is wiped on every deploy.
    if not raw:
        if on_railway:
            raise RuntimeError("DATABASE_URL is not set; reference the Postgres service's DATABASE_URL")
        return f"sqlite:///{sqlite_path}"
    for prefix in ("postgres://", "postgresql://"):
        if raw.startswith(prefix):
            return "postgresql+psycopg://" + raw[len(prefix):]
    return raw


settings = Settings()
```

- [x] **Step 4: Implement `app/db.py`.**

```python
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import resolve_database_url, settings

DATABASE_URL = resolve_database_url(
    settings.DATABASE_URL,
    settings.SQLITE_DB_PATH,
    on_railway=bool(os.environ.get("RAILWAY_ENVIRONMENT_NAME")),
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()
```

- [x] **Step 5: Update `tests/conftest.py`** so the app always gets an explicit test URL. Replace the env-var block at the top (the lines before `import pytest`) with:

```python
import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse

# Point the app at a throwaway database and fallback file before app.config is
# imported, so running the suite never rewrites the real database. Every test
# drops all tables, so a non-local TEST_DATABASE_URL is refused outright.
_TMP_DIR = Path(tempfile.mkdtemp(prefix="career-platform-tests-"))


def _test_database_url(environ, sqlite_path) -> str:
    url = environ.get("TEST_DATABASE_URL")
    if not url:
        return f"sqlite:///{sqlite_path}"
    if urlparse(url).hostname not in ("localhost", "127.0.0.1"):
        raise RuntimeError("TEST_DATABASE_URL must point at a local database")
    return url


os.environ["DATABASE_URL"] = _test_database_url(os.environ, _TMP_DIR / "test.db")
os.environ["SQLITE_DB_PATH"] = str(_TMP_DIR / "test.db")
os.environ["FALLBACK_PROFILE_PATH"] = str(_TMP_DIR / "fallback-profile.json")
os.environ.pop("RAILWAY_ENVIRONMENT_NAME", None)
```

Leave the rest of `conftest.py` unchanged.

- [x] **Step 6: Add the driver.**

```bash
uv add "psycopg[binary]"
grep -A1 'name = "psycopg"' uv.lock | grep version    # the resolved version, e.g. 3.2.x
```

Then pin it exactly in `pyproject.toml` (replace the `>=` range that `uv add` wrote with `==<version>`), run `uv lock`, and add `psycopg[binary]==<version>` to `requirements.txt`. Check: `.venv/bin/python -c "import psycopg; print(psycopg.__version__)"` prints that version. If `.venv` isn't uv-managed, run `uv sync`.

- [x] **Step 7: Update `.env.example`.**

```
APP_NAME="Career Platform"
# Leave unset for local SQLite. On Railway this is ${{Postgres.DATABASE_URL}}.
DATABASE_URL=""
SQLITE_DB_PATH="career_platform.db"
FALLBACK_PROFILE_PATH="data/fallback-profile.json"
```

- [x] **Step 8: Run the whole suite.**

Run: `.venv/bin/python -m pytest -q`
Expected: 35 + 7 = 42 passed.

- [x] **Step 9: Commit** on a branch `feat/railway-postgres` (cut from `main`).

```bash
git checkout -b feat/railway-postgres
git add app/config.py app/db.py tests/conftest.py tests/test_database_url.py requirements.txt pyproject.toml uv.lock .env.example
git commit -m "feat: read the database from DATABASE_URL with SQLite as the local default"
```

---

### Task 2: Prove the app on a local Postgres, and add the copy command

**Files:**
- Create: `app/copy_database.py`
- Create: `tests/test_copy_database.py`

**Interfaces:**
- Consumes: `app.db.Base`, `app.db.SessionLocal`, `app.migrations.ensure_columns`, `app.models.*`.
- Produces: `app.copy_database.copy_database(source_url: str, target_url: str, replace: bool = False) -> dict[str, int]` (table name → rows copied). `app.copy_database.TargetNotEmpty(Exception)`. CLI: `python -m app.copy_database --source <url> --target <url> [--replace]`.

- [x] **Step 1 (user's laptop): Install a local Postgres for tests.**

```bash
brew install postgresql@16
brew services start postgresql@16
/opt/homebrew/opt/postgresql@16/bin/createdb career_platform_test
```

Check: `/opt/homebrew/opt/postgresql@16/bin/psql -d career_platform_test -c 'select 1'` prints `1`.

- [x] **Step 2: Run the existing suite on Postgres.**

Run: `TEST_DATABASE_URL=postgresql://localhost/career_platform_test .venv/bin/python -m pytest -q`
Expected: 42 passed. If something fails, fix it in app code (not by skipping the test) and record what you found here. The most likely candidate is ordering: Postgres doesn't guarantee row order without `ORDER BY`. `get_experiences` sorts in Python, and the other content queries order by `id`. `db.query(Profile).first()` has no `ORDER BY`, but there's only one profile.

- [x] **Step 3: Write the failing tests** in `tests/test_copy_database.py`. They use whatever database the suite is using (SQLite by default, local Postgres when `TEST_DATABASE_URL` is set) as the **target**, and a temp SQLite file as the **source**:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.copy_database import TargetNotEmpty, copy_database
from app.db import DATABASE_URL, Base, SessionLocal
from app.models import Experience, Profile, Project, Skill


def _project(id, slug):
    return Project(id=id, title=slug.title(), slug=slug, summary="s", description="d", role="r",
                   tech_stack=["SQL", "Python"], tags=[], metrics=["m1"], featured=1)


@pytest.fixture
def source_url(tmp_path):
    url = f"sqlite:///{tmp_path / 'source.db'}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(Profile(id=1, full_name="Source Person", headline="h", summary="s", email="source@example.org",
                       highlights=["LMU · May 2027", "Dean's List"]))
        db.add_all([_project(5, "five"), _project(9, "nine")])
        db.add(Experience(id=3, role_title="Analyst", company_name="Co", start_date="2024-01", summary="s",
                          bullet_points=["did a thing"], impact_notes=[], skills=["SQL"], category="work"))
        db.add(Skill(id=2, name="SQL", category="Data"))
        db.commit()
    engine.dispose()
    return url


def test_copy_refuses_non_empty_target(source_url):
    # The autouse fixture has already seeded the target.
    with pytest.raises(TargetNotEmpty):
        copy_database(source_url, DATABASE_URL)


def test_copy_replaces_target_with_source_rows(source_url):
    counts = copy_database(source_url, DATABASE_URL, replace=True)
    assert counts["profiles"] == 1 and counts["projects"] == 2 and counts["experiences"] == 1
    db = SessionLocal()
    try:
        profile = db.query(Profile).one()
        assert profile.full_name == "Source Person"
        assert profile.highlights == ["LMU · May 2027", "Dean's List"]
        assert [p.slug for p in db.query(Project).order_by(Project.id)] == ["five", "nine"]
        assert db.query(Experience).one().bullet_points == ["did a thing"]
    finally:
        db.close()


def test_new_rows_after_copy_get_the_next_id(source_url):
    copy_database(source_url, DATABASE_URL, replace=True)
    db = SessionLocal()
    try:
        project = Project(title="New", slug="new", summary="s", description="d", role="r")
        db.add(project)
        db.commit()
        assert project.id == 10
    finally:
        db.close()
```

- [x] **Step 4: Run them and confirm they fail.**

Run: `.venv/bin/python -m pytest tests/test_copy_database.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.copy_database'`.

- [x] **Step 5: Implement `app/copy_database.py`.**

```python
"""Copy every table from one database into another (SQLite → Railway Postgres).

    python -m app.copy_database --source sqlite:///career_platform.db --target "$DATABASE_PUBLIC_URL"
"""
import argparse

from sqlalchemy import create_engine, func, insert, select, text

import app.models  # noqa: F401  # register every table on Base.metadata
from app.config import resolve_database_url
from app.db import Base
from app.migrations import ensure_columns


class TargetNotEmpty(Exception):
    pass


def _count(conn, table) -> int:
    return conn.execute(select(func.count()).select_from(table)).scalar_one()


def copy_database(source_url: str, target_url: str, replace: bool = False) -> dict[str, int]:
    tables = Base.metadata.sorted_tables
    source = create_engine(resolve_database_url(source_url, "", on_railway=False))
    target = create_engine(resolve_database_url(target_url, "", on_railway=False))
    try:
        Base.metadata.create_all(target)
        ensure_columns(target)
        counts = {}
        with source.connect() as src, target.begin() as dst:
            filled = [table.name for table in tables if _count(dst, table)]
            if filled and not replace:
                raise TargetNotEmpty(f"target already has rows in {', '.join(filled)}; pass --replace to overwrite")
            for table in reversed(tables):
                dst.execute(table.delete())
            for table in tables:
                rows = [dict(row._mapping) for row in src.execute(select(table))]
                if rows:
                    dst.execute(insert(table), rows)
                counts[table.name] = len(rows)
            if dst.dialect.name == "postgresql":
                # Rows were inserted with explicit ids, so move each id sequence past them.
                for table in tables:
                    dst.execute(text(
                        f"SELECT setval(pg_get_serial_sequence('{table.name}', 'id'), "
                        f"COALESCE((SELECT MAX(id) FROM {table.name}), 0) + 1, false)"
                    ))
        with target.connect() as dst:
            for table in tables:
                if _count(dst, table) != counts[table.name]:
                    raise RuntimeError(f"row count mismatch in {table.name} after copy")
        return counts
    finally:
        source.dispose()
        target.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--replace", action="store_true", help="delete existing rows in the target first")
    args = parser.parse_args()
    for name, count in copy_database(args.source, args.target, args.replace).items():
        print(f"{name}: {count}")


if __name__ == "__main__":
    main()
```

- [x] **Step 6: Run the new tests on both databases.**

Run: `.venv/bin/python -m pytest tests/test_copy_database.py -v`, then `TEST_DATABASE_URL=postgresql://localhost/career_platform_test .venv/bin/python -m pytest tests/test_copy_database.py -v`
Expected: 3 passed each time. The Postgres run is the one that actually exercises `setval`.

- [x] **Step 7: Run the full suite on both.**

Run: `.venv/bin/python -m pytest -q && TEST_DATABASE_URL=postgresql://localhost/career_platform_test .venv/bin/python -m pytest -q`
Expected: 45 passed, twice.

- [x] **Step 8: Rehearse with the real data on local Postgres.**

```bash
/opt/homebrew/opt/postgresql@16/bin/createdb career_platform_rehearsal
.venv/bin/python -m app.copy_database --source sqlite:///career_platform.db --target postgresql://localhost/career_platform_rehearsal
DATABASE_URL=postgresql://localhost/career_platform_rehearsal .venv/bin/uvicorn app.main:app --port 8001
```

Check: it prints `profiles: 1, experiences: 3, projects: 1, skills: 12, education: 1, media: 0, fallback_profile_snapshots: 0`. Every page at `http://localhost:8001` looks the same as `http://localhost:8000` running on SQLite, and `curl -s localhost:8001/api/profile` shows `"source": "database"` and the real name.

- [x] **Step 9: Commit.**

```bash
git add app/copy_database.py tests/test_copy_database.py
git commit -m "feat: add a command that copies the SQLite data into Postgres"
```

---

### Task 3: Railway build config, and the real data copy

**Files:**
- Create: `railway.json`
- Modify: `README.md` (setup + deploy sections)

- [x] **Step 1: Write `railway.json`.**

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "sh -c 'uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips=*'",
    "healthcheckPath": "/",
    "healthcheckTimeout": 60,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

> **Deviation 2026-10-08:** wrapped in `sh -c` so `$PORT` expands even if Railway runs the start command without a shell. Checked locally: the exact command booted on `PORT=8103` against Postgres, and stopped with the `DATABASE_URL` error when the variable was empty and `RAILWAY_ENVIRONMENT_NAME` was set.

Railpack detects Python from `pyproject.toml`/`uv.lock` and Python 3.12 from `.python-version`. `--proxy-headers` makes `request.url` show `https` behind Railway's edge. Today that's only used for `request.url.path`, but it keeps any future absolute URLs correct.

- [x] **Step 2: Update `README.md`.** Replace "built with FastAPI and SQLite" with "built with FastAPI, using PostgreSQL in production (Railway) and SQLite locally". Under **Environment**, add: "`DATABASE_URL` selects the database. Leave it unset to use `career_platform.db`. Run the tests against Postgres with `TEST_DATABASE_URL=postgresql://localhost/career_platform_test pytest` (local databases only)." Add a **Deploy** section: "Pushes to `main` deploy to Railway (`railway.json`). The web service's `DATABASE_URL` references the Postgres service. One-off data copy: `python -m app.copy_database --source sqlite:///… --target \"$DATABASE_PUBLIC_URL\"`."

- [x] **Step 3: Commit, then open a PR** (don't merge yet, since merging may deploy).

```bash
git add railway.json README.md
git commit -m "chore: add Railway build and start config"
git push -u origin feat/railway-postgres
gh pr create --title "Move to Railway + PostgreSQL" --body "Implements docs/superpowers/plans/2026-10-08-railway-postgres-migration.md"
```

- [x] **Step 4: Pull the live database off the VM.** Content freeze starts here.

```bash
SCRATCH=/private/tmp/claude-501/-Users-tristanbrennan-Desktop-GITHUB-career-platform/scratchpad   # or any non-repo folder
mkdir -p "$SCRATCH"
ssh -i ~/.ssh/isba4775_azure azureuser@20.221.247.215 'cd ~/career-platform && sqlite3 career_platform.db ".backup /tmp/live.db"'
scp -i ~/.ssh/isba4775_azure azureuser@20.221.247.215:/tmp/live.db "$SCRATCH/live.db"
for t in profiles experiences projects skills education media fallback_profile_snapshots; do echo "$t $(sqlite3 "$SCRATCH/live.db" "select count(*) from $t")"; done
```

> **Pre-migration backup 2026-10-08:** `~/career_platform.db.bak-20261008T214815Z` on the VM (mode 600). `pragma integrity_check` = ok, row counts match the live DB (1/3/1/12/1/0/0), and the `.dump` checksum is identical to the live DB. This is a safety copy. Step 4 still takes a fresh copy at copy time.

`.backup` takes a consistent copy even while the app has the file open. Check that the counts match the table at the top of this plan. If they differ, the VM has newer content, which is fine: it's the source of truth.

- [x] **Step 5: Check the Railway Postgres is empty** (this is Task 0, Step 4).

```bash
PUB=$(railway variables --service <Postgres> --kv | sed -n 's/^DATABASE_PUBLIC_URL=//p')
.venv/bin/python -c "
import sys; from sqlalchemy import create_engine, inspect
from app.config import resolve_database_url
print(inspect(create_engine(resolve_database_url(sys.argv[1], '', False))).get_table_names())" "$PUB"
```

Expected: `[]`. If tables exist, an earlier deploy created them (and probably seeded placeholders). Note that here, and use `--replace` in Step 6 after confirming with the user.

- [x] **Step 6: Copy.**

```bash
.venv/bin/python -m app.copy_database --source "sqlite:///$SCRATCH/live.db" --target "$PUB"
```

Expected: the same counts as Step 4. The command checks the counts itself and raises on any mismatch.

> **Done 2026-10-08 (no Railway CLI; the user put `DATABASE_PUBLIC_URL` in `.env` as `RAILWAY_DATABASE_URL`):** Railway Postgres 18.6 had no tables beforehand. Copied from the verified VM backup `~/career_platform.db.bak-20261008T214815Z` (fingerprint `19f1b57de9488406`, the same as the live DB). Then compared it against a fresh read-only snapshot of the **live** VM DB (same fingerprint), table by table: the same 7 tables, the same columns, and identical row counts and values (education 1, experiences 3, fallback_profile_snapshots 0, media 0, profiles 1, projects 1, skills 12; 114 values checked). Every ID counter on Railway is at max id + 1. A deliberately altered local copy was flagged as DIFFERENT, so the check works. Content freeze is now in effect until DNS cutover.

**Undo:** `--replace` with a fresh copy fixes bad data. To empty Postgres entirely: `railway connect <Postgres>`, then `DROP SCHEMA public CASCADE; CREATE SCHEMA public;`.

---

### Task 4: Deploy the web service and verify on its Railway domain

- [ ] **Step 1 (user, Railway dashboard): Set the web service's variables.** Add `DATABASE_URL` = `${{<Postgres>.DATABASE_URL}}`. That's the private-network URL, so no egress fees, and it never leaves Railway. Don't set `SQLITE_DB_PATH`. Confirm `RAILWAY_ENVIRONMENT_NAME` shows under the service's Railway-provided variables.

- [ ] **Step 2 (user, Railway dashboard): Set the deploy source.** The web service should deploy from `tscholzbrennan/career-platform`. For a first deploy before merging, set the branch to `feat/railway-postgres`. Otherwise merge the PR and leave it on `main`. Settings → Networking → **Generate Domain** to get a `*.up.railway.app` URL.

- [ ] **Step 3: Watch the deploy.**

Run: `railway logs --service <web>`
Expected: `Uvicorn running on http://0.0.0.0:<port>`, `Application startup complete`, no traceback, and the healthcheck passes.

- [ ] **Step 4: Verify from the laptop.**

```bash
URL=https://<web>.up.railway.app
curl -s $URL/api/profile | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['source'], d['full_name'], d['email'])"
for p in / /about /experience /projects /resume /contact /static/resume/Tristan-Scholz-Brennan-Resume.pdf; do echo "$p $(curl -s -o /dev/null -w '%{http_code}' $URL$p)"; done
curl -s $URL/ | grep -c "example.com"
```

Expected: `database Tristan Scholz-Brennan Tscholzbrennan@gmail.com`, every path `200`, and `0` placeholder hits. Then open the Railway URL in a browser and compare each page against `https://tristaninfo.me`. They should look the same.

- [ ] **Step 5: Check that the seed didn't add rows.** Re-run the counts from Task 3, Step 5 (`get_table_names` swapped for a count loop, or `railway connect <Postgres>` + `select count(*) from projects;`). Expected: the same counts as the copy.

- [ ] **Step 6: If you deployed from the branch, merge the PR** and set the source branch back to `main`. Check that the deploy from `main` also passes Step 4.

**Undo:** in the dashboard, Deployments → redeploy the previous deployment, or remove the service's domain. The live site is still on the VM, so visitors are unaffected.

---

### Task 5: Move `tristaninfo.me` to Railway (Cloudflare DNS)

- [ ] **Step 1 (user, Cloudflare, a day ahead if possible): Lower TTL** on the `tristaninfo.me` and `www` A records to 1–5 minutes (they're DNS-only, so TTL applies).

- [ ] **Step 2 (user, Railway): Add custom domains** `tristaninfo.me` and `www.tristaninfo.me` on the web service (Settings → Networking → Custom Domain), target port = the app's port. Railway shows a CNAME target for each, and possibly a `_railway-verify` TXT record.

- [ ] **Step 3 (user, Cloudflare): Swap the records.** Write down the current A records (both point to `20.221.247.215`). Delete them, then add:
  - `CNAME @ → <railway target>`. Cloudflare flattens a CNAME at the apex automatically.
  - `CNAME www → <railway target for www>`
  - Any `TXT` verification record Railway asked for.

  Keep them **DNS only** (grey cloud) until Railway shows both domains as verified with a certificate issued. Cloudflare's proxy in front of Railway works, but it needs SSL mode "Full", and it's a separate decision.

- [ ] **Step 4: Verify.**

```bash
dig +short tristaninfo.me www.tristaninfo.me      # no longer 20.221.247.215
curl -sI https://tristaninfo.me | head -1         # HTTP/2 200
echo | openssl s_client -connect tristaninfo.me:443 -servername tristaninfo.me 2>/dev/null | openssl x509 -noout -issuer -subject
curl -s https://tristaninfo.me/api/profile | python3 -c "import json,sys; print(json.load(sys.stdin)['source'])"
```

Expected: Railway IPs, `200`, a certificate issued for `tristaninfo.me` (Let's Encrypt via Railway), and `database`. Also confirm there's no request in the VM's nginx log after the TTL expires: `ssh … 'sudo tail -n 5 /var/log/nginx/access.log'`.

**Undo:** in Cloudflare, delete the two CNAMEs and restore `A @ → 20.221.247.215` and `A www → 20.221.247.215`. The VM is untouched and still running, so the site is back within the TTL.

---

### Task 6: Soak, then stop the VM (keep it)

- [ ] **Step 1: Soak for 7 days** (until 2026-10-15 or later). Check `railway logs` for errors every few days, and load the site once.

- [ ] **Step 2 (user, after the soak): Deallocate the VM.**

```bash
az vm deallocate -g RG-CAREER-PLATFORM -n vm-career-platform
az vm get-instance-view -g RG-CAREER-PLATFORM -n vm-career-platform --query "instanceView.statuses[1].displayStatus" -o tsv
```

Expected: `VM deallocated`. The disk and the static IP `20.221.247.215` are kept, and the IP still has a small cost. Deleting the resource group is a separate decision for later.

- [ ] **Step 3: Update this plan and memory.** Record dates and results here. Update the project memory: the site is on Railway, the deploy routine is "merge to `main`", the VM is deallocated but kept as a rollback, and `how-this-site-is-secured.md` still needs a Railway rewrite.

**Undo:** `az vm start -g RG-CAREER-PLATFORM -n vm-career-platform`. systemd brings the app and nginx back. Then repeat the Task 5 Undo.
