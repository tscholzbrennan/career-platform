# Zoho Mail Header Check: tristaninfo.me

Date recorded: 2026-10-13.

The test message "Test 02: Outbound" was sent from Zoho Mail (`tristan@tristaninfo.me`) to my Gmail address and delivered to Gmail's Spam folder. This record covers the headers only. The message body is left out, and my Gmail address is shown as `<my Gmail address>`.

## Result

| Check | Result | Domain checked | Aligned with From (`tristaninfo.me`) | Reported by |
|---|---|---|---|---|
| SPF | **pass** | `tristaninfo.me` (envelope sender `tristan@tristaninfo.me`), sending IP `165.173.180.52` | Yes | Gmail and Zoho |
| DKIM | **pass** | `d=tristaninfo.me`, selector `zmail` | Yes | Gmail and Zoho |
| DMARC | **pass according to Zoho only** | `header.from=tristaninfo.me` | Yes | Zoho (ARC i=1). Gmail recorded no DMARC result |
| ARC | pass | `zohomail.com` seal (i=1) | n/a | Gmail |

SPF and DKIM both pass for `tristaninfo.me`, the same domain as the visible From address. Each one aligns on its own, so the message would satisfy DMARC.

Gmail's own `Authentication-Results` line lists `dkim`, `arc` and `spf` but has no `dmarc=` entry. The message was sent at 21:56:16 UTC, and the `_dmarc.tristaninfo.me` record was created in Cloudflare at 22:01 UTC (see `dns-before-zoho.md`). So no DMARC record was published when Gmail checked this message. The `dmarc=pass` comes only from Zoho's own check, carried in the ARC header.

## Delivery path

1. `mail.zoho.com` → `mx.zohomail.com`, Tue, 13 Oct 2026 14:56:16 -0700.
2. `sender6-of-o52.zoho.com [165.173.180.52]` → `mx.google.com` over ESMTPS, `TLS1_3`, `TLS_AES_256_GCM_SHA384`, 14:56:18 -0700.

## Header excerpts

Gmail's verdict:

```
Authentication-Results: mx.google.com;
  dkim=pass header.i=@tristaninfo.me header.s=zmail header.b=LIvGfB0y;
  arc=pass (i=1 spf=pass spfdomain=tristaninfo.me dkim=pass dkdomain=tristaninfo.me dmarc=pass fromdomain=tristaninfo.me>);
  spf=pass (google.com: domain of tristan@tristaninfo.me designates 165.173.180.52 as permitted sender) smtp.mailfrom=tristan@tristaninfo.me
Received-SPF: pass (google.com: domain of tristan@tristaninfo.me designates 165.173.180.52 as permitted sender) client-ip=165.173.180.52;
Return-Path: <tristan@tristaninfo.me>
```

Zoho's verdict (ARC hop 1):

```
ARC-Authentication-Results: i=1; mx.zohomail.com; dkim=pass
  header.i=tristaninfo.me; spf=pass
  smtp.mailfrom=tristan@tristaninfo.me; dmarc=pass header.from=<tristan@tristaninfo.me>
```

DKIM signature (signature value shortened):

```
DKIM-Signature: v=1; a=rsa-sha256; q=dns/txt; c=relaxed/relaxed; t=1791928577;
  s=zmail; d=tristaninfo.me; i=tristan@tristaninfo.me;
  h=Date:Date:From:From:To:To:Message-Id:Message-Id:Subject:Subject:MIME-Version:Content-Type:Reply-To:Cc;
  bh=Xa/WTPVAOcMXOemuTfbjKOJ5Q+0jkSJEmzsjcub9RQc=; b=LIvGfB0y…
```

Message identity:

```
Date: Tue, 13 Oct 2026 14:56:16 -0700
From: Tristan <tristan@tristaninfo.me>
To: <my Gmail address>
Message-Id: <1a137442a28.2b97057b185487.3531636157042813034@tristaninfo.me>
Subject: Test 02: Outbound
User-Agent: Zoho Mail
```

## Why it went to Spam

Authentication was not the cause. The headers don't say why Gmail filtered the message. The likely causes are that `tristaninfo.me` had no sending history before this day, and that the message was a short "Test" with almost no body. A follow-up test sent after 22:01 UTC should show `dmarc=pass` in Gmail's own `Authentication-Results` line.
