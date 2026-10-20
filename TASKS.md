# Project 1 Gaps

From the requirements audit on 2026-10-20. Due 2026-10-22, 1:45 PM.

## 1. Profile and project data

- [x] Return 503 and show "Projects temporarily unavailable" when project reads fail, keeping the profile visible — `app/services/content_service.py`, `app/main.py`, templates
- [x] Stop substituting fallback `featured_projects` for failed project reads on `/` — `app/main.py` `home`
- [x] Change the outage tests to expect 503 and no sample projects — `tests/test_failure_states.py`
- [x] Add a test that projects return after the database recovers, without a restart — `tests/test_failure_states.py`
- [x] Explain the initial database engine choice (SQLite) — README decisions section

## 2. Azure deployment

- [x] ~~Run and record a controlled VM restart (site responds, reads database after reboot) — `docs/superpowers/plans/2026-10-01-operate-the-vm.md` or README~~ — VM retired after Railway cutover; README explains the reboot test wasn't run (2026-10-20)
- [x] Explain which parts made restart survival work (systemd `enable`, `WorkingDirectory`, nginx service) — README
- [x] Document the VM's private IP alongside the public IP and network rules — README or `docs/evidence/ex03.md`
- [x] ~~Confirm the VM is still running and keep it running~~ — VM is deallocated, not deleted; state recorded in README (2026-10-20)

## 3. Domain and HTTPS

- [x] ~~Change `www` to a proxied record with a Cloudflare redirect rule to the root — Cloudflare, then record in DNS evidence~~ — professor OK'd leaving `www` as is; decision and fix recorded in `docs/evidence/https.md` (2026-10-20)
- [x] ~~Verify `http://www` and `https://www` both land on the root with a valid cert — `curl -IL` output, dated~~ — not applicable; dated `www` check in `docs/evidence/https.md`
- [x] Record Railway's certificate hostname, validity, and renewal — `openssl s_client` output against `tristaninfo.me`
- [x] Add each DNS record's purpose to the record table — `docs/evidence/dns-before-zoho.md` or README

## 4. Railway and PostgreSQL migration

- [x] Add a Railway migration spec, or note in the plan that the spec was the conversation request — `docs/superpowers/specs/`
- [x] Link the original spec and all plans from the README and submission index — `README.md`, `docs/project-1-submission.md`
- [ ] Record Task 4 results (Railway domain deploy, page checks, seed didn't add rows) — Railway plan, Task 4 — recorded 2026-10-20 except the direct seed row count, which needs a Railway DB read
- [x] Record Task 5 cutover and post-cutover checks (dig, curl, cert, `source: database`) — Railway plan, Task 5
- [x] Write a rollback procedure that covers data written after cutover — README rollback section
- [x] Compare who manages OS, runtime, entry point, TLS, code, config, DB software, data, DNS on Azure vs Railway — README

## 5. Reviewed change through Railway

- [x] Record one change: diff reviewed, local check, commit SHA, Railway deployment, live result — README or new evidence file
- [x] Write code and database rollback for a bad deploy — README rollback section
- [x] Record the Railway deploy branch and auto-deploy setting — README deploy section
- [x] Decide whether to stop tracking `career_platform.db` in the public repo — `.gitignore`, `git rm --cached` — untracked 2026-10-20; clean checkout passes 50 tests and starts

## 6. Zoho email

- [x] Add the before-MX message line and what happened to it — `docs/evidence/ex06.md`
- [x] Explain MX, SPF, DKIM, and DMARC — `docs/evidence/ex06.md` or README
- [x] ~~Send, receive, and reply in Zoho webmail (not only the MCP server), and record it~~ — kept the MCP reply; `ex06.md` says which tests used webmail (send: Test 02; receive: Test01) and that the reply went through the MCP server (2026-10-20)
- [x] Explain the Test 02 Spam result as an unresolved check — `docs/evidence/zoho-header-check.md`
- [x] Link `ex06.md` and `zoho-header-check.md` from the README and submission index

## 7. GA4

- [ ] Explain how browser activity reaches GA4 (consent, gtag, collect request, Realtime) — `docs/evidence/ex06.md` or README
- [ ] Explain why the outbound click event is useful for this site — `docs/evidence/ex06.md`

## 8. Engineering record

- [ ] Add live address, setup, and update steps — `README.md`
- [ ] Add Azure and Railway diagrams with locations, protocols, ports, data flow, email and analytics paths — `README.md`
- [ ] Explain how the migration preserved current data and which responsibilities moved — `README.md`
- [ ] Add two decisions with alternatives (Railway migration, managed vs self-hosted email) — `README.md`
- [ ] Link the two investigated failures (`ex03.md` dependency, `ex05.md` simulated DNS/TLS) and list remaining limitations — `README.md`
- [ ] Write a short reflection — `README.md`
- [ ] Record costs, credits, Railway trial end date, expirations, and cleanup plans — `README.md`
- [ ] Add repo URL, live URL, final SHA, and links for all 8 categories — `docs/project-1-submission.md`

## Loose ends

- [ ] Decide on the uncommitted about-text edit — `data/fallback-profile.json`
- [ ] Check `feat/railway-postgres` and `fix/identity-and-contact-links` are merged, then delete them — `git branch --merged main`
