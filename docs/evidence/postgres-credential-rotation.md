# Rotating the Railway Postgres password

Railway published a security disclosure on 2026-10-21 and paused deployments that day. On 2026-10-22 it recommended that customers rotate their PostgreSQL credentials ([Railway's guide](https://blog.railway.com/p/security-disclosure-recommendation-rotate-postgresql-database-credentials)). I rotated the password on 2026-10-25. Times are UTC. PDT is 7 hours earlier.

## Who uses the password

| Consumer | How it gets the password | What rotation needs |
|---|---|---|
| `career-platform` web service | `DATABASE_URL="${{Postgres.DATABASE_URL}}"`, a reference variable, checked in the service's Raw Editor. It uses the private host `postgres.railway.internal:5432` | A redeploy, so the container reads the new value |
| My laptop | `RAILWAY_DATABASE_URL` in `.env` (the public `DATABASE_PUBLIC_URL`, `switchback.proxy.rlwy.net`). `.env` is in `.gitignore` | Paste the new public URL by hand |

Nothing else connects. There's no CI job or outside tool using the database.

## Before rotating: checks for misuse (20:15 UTC)

Read-only `psql` session with the old password:

- **Sessions:** two idle ones from Railway's private network (`fd12:3e95:…`), opened 2026-10-21 00:56 UTC. That's when the `f470e9d` deploy started, so they were the web app's connection pool. The third session was my own check. There were no unrecognized sessions.
- **Roles:** only `postgres`.
- **Extensions:** only `plpgsql`, the default.
- **Data:** the same 7 tables with the same row counts as the 2026-10-08 copy: profiles 1, experiences 3, projects 1, skills 12, education 1, media 0, fallback_profile_snapshots 0.

## Rotation

| UTC | What happened |
|---|---|
| 20:23 | In the Railway dashboard: Postgres → Database → Config → **Regenerate** password. Railway updated `POSTGRES_PASSWORD`, and `DATABASE_URL` and `DATABASE_PUBLIC_URL` update with it. |
| 20:23:42 | Railway redeployed `career-platform` on its own (reason `redeploy`, commit `f470e9d`). |
| 20:23:48 | Postgres restarted with the new password (`pg_postmaster_start_time()`). All old sessions were dropped. |
| 20:24:40 | The web app opened two new sessions from a new private address, so the redeploy picked up the new password. |
| ~20:25 | New `DATABASE_PUBLIC_URL` pasted into `.env`. |

The site had no database for about 52 seconds, from 20:23:48 to 20:24:40. During that time the fallback profile covers the profile, and project pages return `503`.

## After rotating: verification (20:28 UTC)

```
$ psql "<old URL>" -c "select 1"
psql: error: connection to server at "switchback.proxy.rlwy.net" (66.33.22.230), port 27291 failed: FATAL:  password authentication failed for user "postgres"
```

- **Old password:** rejected, as shown above.
- **New password from `.env`:** connects. Still only the `postgres` role, and the same 7 tables and row counts as before.
- **Sessions:** only the web app's two (opened 20:24:40) and mine.
- **Site:** `https://tristaninfo.me/` and `/projects` both return `200`, and the "Projects temporarily unavailable" message isn't shown.
- **Logs:** with the Railway CLI, `railway logs --service career-platform --deployment` has no `authentication failed` lines. The Postgres log shows exactly two failures, at 20:28:17 and 20:28:18. Those were my own test with the old password above.

## Gaps

- **The old password was pasted in a chat with my coding agent** while I was finding the right variable, before the rotation. It stopped working at 20:23:48.
- **What I can't see:** Postgres doesn't log successful connections by default, so a connection made with the old password before 2026-10-25 wouldn't show up anywhere. The checks above only show that nothing was left behind (roles, extensions, data, sessions).
- **Public access is still on.** Railway suggests turning it off if nothing outside Railway needs it. My local `psql` and `python -m app.copy_database` use it, so I'm keeping it on for now.
- **The live site still runs `f470e9d`.** `2451b41` (docs only) was pushed on 2026-10-21 while deployments were paused, and it was never deployed. The automatic redeploy reused `f470e9d`.
