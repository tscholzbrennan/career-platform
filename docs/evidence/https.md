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

- **Hostname:** `tristaninfo.me` only. `www.tristaninfo.me` isn't on this certificate, so Railway can't serve `www` directly. Cloudflare's proxy redirects it instead (see below).
- **Validity:** 90 days, 2026-10-08 to 2027-01-06. It was issued on the day the domain was added to Railway.
- **Renewal:** Railway requests and renews the Let's Encrypt certificate for custom domains itself. Nothing to run by hand, as long as the apex CNAME keeps pointing at Railway and the record stays DNS-only (not proxied), so Railway can complete the validation.

## www

### Before the fix

Checked 2026-10-20 16:28 PDT:

```
$ curl -sIL --max-time 10 http://www.tristaninfo.me    # no response
$ curl -sIL --max-time 10 https://www.tristaninfo.me   # no response
$ dig +short www.tristaninfo.me
20.221.247.215
```

`www` still pointed at the Azure VM, as a DNS-only A record, and the VM is deallocated, so both requests timed out. A redirect rule "Redirect from www to root" had existed since 2026-10-13 (Cloudflare's template, `http*://www.*` → `https://${2}`, 301), but a rule can only run on a **proxied** record.

### The fix

2026-10-20 17:46 PDT (00:46:57 UTC), with the Cloudflare CLI: the `www` A record changed from `20.221.247.215`, DNS only, to `192.0.2.1`, **Proxied**. `192.0.2.1` is a reserved documentation address. Cloudflare answers every `www` request with the redirect, so the request never reaches that address. The root `tristaninfo.me` CNAME to Railway stays **DNS only**, so Railway keeps serving it and renewing its certificate.

To undo: set `www` back to `A 20.221.247.215`, DNS only.

### After the fix

Checked 2026-10-20 17:47 PDT:

```
$ dig +short www.tristaninfo.me @1.1.1.1
104.21.82.22
172.67.193.113                       # Cloudflare's proxy addresses

$ curl -sIL http://www.tristaninfo.me
HTTP/1.1 301 Moved Permanently
Location: https://tristaninfo.me/
Server: cloudflare

$ curl -sIL "https://www.tristaninfo.me/projects?x=1"
HTTP/2 301
location: https://tristaninfo.me/projects?x=1
server: cloudflare

$ curl -sL -o /dev/null -w '%{url_effective} %{http_code} %{ssl_verify_result}\n' <url>
http://www.tristaninfo.me            -> https://tristaninfo.me/ 200, cert ok (0)
https://www.tristaninfo.me           -> https://tristaninfo.me/ 200, cert ok (0)
https://www.tristaninfo.me/projects?x=1 -> https://tristaninfo.me/projects?x=1 200, cert ok (0)
```

The certificate `https://www` presents is Cloudflare's edge certificate, not Railway's:

```
subject=CN=tristaninfo.me
issuer=C=US, O=Let's Encrypt, CN=YE2
notBefore=Oct  1 21:04:04 2026 GMT
notAfter=Dec 30 21:04:03 2026 GMT
X509v3 Subject Alternative Name: DNS:*.tristaninfo.me, DNS:tristaninfo.me
```

Cloudflare's Universal SSL issues and renews it automatically for proxied names. With `curl -I` (a HEAD request), the last hop shows `405` from Railway, because FastAPI's GET routes don't answer HEAD. A normal GET returns `200`.

So `http://www` and `https://www` both land on `https://tristaninfo.me` with a valid certificate, and the path and query string are kept.
