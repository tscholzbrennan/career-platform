# A reviewed change through Railway

The change: when project rows can't be read, `/`, `/projects` and `/projects/<slug>` return `503` with "Projects temporarily unavailable", instead of showing sample projects (or, on a project page, a misleading `404`). Times are Pacific (PDT) unless marked UTC.

## 1. Diff reviewed

Made with Claude Code on 2026-10-20. The full diff of `app/main.py`, `app/services/content_service.py`, `templates/index.html` and `templates/projects.html` was printed in the session and checked before I approved the commit. What was checked:

- Only project reads changed. Experience, education and skills still fall back to an empty result.
- The profile is still loaded on the 503 pages, so my name and contact links stay visible.
- `get_project_by_slug` no longer turns a database error into a `404`.
- `/` no longer falls back to the snapshot's `featured_projects`.

## 2. Local check

Tests written first and seen failing (3 failed, 7 passed in `tests/test_failure_states.py`), then the code change, then the full suite:

```
$ uv run python -m pytest -q
50 passed, 59 warnings in 1.20s
```

The new tests cover a 503 with no sample projects on all three project pages, and projects coming back on the next request once the database recovers, with no restart.

## 3. Commit

`eb5d5ab266714387391b523ad473a46cd60f8a83`, "fix: return 503 when project reads fail instead of showing sample projects", 2026-10-20 16:20:29, pushed to `main`.

## 4. Railway deployment

Railway deploys every push to `main` and reports each deploy to GitHub (`GET /repos/tscholzbrennan/career-platform/deployments`, environment `chic-flexibility / production`).

- No GitHub deployment record names `eb5d5ab` itself. The previous deployment (`08c52d2`) went `inactive` at 23:21:37 UTC, about a minute after the push, which means it was replaced. My guess is that `eb5d5ab` was built without a record, but I haven't checked that in the Railway dashboard.
- `7b41cca`, pushed 6 minutes later, deployed `success` at 23:27:37 UTC.
- `40a92f7`, deployed `success` at 23:33:52 UTC, contains `eb5d5ab` (`git merge-base --is-ancestor eb5d5ab 40a92f7` exits 0). Every deploy since then includes the change.

## 5. Live result

Checked 2026-10-20 23:37 UTC against `https://tristaninfo.me`:

```
/ 200
/projects 200
/projects/career-platform 200
"temporarily unavailable" on /projects: 0
```

With the database up, the pages are unchanged: they return `200` and show the real project. The 503 path wasn't triggered in production, because that would mean breaking the live database connection. It's covered by the tests above, which replace the database session with one that raises.
