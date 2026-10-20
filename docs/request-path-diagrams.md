# Request Path Diagrams

What happens when a browser opens `tristaninfo.me`. Drafted with Claude Code on 2026-10-20 from the repository's plans and evidence.

Assumptions: no cached DNS answer and a new HTTPS connection. The dashed line is the DNS lookup, a separate exchange that happens first. The response comes back along the same path, and the browser then requests CSS and JS as separate requests.

## Railway (current)

```mermaid
flowchart LR
  laptop["Laptop browser<br/>private IP"] -- "Wi-Fi" --> router["Home router<br/>gateway, NAT, firewall"]
  router --> isp["Modem, ISP,<br/>internet"]
  isp -. "1. DNS, UDP 53" .-> dns["Cloudflare DNS<br/>CNAME to Railway"]
  isp -- "2. HTTPS, TCP 443" --> edge["Railway edge<br/>TLS ends here"]
  edge -- "3. HTTP, $PORT" --> app["App<br/>uvicorn"]
  app -- "4. SQL, private network" --> db[("Postgres")]
```

## Azure (before the move)

```mermaid
flowchart LR
  laptop["Laptop browser<br/>private IP"] -- "Wi-Fi" --> router["Home router<br/>gateway, NAT, firewall"]
  router --> isp["Modem, ISP,<br/>internet"]
  isp -. "1. DNS, UDP 53" .-> dns["Cloudflare DNS<br/>A 20.221.247.215"]
  isp -- "2. HTTPS, TCP 443" --> nsg["Azure NSG<br/>allows 80, 443"]
  nsg --> nginx["nginx<br/>TLS ends here"]
  nginx -- "3. HTTP, 127.0.0.1:8000" --> app["App<br/>uvicorn, 2 workers"]
  app -- "4. file read" --> db[("SQLite file")]
```

## Not recorded in the repository

- Your private IP, gateway, and DNS resolver: check your Exercise 01 notes or `scutil --dns`.
- Whether your router, access point, and modem are one box.
- Railway's edge address and certificate: check `dig tristaninfo.me` and `openssl s_client -connect tristaninfo.me:443`.
