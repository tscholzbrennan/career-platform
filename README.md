# Career Platform

A recruiter-focused personal career website built with FastAPI, using PostgreSQL in production (Railway) and SQLite locally.

## Design and plans

- Spec: [`docs/superpowers/specs/2026-09-15-career-platform-resume-site-design.md`](docs/superpowers/specs/2026-09-15-career-platform-resume-site-design.md)
- Plan: [Move to the Azure VM](docs/superpowers/plans/2026-09-24-azure-vm-migration.md) (2026-09-24)
- Plan: [Operate the VM](docs/superpowers/plans/2026-10-01-operate-the-vm.md) (systemd, nginx, HTTPS; 2026-10-01)
- Plan: [Move to Railway + PostgreSQL](docs/superpowers/plans/2026-10-08-railway-postgres-migration.md) (2026-10-08). There's no separate spec file for this move. The spec was the request in conversation, quoted at the top of the plan.
- Project 1 submission index: [`docs/project-1-submission.md`](docs/project-1-submission.md)

## Local setup

1. Create a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Start the app:
   `uvicorn app.main:app --reload`
4. Visit `http://localhost:8000`.

`career_platform.db` isn't in the repo. On first start the app creates it and fills it with placeholder seed data. To work with real content, copy it down from Railway: `python -m app.copy_database --source "$RAILWAY_DATABASE_URL" --target sqlite:///career_platform.db`.

## Environment

Copy `.env.example` to `.env` and adjust values if needed.

`DATABASE_URL` selects the database. Leave it unset to use `career_platform.db`.

Run the tests against Postgres with `TEST_DATABASE_URL=postgresql://localhost/career_platform_test pytest`. The tests drop every table, so only local databases are accepted.

## Deploy

Production runs on Railway, built and started with the settings in `railway.json`. The web service's `DATABASE_URL` references the Postgres service.

**Deploy branch: `main`, auto-deploy on.** Every push to `main` builds and deploys with no manual step, so a push to `main` is a production release. Railway records each deploy on GitHub in the `chic-flexibility / production` environment. On 2026-10-20 each push's deploy started within seconds and succeeded 40–90 seconds later. Railway checks `/` before switching traffic to a new deploy (`healthcheckPath` in `railway.json`), so a build that doesn't start keeps the old one serving.

A change goes: diff reviewed → `pytest` passes locally → commit → push to `main` → Railway deploys → check the live site. One change recorded end to end: [`docs/evidence/reviewed-change.md`](docs/evidence/reviewed-change.md).

### Rolling back a bad deploy

**Code.** The fastest way is in the Railway dashboard: web service → Deployments → pick the last good deployment → **Redeploy**. That serves the old build within a minute, without touching git. Then fix `main` so the next push doesn't bring the bad code back: `git revert <bad sha>`, run `pytest`, and push. The revert deploys like any other change.

**Database.** The app never drops or rewrites columns. At startup, `ensure_columns` only adds missing ones, so older code still runs against a newer schema, and a code rollback doesn't need a database rollback. If a deploy or a manual edit damaged the data:

1. Before any risky change, take a backup: `pg_dump "$RAILWAY_DATABASE_URL" > railway-$(date +%Y%m%d-%H%M).sql` (kept outside the repo). Railway runs PostgreSQL 18, and `pg_dump` refuses to dump a newer server than itself. The laptop's Homebrew `pg_dump` is 16, so use 18: `brew install postgresql@18`, then `/opt/homebrew/opt/postgresql@18/bin/pg_dump`.
2. To restore, roll the code back first, then load the backup into an empty schema: `psql "$RAILWAY_DATABASE_URL" -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'` followed by `psql "$RAILWAY_DATABASE_URL" < railway-<date>.sql`.
3. Check: `curl -s https://tristaninfo.me/api/profile` shows `"source": "database"` and the expected content.

While the database is broken, visitors still see the profile from the fallback snapshot, and project pages return `503` instead of wrong data.

One-off data copy from SQLite into Postgres:
`python -m app.copy_database --source sqlite:///career_platform.db --target "$DATABASE_PUBLIC_URL"`
It refuses to write into a database that already has rows unless you pass `--replace`.

### Who manages what: Azure VM vs Railway

| | Azure VM (staging) | Railway (production) |
|---|---|---|
| OS | Me: Ubuntu 24.04, patched with `apt` | Railway: the container base image Railpack picks |
| Python runtime | Me: system CPython 3.12.3 plus a `uv` venv | Railway: Railpack installs Python and the locked dependencies from `uv.lock`. I choose the versions |
| Entry point | Me: systemd unit runs uvicorn on `127.0.0.1:8000`, behind nginx | Me: `startCommand` in `railway.json`. Railway runs it, healthchecks `/`, and restarts it on failure |
| TLS | Me: Certbot + Let's Encrypt on nginx, renewed by `certbot.timer` | Railway: Let's Encrypt at Railway's edge, renewed automatically |
| Code | Me: `git pull` on the VM, then restart the service | Me: push to `main`. Railway builds and deploys it |
| Config | Me: `.env` file on the VM | Me: service variables in the Railway dashboard (`DATABASE_URL` references the Postgres service) |
| Database software | Me: the SQLite library, nothing to run | Railway: managed PostgreSQL 18.6 |
| Data | Me: one file on the VM's OS disk, backed up by hand | Me for the content. Railway stores it on the Postgres service |
| DNS | Me: Cloudflare | Me: Cloudflare (unchanged) |

Moving to Railway handed over the OS, the runtime install, TLS and the database server. I still own the code, the start command, the config values, the content and DNS.

### Rollback to the Azure VM

The VM's SQLite file stopped receiving changes at cutover (2026-10-08). Anything written to Railway Postgres since then isn't on the VM. A rollback therefore copies the data back first, then moves DNS:

1. **Freeze edits** on the Railway database until the rollback is finished.
2. **Back up Postgres:** `pg_dump "$RAILWAY_DATABASE_URL" > railway-$(date +%Y%m%d).sql`. Keep this file out of the repo. Use `pg_dump` 18 (see the note under "Rolling back a bad deploy").
3. **Start the VM** (`az vm start -g RG-CAREER-PLATFORM -n vm-career-platform`) and back up its current database: `sqlite3 career_platform.db ".backup ~/career_platform.db.bak-$(date +%Y%m%dT%H%M%S)"`.
4. **Copy Postgres into a fresh SQLite file** on the laptop. The copy command works in either direction, and a new file needs no `--replace`:
   `python -m app.copy_database --source "$RAILWAY_DATABASE_URL" --target sqlite:///rollback.db`
   It prints the row counts and stops if any table's count doesn't match.
5. **Swap it in on the VM.** Don't `git pull` on the VM before this step: `career_platform.db` stopped being tracked on 2026-10-20, so pulling would delete the VM's copy. To bring the VM's code up to date, run `git pull` only after the backup in step 3, then put the database back. **Swap:** `scp` `rollback.db` over, `sudo systemctl stop career-platform`, move it to `~/career-platform/career_platform.db`, then `sudo systemctl start career-platform`.
6. **Check on the VM** before DNS points there: `curl -s -H 'Host: tristaninfo.me' localhost:8000/api/profile` should show `"source": "database"` and the current email. Also check that `sudo certbot certificates` shows a valid certificate. The VM's certificate expires 2027-01-04 and only renews while the VM is running.
7. **Move DNS** in Cloudflare: replace the apex CNAME to `aq2r9r5b.up.railway.app` with `A tristaninfo.me → 20.221.247.215`, DNS only. Then run `dig +short tristaninfo.me` and `curl -s https://tristaninfo.me/api/profile` again.

To undo the rollback, put the CNAME back. If content changed on the VM in the meantime, copy SQLite → Postgres with `--replace` first.

## Azure VM (staging, now deallocated)

Before Railway, the site ran on an Azure VM: `vm-career-platform` in resource group `rg-career-platform`, region North Central US, Ubuntu 24.04. Since the Railway cutover it has been **deallocated**, which means it's stopped and not billed for compute. Its disk and static IP are kept so it can serve as a rollback. Checked 2026-10-20 with `az vm show -d`: `"powerState": "VM deallocated"`.

| | |
|---|---|
| Public IP | `20.221.247.215` (static) |
| Private IP | `172.16.0.4`, on subnet `snet-northcentralus-1` in `vnet-northcentralus-1` |
| NSG `vm-career-platform-nsg` | `Allow-SSH-Laptop`: TCP 22 from the laptop's IP only (priority 300) |
| | `Nginx`: port 80 from anywhere (310) |
| | `Allow-HTTPS-443`: TCP 443 from anywhere (320) |

Port 8000 has no rule. uvicorn listens on `127.0.0.1:8000`, so only nginx on the VM can reach it.

### What made it survive a restart

- **`systemctl enable career-platform`** linked the unit into `multi-user.target.wants` (via `WantedBy=multi-user.target`), so systemd starts the app on every boot without anyone logging in. Before this, the app ran under `nohup` and a reboot would have left the site down.
- **`Restart=always` / `RestartSec=3`** brings the app back if the process dies. `--workers 2` keeps one worker serving while a crashed one is replaced.
- **`WorkingDirectory=/home/azureuser/career-platform`** makes the relative paths in `.env` (`career_platform.db`, `data/fallback-profile.json`) and the `static`/`templates` folders resolve. Without it the service would start in `/`, find no database, and serve the fallback or fail.
- **nginx's own systemd service** is enabled by the Ubuntu package, so the reverse proxy and TLS on 80/443 also come back on boot.

The database is a file on the VM's OS disk, which survives reboots and deallocation, so after a restart the app reads the same data.

**Not done: a controlled reboot test.** The operate-the-VM plan left the reboot test (`sudo reboot`, then reload the site and check `"source": "database"`) for later. It was never run before the site moved to Railway, and the VM was retired instead of being kept running. Restart survival on Azure is therefore shown by the configuration above (`is-enabled` → `enabled` for both services, recorded 2026-10-03 in `docs/superpowers/plans/2026-10-01-operate-the-vm.md`), not by an observed reboot. On Railway, restarts are handled by the platform (`restartPolicyType: ON_FAILURE` in `railway.json`).

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
