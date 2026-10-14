# DNS Records Before Zoho Mail: tristaninfo.me

Date recorded: 2026-10-13 22:04 UTC.

Source: Cloudflare's `cf` CLI (`1.0.0-beta.16`), listing the live records for the `tristaninfo.me` zone:

```
$ cf dns records list --zone tristaninfo.me
```

The zone holds **10 records**. A second listing with `--per-page 5000` also returned 10, so nothing was cut off by paging.

**Note:** this is not a true "before" snapshot. The Zoho records (verification TXT, three MX, SPF, DKIM) were created on 2026-10-13 between 21:23 and 21:25 UTC, and the DMARC record at 22:01 UTC, all before this listing. The records that predate the Zoho work are the `www` A record, the apex CNAME to Railway, and the Railway verification TXT.

## Records

| Type | Name | Content | Priority | TTL | Proxy | Last modified (UTC) |
|---|---|---|---|---|---|---|
| A | `www.tristaninfo.me` | `20.221.247.215` |  | Auto | DNS only | 2026-10-01 21:41 |
| CNAME | `tristaninfo.me` | `aq2r9r5b.up.railway.app` |  | Auto | DNS only | 2026-10-08 22:18 |
| MX | `tristaninfo.me` | `mx.zoho.com` | 10 | 600 | DNS only | 2026-10-13 21:25 |
| MX | `tristaninfo.me` | `mx2.zoho.com` | 20 | 600 | DNS only | 2026-10-13 21:25 |
| MX | `tristaninfo.me` | `mx3.zoho.com` | 50 | 600 | DNS only | 2026-10-13 21:25 |
| TXT | `_dmarc.tristaninfo.me` | `"v=DMARC1; p=none; rua=mailto:tristan@tristaninfo.me"` |  | Auto | DNS only | 2026-10-13 22:01 |
| TXT | `_railway-verify.tristaninfo.me` | `"railway-verify=2c397bc8ae53198c791d9a0ce926d37d09dd4bb8a14756a84b049d2d352cae11"` |  | Auto | DNS only | 2026-10-08 22:19 |
| TXT | `tristaninfo.me` | `"v=spf1 include:zohomail.com ~all"` |  | 3600 | DNS only | 2026-10-13 21:25 |
| TXT | `tristaninfo.me` | `"zoho-verification=zb16547835.zmverify.zoho.com"` |  | Auto | DNS only | 2026-10-13 21:23 |
| TXT | `zmail._domainkey.tristaninfo.me` | `"v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC6plfzI5rQjxlwpWZMaOzJV2/fmWP4px9r/yizJOGuOYdu/B0zN9dGlUDoE7WFZ158VROaGDIDAJG+ABLGR300pNCEm0EqakUDTMsHiuo7VKSqMyR4TUevGQPgIYx1grbTUwyhg+2VWoobbaBSr6fusR7MpSCfAXSzUlca4srAQwIDAQAB"` |  | 600 | DNS only | 2026-10-13 21:25 |

TTL "Auto" is Cloudflare's automatic TTL (stored as `1`). No record has a comment or tags.
