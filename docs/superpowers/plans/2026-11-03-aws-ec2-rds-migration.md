# Move to AWS (EC2 + Single-AZ RDS) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status: in progress. Tasks 3 and 4 done on 2026-11-03 (RDS is running and billing). Tasks 1, 2, and 5 done on 2026-11-07 (EC2 is running and billing; the app runs on placeholder data). Nothing runs until the user says to.**

## Where things stand (inspected 2026-11-03)

| | |
|---|---|
| Live site | `tristaninfo.me` is DNS-only in Cloudflare and goes straight to Railway (`server: railway-hikari`, no `cf-ray`). Railway ends TLS. `www` is Cloudflare-proxied and 301s to the root at the edge. Mail is Zoho (MX records at Cloudflare). |
| Railway | Trial ends **2026-11-07**, and credit may run out sooner. Pushing `main` auto-deploys. Postgres 18.6. |
| App | FastAPI + Jinja + SQLAlchemy, Python 3.12. No outbound calls. One writer path, and it is not exposed over HTTP. `static/` and `templates/` are relative paths, so `WorkingDirectory` matters. |
| Startup | `create_all`, `ensure_columns`, `seed_data` run at boot and need DDL rights. If the database is unreachable at boot, the process exits. |
| Data | 7 tables, 18 rows (profiles 1, experiences 3, projects 1, skills 12, education 1, media 0, fallback_profile_snapshots 0). Verified dump from 2026-10-29 in `~/backups/career-platform/`. It is stale by cutover, so Task 6 takes a new one. |
| AWS account | Free plan account (ID not published), **Free plan, $120 credits**. CLI profile `isba-4775` (IAM user `isba-student`, EC2 and RDS full access, no IAM, budgets, or pricing). `us-east-1` has only the default VPC `vpc-0e48ef02c6763e4e9` and its default security group. No instances, Elastic IPs, or RDS databases. |
| Local tools | AWS CLI 2.39.3. Postgres 18 client at `/opt/homebrew/opt/postgresql@18/bin`. The `aws-mcp` server fails to connect, so this plan uses the CLI with an explicit profile. |

**Goal:** `tristaninfo.me` is served from one EC2 instance reading a private Single-AZ RDS PostgreSQL 18.6 database, with Railway's current data, before the Railway trial ends.

**Architecture:** One `t3.micro` runs nginx and a single uvicorn process. RDS sits in the default subnets with public access off and no public address, reachable only from the EC2 security group, in the same Availability Zone. (Changed 2026-11-03: policy `ISBA4775EC2Migration` allows only `t3.micro`/`t3.small` and denies creating subnets. The user chose default subnets over widening the policy.) Cloudflare proxies the site, and port 443 on EC2 accepts only Cloudflare's address ranges. The app stays portable: plain Postgres, one `DATABASE_URL`, no AWS code.

```
before: visitor ─▶ Cloudflare DNS (DNS only) ─▶ Railway edge (TLS) ─▶ uvicorn ─▶ Railway Postgres
after:  visitor ─▶ Cloudflare proxy (TLS) ─▶ EC2 :443 nginx (origin cert) ─▶ 127.0.0.1:8000 uvicorn ─▶ RDS :5432 (TLS, no public address)
```

**Tech Stack:** Ubuntu 24.04 x86_64 (`t3.micro`), nginx, systemd, RDS PostgreSQL 18.6 (`db.t4g.micro`), AWS CLI v2, Cloudflare origin certificate, `pg_dump`/`pg_restore` 18.

**Spec:** The user's request on 2026-11-03: "Look at my app and help me plan its move to AWS. Use EC2 for the app and a Single-AZ RDS PostgreSQL database. Work on a new branch so Railway doesn't redeploy from main. Don't create anything yet." Interview decisions the same day: it is for class and stays live afterward; it may move again later; Free plan with no extra spending; no paid Railway fallback; a day or two of downtime is acceptable. The user waived the rubric question.

## Estimated cost

Rates are from memory for `us-east-1`. The pricing API is denied for this user, so check them against the billing page after the first day.

| Resource | Size | Per month |
|---|---|---|
| RDS Single-AZ | `db.t4g.micro` | ~$11.70 |
| RDS storage | 20 GB | ~$2.30 |
| EC2 | `t3.micro` | ~$7.60 |
| EBS | 8 GB gp3 | ~$0.65 |
| Public IPv4 (Elastic IP) | 1 | ~$3.65 |
| **Total** | | **~$25.90, about 4.6 months of $120 credit** |

Free plan accounts are not charged. The account [locks at 6 months from creation or when credits run out](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html), whichever comes first. After that the user has 90 days to upgrade before AWS deletes the account's contents.

## Global Constraints

- Nothing runs until the user says to. Steps marked **(user)** happen in a dashboard or need the user's login. Confirm before each step that creates a billed resource.
- Every AWS command uses `--profile isba-4775 --region us-east-1`. Never use the root user for the CLI.
- Region `us-east-1`. EC2 and RDS both in `us-east-1a`. Avoid `us-east-1e`, which offers neither instance type.
- PostgreSQL **18.6**, `db.t4g.micro`, **Single-AZ** (`--no-multi-az`), `--no-publicly-accessible`.
- Secrets never appear in chat, command text, git, or logs. Generate them with `openssl rand -hex 32` (hex is URL-safe) and read them from a `chmod 600` file. The Railway and RDS URLs are never printed.
- Do not use RDS-managed master passwords: they rotate and would break the server's `.env`.
- Work on branch `feat/aws-ec2-rds`. Nothing reaches `main` until Task 8, because a push to `main` redeploys Railway.
- The user approves every commit and push. Stage files by name. `data/fallback-profile.json` has an uncommitted on-hold edit and is never staged or copied to the server.
- `git tag project-1` and the Project 1 evidence are not changed.
- Tests never touch a remote database (`tests/conftest.py` already enforces this).
- Every task with a live effect ends with an **Undo** block.
- Tick steps and add dated results or deviations in this file while executing. Keep a short result line per task as class evidence.

## Review Focus

1. **`DATABASE_URL` missing on the server:** the app must refuse to start, not serve SQLite placeholder content with a 200. Unit test in Task 1, live check in Task 5.
2. **RDS unreachable at boot or while running:** systemd keeps retrying and the site recovers without a manual restart. Live check in Task 5.
3. **Someone bypasses Cloudflare or reaches the database directly:** direct requests to the Elastic IP and the RDS endpoint time out. Live check in Task 7.
4. **The instance reboots:** the site returns by itself, reading the database. Never tested on Azure. Live check in Task 8.
5. **Content is edited during the freeze:** Railway and RDS diverge silently. The data comparison reruns immediately before the DNS change in Task 8.

---

### Task 0: Preconditions (user)

- [ ] **Step 1: Confirm root MFA and the $30 monthly budget in the console.**
- [ ] **Step 2: Record the account creation date** (account menu → Account) and the resulting lock date here: `____`. Lock date = the earlier of creation + 6 months and the estimated credit run-out.
- [ ] **Step 3: Confirm the Cloudflare login works,** and record the current SSL/TLS mode and the current apex record value here: `____`. This is the DNS undo value. The README records `aq2r9r5b.up.railway.app`.
- [ ] **Step 4: Check whether the pending live email change** (noted 2026-10-20) was applied. Apply content changes on Railway before Task 6, not after.

---

### Task 1: Refuse to start in production without `DATABASE_URL`

Today only Railway is protected. On EC2 a missing value silently selects SQLite.

**Files:**
- Modify: `app/config.py`, `app/db.py`, `app/copy_database.py`, `tests/conftest.py`
- Test: `tests/test_database_url.py`

**Interfaces:**
- Produces: `database_url_required(environ: Mapping[str, str]) -> bool` in `app/config.py`, and `resolve_database_url(raw: str, sqlite_path: str, require_url: bool) -> str` (renames `on_railway`).

- [x] **Step 1: Rename `on_railway=` to `require_url=` in the existing tests, import `database_url_required`, and add the failing tests.**

```python
@pytest.mark.parametrize("environ, expected", [
    ({}, False),
    ({"APP_ENV": "development"}, False),
    ({"APP_ENV": "production"}, True),
    ({"RAILWAY_ENVIRONMENT_NAME": "production"}, True),
])
def test_database_url_required(environ, expected):
    assert database_url_required(environ) is expected


def test_missing_url_when_required_is_an_error():
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        resolve_database_url("", "x.db", require_url=True)


def test_rds_url_keeps_its_tls_options():
    raw = "postgresql://u:p@h:5432/db?sslmode=verify-full&sslrootcert=/x.pem"
    assert resolve_database_url(raw, "x.db", require_url=True) == (
        "postgresql+psycopg://u:p@h:5432/db?sslmode=verify-full&sslrootcert=/x.pem"
    )
```

- [x] **Step 2: Run them and confirm they fail.** Run: `.venv/bin/python -m pytest tests/test_database_url.py -q`. Expected: `database_url_required` import error.
- [x] **Step 3: Implement.** Add `database_url_required` and rename the parameter. Keep the Railway check, since the site may move back. `app/db.py` passes `require_url=database_url_required(os.environ)`. `app/copy_database.py` passes `require_url=False` in both calls. Replace the error message and the Railway-specific comment so they describe production generally. `tests/conftest.py` also pops `APP_ENV`. Read the real process environment, not `.env`, so the guard holds even if `.env` is missing.
- [x] **Step 4: Run the full suite.** Run: `.venv/bin/python -m pytest -q`. Expected: all pass.
**Result, 2026-11-07:** the new tests failed first (import error), then 12 passed; full suite 55 passed.

- [ ] **Step 5: Commit (ask first).** `git add app/config.py app/db.py app/copy_database.py tests/conftest.py tests/test_database_url.py`, message `fix: refuse to start in production without DATABASE_URL`.

---

### Task 2: Server config files and the privacy page

Writing these on the branch means the privacy text only goes live with the cutover.

**Files:**
- Create: `deploy/career-platform.service`, `deploy/nginx-career-platform.conf`, `deploy/journald-retention.conf`, `deploy/deploy.sh`
- Modify: `templates/privacy.html:27,69-70`
- Test: `tests/test_pages.py`

**Interfaces:**
- Produces: service name `career-platform`, app at `/home/ubuntu/career-platform`, uvicorn on `127.0.0.1:8000`, origin certificate at `/etc/ssl/cloudflare/origin.pem` and `origin.key`, RDS CA bundle at `/etc/ssl/rds/global-bundle.pem`.

- [x] **Step 1: Write the failing test** in `tests/test_pages.py`.

```python
def test_privacy_page_names_the_current_hosts():
    client = TestClient(app)
    response = client.get('/privacy')
    assert 'Amazon Web Services' in response.text
    assert 'Cloudflare' in response.text
    assert 'Railway' not in response.text
```

- [x] **Step 2: Run it and confirm it fails.** Run: `.venv/bin/python -m pytest tests/test_pages.py -q`. Expected: fails on `'Amazon Web Services'`.
- [x] **Step 3: Update the privacy page.** Line 27 starts "The site runs on Amazon Web Services (AWS), and requests pass through Cloudflare first." The rest of that paragraph is unchanged. Replace the Railway row with **AWS**: "Hosts the site and stores the server logs for up to 7 days." Add a row for **Cloudflare**: "Receives each request first and passes it on to AWS. It handles your IP address and the page requested to do this." Update any "last updated" date on the page.
- [x] **Step 4: Run the tests.** Expected: all pass.
- [x] **Step 5: Write `deploy/career-platform.service`.** Required values: `After=network-online.target`, `Wants=network-online.target`, `StartLimitIntervalSec=0`, `User=ubuntu`, `WorkingDirectory=/home/ubuntu/career-platform`, `Environment=APP_ENV=production`, `EnvironmentFile=/home/ubuntu/career-platform/.env`, `Restart=always`, `RestartSec=5`, `WantedBy=multi-user.target`.
  `ExecStart=/home/ubuntu/career-platform/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips=127.0.0.1`
  Use one process: more workers would race on the startup seed. Do not copy the `--forwarded-allow-ips=*` from `railway.json`.
- [x] **Step 6: Write `deploy/nginx-career-platform.conf`.** It listens on 443 with `ssl` and `http2` for `tristaninfo.me` and `aws.tristaninfo.me`, using the origin certificate paths above, and `proxy_pass http://127.0.0.1:8000` with `Host` and `X-Forwarded-Proto` set. Use `real_ip_header CF-Connecting-IP` with one `set_real_ip_from` per range in [Cloudflare's published list](https://www.cloudflare.com/ips-v4), so the logged visitor IP matches the privacy page. There is no port 80 server, because Full (strict) reaches the origin on 443.
- [x] **Step 7: Write `deploy/journald-retention.conf`** with `[Journal]` and `MaxRetentionSec=7day`. This keeps the 7-day promise on the privacy page. Task 5 also sets nginx's logrotate to `daily` and `rotate 7`.
- [x] **Step 8: Write `deploy/deploy.sh`.** It runs with `set -euo pipefail`, then `git pull --ff-only`, `.venv/bin/pip install -r requirements.txt`, `sudo systemctl restart career-platform`, waits up to 30 s, then exits non-zero unless `curl -s http://127.0.0.1:8000/api/profile` contains `"source":"database"`.
**Result, 2026-11-07:** the privacy test failed first, then the full suite passed (56). Privacy "Last updated" is November 7, 2026. nginx uses `listen 443 ssl http2` because Ubuntu 24.04 ships nginx 1.24, which predates the separate `http2 on` directive. Cloudflare ranges are copied in as of 2026-11-07 (15). `bash -n deploy/deploy.sh` passes and `systemd-analyze verify` on the server reports nothing but the not-yet-created app paths. nginx's own check (`nginx -t`) waits for Task 7.

- [ ] **Step 9: Commit and push the branch (ask first).** `git add templates/privacy.html tests/test_pages.py deploy/`, message `feat: add EC2 service config and name AWS on the privacy page`. Push only `feat/aws-ec2-rds`, since the server clones it. Confirm in the Railway dashboard that no deploy started.

---

### Task 3: Network

No charge for anything in this task.

- [ ] **Step 1: Find the laptop's IP** with `curl -s https://checkip.amazonaws.com`.
- [x] **Step 2: Create security group `career-web`** in `vpc-0e48ef02c6763e4e9`. Inbound: TCP 22 from the laptop's `/32` only. Port 443 is added in Task 7. Nothing else.
- [x] **Step 3: Create security group `career-db`.** Inbound: TCP 5432 with `career-web` as the source. No CIDR rules.
- [ ] ~~Step 4: Create the private subnets.~~ Dropped 2026-11-03: denied by policy; the user chose default subnets.
- [ ] ~~Step 5: Create route table `career-private`.~~ Dropped for the same reason.
- [x] **Step 6: Create DB subnet group `career-db-default`** from default subnets `subnet-0f279ac4066911cbf` (`us-east-1a`) and `subnet-0f3d547a432fad2d6` (`us-east-1b`). AWS requires two AZs even for Single-AZ.
- [x] **Step 7: Verify.** The subnet group is `Complete` and contains those two subnets.

**Result, 2026-11-03 (partial):** created `career-web` (`sg-066ac34b02d19f654`, no inbound rules; deviation: its SSH rule moves to Task 5, when there is a server to reach) and `career-db` (`sg-098df185872c1e670`, 5432 from `career-web` only). Blocked at Step 4: `ec2:CreateSubnet`, `CreateRouteTable`, and `AssociateRouteTable` are denied. Cause found the same day: the user's account has policy `ISBA4775EC2Migration`, and its statement `DenyOtherLaunchSizes` explicitly denies launching anything but `t3.micro` or `t3.small`. Dry runs under it: allowed are `t3.micro` and `t3.small` (x86 Ubuntu AMI `ami-0d6dd9e8265d48906`), `ImportKeyPair`, `AllocateAddress`, security group changes. Denied are `t4g.micro`, `CreateSubnet`, `CreateRouteTable`, `AssociateRouteTable`, `CreateKeyPair`. RDS actions cannot be dry-run. The user chose `t3.micro` and default subnets, and RDS was then created (Task 4). The Step 1 laptop IP and the SSH rule move to Task 5.

**Undo:** delete the subnet group, then the security groups.

---

### Task 4: RDS

Starts billing, so confirm first.

- [x] **Step 1: Generate two secrets locally** (admin and app passwords) into `~/.career-platform-aws/secrets.env`, with the directory `chmod 700` and the file `chmod 600`, without printing them.
- [x] **Step 2: Check the storage type.** `describe-orderable-db-instance-options --engine postgres --engine-version 18.6 --db-instance-class db.t4g.micro`, then use gp3 if listed, otherwise gp2.
- [x] **Step 3: Create instance `career-platform-db`.** `--engine postgres --engine-version 18.6 --db-instance-class db.t4g.micro --no-multi-az --availability-zone us-east-1a --allocated-storage 20 --db-subnet-group-name career-db-default --vpc-security-group-ids <career-db> --no-publicly-accessible --storage-encrypted --master-username career_admin --backup-retention-period 7 --deletion-protection --copy-tags-to-snapshot --no-manage-master-user-password`, with the password read from the secrets file. Do not create a database yet.
  **Result, 2026-11-03:** the Free plan rejected 7, 6, 5, 4, 3, and 2 days (`FreeTierRestrictionError`) and accepted **1 day**, so `--backup-retention-period 1`. Automated backups only reach back about a day, which makes the Task 9 off-AWS dumps the real long-term backup. Storage: gp3.
- [x] **Step 4: Wait and verify.** `aws rds wait db-instance-available`, then `describe-db-instances` shows `MultiAZ=false`, `PubliclyAccessible=false`, `AvailabilityZone=us-east-1a`, `EngineVersion=18.6`, and the actual `BackupRetentionPeriod`. Save the endpoint to the secrets file.

**Result, 2026-11-03:** `career-platform-db` is `available`: PostgreSQL 18.6, `db.t4g.micro`, Single-AZ in `us-east-1a`, 20 GB gp3, encrypted, not public, deletion protection on, 1-day backups, group `career-db-default`, security group `career-db`. From the laptop, the endpoint resolves to private IP `172.31.0.229` and port 5432 times out. No application database or role exists yet (Task 5 Step 6). Secrets and endpoint are in `~/.career-platform-aws/`.

**Undo:** `modify-db-instance --no-deletion-protection --apply-immediately`, then `delete-db-instance --final-db-snapshot-identifier career-platform-db-final`. The snapshot keeps costing a small amount until deleted.

---

### Task 5: EC2 and the app

Starts billing, so confirm first. Tasks 5 to 7 change nothing users see.

- [x] **Step 1: Generate an SSH key locally,** `ssh-keygen -t ed25519 -f ~/.ssh/career-platform-aws`, and `import-key-pair`. The private key never leaves the laptop.
- [x] **Step 2: Launch one instance.** Get the current Ubuntu 24.04 amd64 AMI from Canonical (`099720109477`; it was `ami-0d6dd9e8265d48906` on 2026-11-03). `t3.micro`, default subnet `subnet-0f279ac4066911cbf` (`us-east-1a`), group `career-web`, 8 GB gp3 root volume, `--metadata-options HttpTokens=required`, `--credit-specification CpuCredits=standard` (no surplus charges), tag `Name=career-platform`. No IAM role is needed because the app calls no AWS APIs.
- [x] **Step 3: Allocate and associate an Elastic IP,** so DNS survives stop and start.
**Result, 2026-11-07:** instance `i-0696385e9fefe0a9e` (`t3.micro`, x86_64, Ubuntu 24.04.5, Python 3.12.3, `us-east-1a`, private IP `172.31.8.24`), Elastic IP `44.217.115.62`, key `career-platform`, encrypted 8 GB gp3 root, IMDSv2 required, standard credits. Status checks ok. SSH works from the laptop. Port 5432 on RDS is reachable from the instance. Port 443 times out from the internet. `career-web` port 22 is open to `164.68.240.107/32` only (deviation from Task 3: added here). Incident: an interrupted launch had already created this instance, and a rerun launched a duplicate (`i-0db073e40884bf553`, EIP `3.91.107.88`). The duplicate was terminated and its EIP released with the user's approval about 15 minutes later. Next time, check for existing tagged resources and stop if any exist before rerunning a create.

- [x] **Step 4: Prepare the server over SSH.** `apt update && apt upgrade`, install `nginx python3-venv git`, add a 1 GB swap file (the instance has 1 GB of RAM), confirm `unattended-upgrades` is active, and download the [RDS CA bundle](https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem) to `/etc/ssl/rds/global-bundle.pem`. Confirm `python3 --version` is 3.12.
- [x] **Step 5: Install the app.** Clone the public repo to `/home/ubuntu/career-platform`, check out `feat/aws-ec2-rds`, create `.venv`, and run `pip install -r requirements.txt`. Confirm `psycopg` imports.
- [x] **Step 6: Create the database and app role** through an SSH tunnel from the laptop (`ssh -N -L 55432:<rds-endpoint>:5432 ubuntu@<eip>`), using the Postgres 18 tools. Ubuntu's own packages are older than 18, so nothing Postgres gets installed on the server. As `career_admin`: `CREATE ROLE career_app LOGIN PASSWORD ...`, `GRANT career_app TO career_admin`, `CREATE DATABASE career_platform OWNER career_app`. The role owns the database because startup runs DDL. Send the password over stdin, not in command text.
- [x] **Step 7: Write the server's `.env`** with `chmod 600`, without printing it. `DATABASE_URL="postgresql://career_app:<password>@<endpoint>:5432/career_platform?sslmode=verify-full&sslrootcert=/etc/ssl/rds/global-bundle.pem&connect_timeout=5&tcp_user_timeout=5000"`, quoted because of the `&`. (Timeouts added 2026-11-07 after Step 13; see the result below.) `FALLBACK_PROFILE_PATH` stays at its default, which is relative to `WorkingDirectory`.
- [x] **Step 8: Prove the guard works.** On the server, from `/tmp` so no `.env` is read: `APP_ENV=production PYTHONPATH=/home/ubuntu/career-platform /home/ubuntu/career-platform/.venv/bin/python -c "import app.db"`. Expected: `RuntimeError` mentioning `DATABASE_URL`.
- [x] **Step 9: Install config.** Copy the service file and journald config into place, set nginx logrotate to `daily` and `rotate 7`, then `systemctl enable --now career-platform`. Do not load the nginx site yet, because the certificate arrives in Task 7. The first start creates tables and seeds placeholder rows. Task 6 replaces them.
- [x] **Step 10: Test TLS to the database.** `SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()` from the server's Python environment returns true.
- [x] **Step 11: Test RDS failure handling, part 1 (Review Focus 2).** Block the database on the server with `sudo iptables -I OUTPUT -p tcp --dport 5432 -j REJECT`, then restart the service. Use this and not a security group change, which leaves open connections alive and so would not simulate an outage. Expected: `systemctl status` shows it retrying and never giving up.
- [x] **Step 12: Part 2.** Remove the block with `sudo iptables -D OUTPUT -p tcp --dport 5432 -j REJECT`. Expected: the service becomes active by itself and `curl -s 127.0.0.1:8000/api/profile` says `"source":"database"`.
- [x] **Step 13: Part 3.** With the service running, add the block again. Expected: `/` returns 503 and `/about` still returns 200 from the fallback. Remove the block. Expected: `/` returns 200 without a restart. Confirm `sudo iptables -S OUTPUT` shows no leftover rule.

**Result, Steps 4 to 13, 2026-11-07:** nginx 1.24, Python 3.12.3, 1 GB swap, unattended-upgrades active, RDS CA bundle in place. App cloned at `2172552`, psycopg 3.3.6 (binary). `career_platform` owned by `career_app`. `.env` mode 600 and git-ignored. Guard raises `RuntimeError` without `DATABASE_URL`. Connection is TLS 1.3 with `verify-full`. Service enabled with `Restart=always`, journald keeps 7 days, nginx logs rotate daily for 7 days. Outage tests: during a block, systemd retried 4 times without giving up, then recovered 2 s after unblocking. **Step 13 first failed**: with packets silently dropped, requests hung over 40 s and froze the whole site, static files included, because the routes are `async def` but query the database synchronously. With `--reject-with tcp-reset` the app behaved as designed. Fix: `connect_timeout=5&tcp_user_timeout=5000` in `DATABASE_URL`. Rerun as written: `/` 503 (first request 12 s, then 0.01 s), `/about` 200, recovered without a restart, no leftover rules. Open finding: a stuck database call still freezes every request for up to about 12 s, because sync calls run on the event loop. Fixing that is an app change (`def` routes) and is left for the final review.

**Undo:** `terminate-instances`, then `release-address` (an unattached Elastic IP keeps billing), then `delete-key-pair`.

---

### Task 6: Load production data

- [ ] **Step 1: Freeze content.** Tell the user: no edits to Railway from here until Task 8.
- [ ] **Step 2: Take a fresh dump** with the Postgres 18 tools: `pg_dump "$RAILWAY_DATABASE_URL" --format=custom --no-owner --file=~/backups/career-platform/railway-<UTC timestamp>.dump`, then record its SHA-256.
- [ ] **Step 3: Empty the target.** Stop the service. Through the tunnel, drop and recreate the `public` schema as `career_app`, which removes the placeholder rows.
- [ ] **Step 4: Restore.** `pg_restore --dbname=<tunnel URL> --no-owner --no-privileges --exit-on-error <dump>`. Expected: exit 0.
- [ ] **Step 5: Compare every table.** Run this query against both Railway and RDS, send each result back through `psql` to execute it, sort, and `diff`. `COLLATE "C"` is required: Railway's locale sorts differently, as found on 2026-10-29.

```sql
SELECT string_agg(format(
  'SELECT %L, count(*), md5(coalesce(string_agg(t::text, %L ORDER BY t::text COLLATE "C"), %L)) FROM %I.%I t',
  schemaname || '.' || relname, '|', '', schemaname, relname), ' UNION ALL ' ORDER BY relname)
FROM pg_stat_user_tables;
```

Expected: no differences, 7 tables, 18 rows unless Task 0 changed content.

- [ ] **Step 6: Start the service and check it.** Expected: `/api/profile` says `"source":"database"` with real content, and the row counts did not change (the seed added nothing). In a transaction that gets rolled back, an insert into `skills` gets a new id.

**Undo:** repeat Steps 3 to 5 from a good dump.

---

### Task 7: Cloudflare to the origin

**Superseded 2026-11-07 for `aws.tristaninfo.me`:** at the user's request, TLS is a Let's Encrypt certificate from certbot (webroot), 80 and 443 are open to everyone, and HTTP redirects to HTTPS. See `migration-notes.md`. The steps below describe the original Cloudflare-proxied design and were not run.

- [ ] **Step 1: (user) Create a Cloudflare origin certificate** for `tristaninfo.me` and `*.tristaninfo.me`, RSA or ECC, 15 years. Paste the certificate and key directly into `/etc/ssl/cloudflare/origin.pem` and `origin.key` over SSH (`chmod 600` on the key). The key is shown once and must not go through this chat.
- [ ] **Step 2: Enable the nginx site.** `sudo nginx -t` passes, then reload. On the server: `curl -sk --resolve tristaninfo.me:443:127.0.0.1 https://tristaninfo.me/api/profile` says `"source":"database"`.
- [ ] **Step 3: Open 443 to Cloudflare only.** Add one `career-web` inbound rule per range in the current [Cloudflare IPv4 list](https://www.cloudflare.com/ips-v4).
**Change, 2026-11-07:** the professor's instructions call for a **DNS-only** `A aws → 44.217.115.62` record, created that day with the Cloudflare CLI (no other record changed). Steps 1 to 6 need revisiting to match: a DNS-only name can't be reached through a Cloudflare-only security group, and an origin certificate isn't browser-trusted.

- [ ] **Step 4: (user) Set SSL/TLS mode to Full (strict)** and add a proxied `A aws → <EIP>` record. The mode is zone-wide, but the apex is DNS-only and `www` redirects at the edge, so neither is affected.
- [ ] **Step 5: Test end to end.** `https://aws.tristaninfo.me/` returns 200 with `cf-ray`, all pages load, and `/api/profile` says `"source":"database"`.
- [ ] **Step 6: Test the walls (Review Focus 3).** From the laptop, `curl --max-time 5 https://<EIP>/` and `nc -zv -G 5 <rds-endpoint> 5432` both time out.

**Undo:** remove the `aws` record and the 443 rules, and restore the SSL mode recorded in Task 0.

---

### Task 8: Cutover

- [ ] **Step 1: Rerun the Task 6 comparison (Review Focus 5).** If it differs, repeat Task 6 before going on.
- [ ] **Step 2: Reboot now, while Railway still serves users (Review Focus 4).** `sudo reboot`. Expected: within about 2 minutes `https://aws.tristaninfo.me/api/profile` says `"source":"database"` with no manual steps.
- [ ] **Step 3: (user) Change only the apex record** in Cloudflare to proxied `A tristaninfo.me → <EIP>`. Do not touch MX, SPF, DKIM, DMARC, or the `www` record.
- [ ] **Step 4: Verify the live site.** `https://tristaninfo.me/` returns 200 with `cf-ray` and no `railway` server header. `/api/profile` says `"source":"database"`. Check every page, the resume PDF, `/privacy` naming AWS and Cloudflare, `www` redirecting to the root, and the certificate in a browser. Send a test email to confirm Zoho mail still works.
- [ ] **Step 5: Merge (ask first).** After cutover works, merge `feat/aws-ec2-rds` into `main`, push, and point the server at `main` with `git checkout main`. Railway may redeploy, which is harmless since no traffic goes there. Run `deploy/deploy.sh` to prove the deploy path works.
- [ ] **Step 6: End the freeze.** Content edits now go to RDS only, through the tunnel.

**Result, 2026-11-08:** Steps 1 to 4 done. The apex record went DNS only, not proxied, to match the Let's Encrypt setup and the professor's DNS-only `aws` record. Cut over at 01:58:47 UTC; certificate expanded to `tristaninfo.me` at 01:59:28 UTC. Every live check passed (details in `migration-notes.md`). Step 5 (merge) waits on the user's pull request; Step 6 freeze ended at cutover.

**Undo:** while the Railway trial is alive, restore the apex record from Task 0 (DNS only). After the trial ends there is no Railway to return to, by the user's decision, so fix forward. Worst case, rebuild from Tasks 3 to 7 and the latest dump.

---

### Task 9: Backups, exit, and records

**Files:**
- Modify: `README.md`, `docs/how-this-site-is-secured.md`, `docs/request-path-diagrams.md`
- Create: `docs/evidence/aws-migration.md`

- [ ] **Step 1: Test an RDS restore once.** Create a manual snapshot, restore it to a temporary `db.t4g.micro` in `career-db-default`, check the row counts through the tunnel, and delete the temporary instance with `--skip-final-snapshot`. This costs a few cents. Confirm first.
- [ ] **Step 2: Take the first off-AWS dump** to `~/backups/career-platform/` through the tunnel with the Postgres 18 tools, and copy it somewhere other than the laptop. **(user)** chooses where. Rule: dump after every content change and at least monthly. RDS backups disappear with the account.
- [ ] **Step 3: (user) Add calendar reminders:** start the exit 30 days before the lock date from Task 0, and check the credit balance monthly. Budget alerts lag and never stop spending.
- [ ] **Step 4: (user, optional) Add a free external uptime monitor** that uses GET on `https://tristaninfo.me/api/profile`. HEAD returns 405 on this app, so a HEAD monitor would false-alarm.
- [ ] **Step 5: Write the exit runbook in the README.** Fresh dump, restore to the new host's Postgres, set `DATABASE_URL`, change the apex DNS record, verify `"source":"database"`, update the privacy page, then run the teardown below.
- [ ] **Step 6: Update the docs.** README: live architecture, deploy (now `deploy/deploy.sh`, and a push to `main` no longer deploys), rollback, who-manages-what with an AWS column, costs and lock date. Rewrite `how-this-site-is-secured.md` and add an AWS diagram to `request-path-diagrams.md`. Record each task's result line in `docs/evidence/aws-migration.md`, with no secrets.
- [ ] **Step 7: Turn off Railway's auto-deploy (user)** if the Railway project is still active, and take a final Railway dump before the trial ends.
- [ ] **Step 8: Commit (ask first).** Stage the files above by name, message `docs: record the AWS migration and exit runbook`.

---

## Appendix: routine fixes and teardown

**Laptop IP changed (SSH times out):** replace the `career-web` port 22 rule with the new `/32`.

**Cloudflare changes its ranges:** compare the published list with the `career-web` rules and the nginx `set_real_ip_from` lines. Check when reviewing credits each month.

**Teardown, so nothing keeps charging:** `modify-db-instance --no-deletion-protection`, `delete-db-instance` (with or without a final snapshot), delete manual snapshots, `terminate-instances`, `release-address`, `delete-key-pair`, delete the DB subnet group, then `career-db` and `career-web`. Finish with `describe-*` across all regions and check the Billing page the next day.
