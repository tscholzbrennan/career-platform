# HTTPS: tristaninfo.me

## Railway's certificate

Checked 2026-10-20 16:28 PDT from the laptop:

```
$ echo | openssl s_client -connect tristaninfo.me:443 -servername tristaninfo.me 2>/dev/null \
    | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
subject=CN=tristaninfo.me
issuer=C=US, O=Let's Encrypt, CN=YR1
notBefore=Oct  8 21:21:33 2026 GMT
notAfter=Jan  6 21:21:32 2027 GMT
X509v3 Subject Alternative Name:
    DNS:tristaninfo.me
```

- **Hostname:** `tristaninfo.me` only. `www.tristaninfo.me` isn't on this certificate, so `www` can't be served by Railway directly. That's why the plan is a Cloudflare redirect (see below).
- **Validity:** 90 days, 2026-10-08 to 2027-01-06. It was issued on the day the domain was added to Railway.
- **Renewal:** Railway requests and renews the Let's Encrypt certificate for custom domains itself. Nothing to run by hand, as long as the apex CNAME keeps pointing at Railway and the record stays DNS-only (not proxied), so Railway can complete the validation.

## www

Checked 2026-10-20 16:28 PDT:

```
$ curl -sIL --max-time 10 http://www.tristaninfo.me    # no response
$ curl -sIL --max-time 10 https://www.tristaninfo.me   # no response
$ dig +short www.tristaninfo.me
20.221.247.215
```

`www` still points at the Azure VM, which is deallocated, so both requests time out. The site's address is the root, `https://tristaninfo.me`; nothing on the site links to `www`.

**Decision (2026-10-20):** leave `www` as it is. The professor confirmed this is acceptable for Project 1. If `www` is needed later, the fix is to make the `www` record proxied (any placeholder IP, such as `192.0.2.1`) and add a Cloudflare redirect rule from `*://www.tristaninfo.me/*` to `https://tristaninfo.me/${2}` (301, keeping the query string). The root record stays DNS-only so Railway can keep renewing its certificate.
