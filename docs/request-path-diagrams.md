# Request Path Diagrams

What happens when a browser opens `tristaninfo.me`. Drafted with Claude Code on 2026-10-20 from the repository's plans and evidence. Anything marked **unknown** isn't recorded in the repository, and the check next to it would confirm it.

## 1. Hardware, addressing and where the services sit (Railway)

```mermaid
flowchart LR
  subgraph home["Home network, private addresses (values from Ex01)"]
    laptop["Laptop: browser + Wi-Fi network interface<br/>Private IP, subnet, default gateway, DNS server<br/>all handed out by DHCP"]
    box["Home router box (unknown: one box or several?)<br/>Access point + switch + router = default gateway<br/>DHCP server, NAT, stateful firewall<br/>Public IP after NAT"]
  end
  modem["Modem or ONT<br/>(unknown: cable or fiber?)"]
  subgraph isp["ISP"]
    resolver["Recursive DNS resolver<br/>(unknown: router, ISP or 1.1.1.1?<br/>check: scutil --dns)"]
  end
  net["Internet routers"]
  subgraph cf["Cloudflare: authoritative DNS only"]
    ns["Nameservers for tristaninfo.me<br/>CNAME to aq2r9r5b.up.railway.app<br/>DNS only, no web traffic passes here"]
  end
  subgraph rw["Railway"]
    edge["Railway edge, public IP<br/>(unknown: check dig tristaninfo.me)<br/>TLS ends here"]
    app["Web service: uvicorn app.main:app<br/>listens on $PORT, plain HTTP"]
    pg[("Railway Postgres<br/>private network only")]
  end

  laptop -- "Wi-Fi" --- box --- modem --- isp --- net
  net --- ns
  net --- edge
  edge -- "HTTP + X-Forwarded-Proto" --> app
  app -- "Postgres protocol, private network<br/>(port: check DATABASE_URL)" --> pg
```

## 2. The request, step by step, with the client and server on each exchange

```mermaid
sequenceDiagram
  autonumber
  participant B as Browser on laptop (client)
  participant D as Recursive resolver (unknown)
  participant C as Cloudflare nameserver
  participant E as Railway edge
  participant A as App, uvicorn
  participant P as Postgres
  Note over B: Assumptions: no cached DNS answer, new TCP connection, user typed tristaninfo.me
  Note over B,E: Every packet leaving home passes AP, switch, router, modem, ISP. Router NATs private source to public IP and lets replies back in (stateful)
  B->>D: DNS query for tristaninfo.me over UDP 53 (client B, server D)
  D->>C: Iterative query via root and .me servers (client D, server C)
  C-->>D: Flattened CNAME answer, Railway address
  D-->>B: Railway edge IP
  B->>E: TCP handshake on port 80, GET / over plain http
  E-->>B: Redirect to https (unknown, check curl -I http://tristaninfo.me)
  B->>E: TCP handshake on port 443 (client B, server E)
  B->>E: TLS ClientHello with SNI tristaninfo.me
  E-->>B: Certificate for tristaninfo.me (issuer and dates unknown, check openssl s_client)
  Note over B,E: Browser checks hostname, dates and chain, then keys are agreed. TLS ends at the edge
  B->>E: GET / encrypted
  E->>A: GET / plain HTTP inside Railway (client E, server A)
  A->>P: Query profile and projects (client A, server P)
  P-->>A: Rows
  A-->>E: 200 HTML
  E-->>B: 200 HTML encrypted, back through NAT to the laptop
  B->>E: Separate requests for /static/css/site.css and /static/js/consent.js
  E->>A: Forwarded the same way
  A-->>B: CSS and JS returned via the edge
```

## 3. What changes on Azure

```mermaid
flowchart LR
  dns["Cloudflare DNS<br/>A record to 20.221.247.215, DNS only"]
  B["Browser on laptop"] -- "TCP 443" --> nsg
  subgraph az["Azure, North Central US"]
    nsg["Network security group<br/>80 and 443 from anyone<br/>22 from laptop IP only<br/>nothing for 8000"]
    subgraph vm["Ubuntu VM vm-career-platform<br/>(private IP unknown: check az vm list-ip-addresses)"]
      nginx["nginx on 443<br/>TLS ends here, Let's Encrypt cert<br/>80 redirects to https"]
      uv["uvicorn, 2 workers, run by systemd<br/>127.0.0.1:8000 only"]
      db[("SQLite file<br/>career_platform.db")]
    end
  end
  B -. "DNS lookup first, separate exchange" .-> dns
  nsg --> nginx
  nginx -- "plain HTTP over loopback" --> uv
  uv -- "file read, same machine" --> db
```
