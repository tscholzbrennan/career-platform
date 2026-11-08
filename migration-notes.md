# AWS Migration Notes

A running log of moving `tristaninfo.me` from Railway to AWS (EC2 + Single-AZ RDS). Plan: [`docs/superpowers/plans/2026-11-03-aws-ec2-rds-migration.md`](docs/superpowers/plans/2026-11-03-aws-ec2-rds-migration.md). Every deviation from that plan is logged below with the reason and what it costs. No secrets go in this file.

## Current state

| | |
|---|---|
| Region | `us-east-1` (N. Virginia), everything in `us-east-1a` |
| EC2 | `i-0696385e9fefe0a9e`, `t3.micro`, Ubuntu 24.04, Elastic IP `44.217.115.62` |
| RDS | `career-platform-db`, PostgreSQL 18.6, `db.t4g.micro`, Single-AZ, not public |
| Security groups | `career-web` (`sg-066ac34b02d19f654`): 80 and 443 from anywhere, 22 from the laptop only. `career-db` (`sg-098df185872c1e670`): 5432 from `career-web` only |
| Test address | `https://aws.tristaninfo.me` (DNS only), Let's Encrypt certificate, HTTP redirects to HTTPS |
| Live site | Still Railway until cutover (Task 8) |
| Branch | `feat/aws-ec2-rds`, pushed; `main` untouched |

## Deviations from the plan

| Date | Plan said | What happened instead | Why | Cost if wrong |
|---|---|---|---|---|
| 2026-11-03 | Use the AWS MCP server for AWS work | AWS CLI with `--profile isba-4775` | The MCP failed to connect at first; later its `run_script` tool returned "Unknown tool", and it can't pass the database password without putting it in the transcript | None to the build |
| 2026-11-03 | Private subnets and a route table with no internet route for RDS | RDS in the default subnets (`career-db-default`, `us-east-1a` + `us-east-1b`), public access off | IAM policy `ISBA4775EC2Migration` denies `CreateSubnet` and `CreateRouteTable`; the user chose this over widening the policy | One fewer network layer: RDS has no public address and only `career-web` can reach 5432, but turning public access on would now need only a setting and a rule |
| 2026-11-03 | `career-web` gets its SSH rule in Task 3 | Rule added in Task 5, when the server existed | No reason to open a port with nothing behind it | None |
| 2026-11-03 | RDS automated backups kept 7 days | 1 day | The Free plan rejected 2 to 7 days (`FreeTierRestrictionError`) | RDS can only restore to about the last day, so the off-AWS `pg_dump` copies are the real long-term backup |
| 2026-11-03 | EC2 `t4g.micro` (ARM) | `t3.micro` (x86) | `ISBA4775EC2Migration` statement `DenyOtherLaunchSizes` allows only `t3.micro` and `t3.small` | About $1.50/month more by remembered rates |
| 2026-11-03 | Cost estimate from the pricing API | Estimate uses remembered rates for EC2, RDS, and storage | `pricing:GetProducts` is denied and AWS's pricing pages came back without rate tables | The ~$25.90/month estimate could be off; check the Billing page after the first full day |
| 2026-11-07 | Launch one instance | Two launched; the duplicate (`i-0db073e40884bf553`, EIP `3.91.107.88`) was terminated and released about 15 minutes later with the user's approval | A launch the user interrupted had already created the first instance, and the rerun didn't stop when it found it | A few cents. Now: check for existing tagged resources and stop before rerunning a create |
| 2026-11-07 | nginx `http2 on` style config | `listen 443 ssl http2;` | Ubuntu 24.04 ships nginx 1.24, which predates the separate `http2 on` directive | None |
| 2026-11-07 | Commit messages as written | Rewrote the three branch commits' messages before pushing (files unchanged) | A shell heredoc dropped each message's first line | None; nothing had been pushed |
| 2026-11-07 | `DATABASE_URL` with TLS options only | Added `connect_timeout=5&tcp_user_timeout=5000` | Step 13 outage test: with packets silently dropped, requests hung over 40 s and froze the whole site, because the async routes call the database synchronously | Database failures now surface in 5 to 12 s instead of hanging. The underlying freeze (the event loop blocks during any slow DB call) is still open, as a finding for the final review |
| 2026-11-07 | Plan silent on nginx's default site | Left enabled on port 80 for now | The security group doesn't open 80, and Task 7 replaces it | None while 80 stays closed |
| 2026-11-07 | `aws` record created in Task 7 Step 4, **proxied**, after the origin certificate | `A aws.tristaninfo.me → 44.217.115.62`, **DNS only**, created now with the Cloudflare CLI (record ID `6b3bb416…`). No other record changed: 10 before, 11 after, every existing record identical | The professor's instructions call for a DNS-only `aws` record | The server's IP is now in public DNS and DNS-history services keep it even after a later change. `aws.tristaninfo.me:443` times out until a security group rule allows direct visitors, and the planned Cloudflare origin certificate isn't browser-trusted for direct visits, so Task 7's HTTPS design needs revisiting |
| 2026-11-07 | Task 7: Cloudflare origin certificate; 443 open only to Cloudflare's ranges; no port 80 | Let's Encrypt certificate for `aws.tristaninfo.me` from certbot (`certonly --webroot`, renewed by `certbot.timer`, nginx reloaded by a deploy hook); **80 and 443 open to everyone**; port 80 serves only the ACME challenge and 301s everything else to HTTPS | The `aws` record is DNS only per the professor, so visitors connect directly and need a browser-trusted certificate; Let's Encrypt validates over port 80 | The server is directly reachable from the internet, and Cloudflare's proxy no longer shields it. The repo's `deploy/nginx-career-platform.conf` was rewritten to match. Cloudflare `real_ip` lines kept: harmless for direct visitors (only Cloudflare's ranges are trusted) and useful if the root domain is proxied later |
| 2026-11-07 | Plan silent on certbot's account email | Registered with `--register-unsafely-without-email` | Avoided sending your email to a third party without asking | No expiry warning emails from Let's Encrypt; renewal is automatic, and the timer plus `certbot renew --dry-run` were checked |
| 2026-11-07 | nginx default site left on 80 until Task 7 | Removed; the career-platform site is now `default_server` on 80 and 443 | It would have answered on port 80 once that port opened | None |

## Test results: aws.tristaninfo.me (2026-11-08 UTC)

| Check | Result |
|---|---|
| HTTP to HTTPS | 301 on every path, query strings kept; bare IP also redirects |
| Certificate | Let's Encrypt `YE2`, CN and SAN `aws.tristaninfo.me`, valid until 2027-02-06; `certbot renew --dry-run` succeeded |
| Crawl | 13 URLs (8 pages, CSS, 2 JS, font, resume PDF), all 200, about 200 to 420 ms from California |
| Error handling | Unknown page: custom 404; unknown project: 404; unknown API route: JSON 404; `HEAD /`: 405 (same on Railway) |
| Data | `/api/profile` byte-identical to Railway; `source: database`, not degraded |
| Content vs Railway | Visible text identical on all pages except `/privacy` (intended wording change); CSS, JS, font, and PDF byte-identical |
| Reboot | Back serving from the database 22 s after `reboot`, no manual steps; app, nginx, certbot timer enabled and active; swap back on; no leftover firewall rules |
| Logs | All logged errors and 503s fall in 01:22 to 01:25 UTC, the outage tests; none since the reboot. nginx logs the visitor's real IP |
| Resources | 398 of 909 MB RAM, swap unused, disk 51% |

**Open finding:** `/privacy` now says requests "pass through Cloudflare first". That was written for the planned Cloudflare-proxied setup. `aws.tristaninfo.me` is DNS only, so it's not true there, and it's only true at cutover if `tristaninfo.me` is proxied. Fix the wording once the cutover design is decided.

