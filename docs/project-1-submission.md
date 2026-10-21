# Project 1 Submission

| | |
|---|---|
| Repository | <https://github.com/tscholzbrennan/career-platform> |
| Live site | <https://tristaninfo.me> (`www.tristaninfo.me` redirects there) |
| Final commit | Added at submission, along with the tag `project-1` |

Everything below is in this repository. README links point to sections of [`README.md`](../README.md).

## README, spec and plans

- [README](../README.md): what the site does, setup, update steps, deploy and rollback
- [Spec: career platform resume site](superpowers/specs/2026-09-15-career-platform-resume-site-design.md)
- [Plan: move to the Azure VM](superpowers/plans/2026-09-24-azure-vm-migration.md)
- [Plan: operate the VM](superpowers/plans/2026-10-01-operate-the-vm.md) (systemd, nginx, HTTPS)
- [Plan: move to Railway + PostgreSQL](superpowers/plans/2026-10-08-railway-postgres-migration.md). The spec for this move was the request in conversation, quoted in the plan.

## 1. Personal application

- Profile and project reads, empty-table and outage behaviour: [README: Fallback profile behavior](../README.md#fallback-profile-behavior)
- Outage, 503 and recovery tests: [`tests/test_failure_states.py`](../tests/test_failure_states.py)
- Initial database choice: [README: SQLite as the first database](../README.md#sqlite-as-the-first-database)

## 2. Azure deployment

- [README: Azure VM (staging, now deallocated)](../README.md#azure-vm-staging-now-deallocated): public and private IPs, NSG rules, SSH restricted to the laptop's IP, current state
- [README: What made it survive a restart](../README.md#what-made-it-survive-a-restart). The controlled reboot test was **not run**, and the README says so. The instructor confirmed the VM doesn't need to keep running.
- HTTP, service and nginx evidence: [operate-the-VM plan](superpowers/plans/2026-10-01-operate-the-vm.md), [Azure migration plan](superpowers/plans/2026-09-24-azure-vm-migration.md), [`evidence/ex03.md`](evidence/ex03.md)

## 3. Domain and HTTPS

- [DNS records and their purposes](evidence/dns-before-zoho.md)
- [HTTPS certificate and `www` redirect](evidence/https.md): Railway's certificate, renewal, and dated before/after `curl` and `openssl` checks
- [How this site is secured](how-this-site-is-secured.md): my Exercise 04 HTTPS explanation (VM era)

## 4. Railway and PostgreSQL migration

- [Migration plan](superpowers/plans/2026-10-08-railway-postgres-migration.md): dependency inventory, PostgreSQL compatibility, the data copy and table-by-table comparison (Task 3), deploy (Task 4) and cutover (Task 5) results
- [README: How the move preserved the data](../README.md#how-the-move-preserved-the-data)
- [README: Rollback to the Azure VM](../README.md#rollback-to-the-azure-vm), covering data written after cutover
- [README: Who manages what: Azure VM vs Railway](../README.md#who-manages-what-azure-vm-vs-railway)
- Diagrams: [README: Architecture](../README.md#architecture) and [`request-path-diagrams.md`](request-path-diagrams.md)

## 5. Verified website update

- [A reviewed change through Railway](evidence/reviewed-change.md): diff, tests, commit `eb5d5ab`, Railway deployment, live result
- [README: Deploy](../README.md#deploy) (branch `main`, auto-deploy) and [README: Rolling back a bad deploy](../README.md#rolling-back-a-bad-deploy) (code and database)

## 6. Zoho email

- [Exercise 06 results sheet](evidence/ex06.md): received, replied, sent, and before-MX rows, plus SPF/DKIM/DMARC results
- [Zoho header check (Test 02)](evidence/zoho-header-check.md), including the unresolved Spam result
- [README: Email and analytics](../README.md#email-and-analytics): the before-MX timeline, what MX, SPF, DKIM and DMARC do, and which tests used webmail and which used the MCP server

## 7. GA4

- [Exercise 06 results sheet, section 3](evidence/ex06.md#3-analytics): live and Privacy links, Realtime screenshots of `page_view` and the GitHub `click`
- [README: How a visit reaches GA4](../README.md#how-a-visit-reaches-ga4) and [Why the outbound click event matters here](../README.md#why-the-outbound-click-event-matters-here)

## 8. Engineering record

- [README: Decisions](../README.md#decisions): SQLite, the move to Railway, and managed vs self-hosted email
- [README: Failures investigated](../README.md#failures-investigated): [`ex03.md`](evidence/ex03.md) (build and Azure migration) and [`ex05.md`](evidence/ex05.md) (DNS/TLS, simulated)
- [README: Remaining limitations](../README.md#remaining-limitations)
- [README: Reflection](../README.md#reflection)
- [README: Costs, expirations and cleanup](../README.md#costs-expirations-and-cleanup), including the Railway trial end date (2026-11-07)
