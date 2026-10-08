# How This Site Is Secured

**Question: How do I know my data to your site is encrypted?**

When you visit `https://tristaninfo.me`, your browser and my server set up an encrypted TLS connection before any page or form data is sent. The server proves who it is with a certificate from Let's Encrypt, a certificate authority that your browser already trusts. If someone tried to read or change the traffic on the way, your browser would see that the certificate doesn't match and warn you. If you type `http://` by mistake, the server doesn't serve the page over plain HTTP. It sends you straight to the `https://` address.

## The certificate

- **Issued by:** Let's Encrypt
- **Domains covered:** `tristaninfo.me` and `www.tristaninfo.me`
- **Valid from:** 2026-10-06 21:03:50 UTC
- **Expires:** 2027-01-04 21:03:49 UTC (88 days left on 2026-10-07)
- **Key difference:** Certbot proved I had control of the domain, and Let's Encrypt issued the cert.

## How renewal works

I don't renew the certificate by hand. When Certbot was installed, it set up a systemd timer (`certbot.timer`) that runs `certbot renew` twice a day. Each run checks the certificate and renews it only once it's within 30 days of expiring. Renewal uses the same check Let's Encrypt used the first time: Let's Encrypt asks for a file over port 80 to prove I still control the domain. Certbot then gets the new certificate and reloads nginx so it starts using it.

`sudo certbot renew --dry-run` runs a complete dry run renewal without replacing the real certificate. It passed:

```
Processing /etc/letsencrypt/renewal/tristaninfo.me.conf
Simulating renewal of an existing certificate for tristaninfo.me and www.tristaninfo.me

Congratulations, all simulated renewals succeeded:
  /etc/letsencrypt/live/tristaninfo.me/fullchain.pem (success)
```

**Timer check:** the timer is `enabled` (it starts on boot) and `active`. It last ran at 08:23 UTC and its next run is at 23:44 UTC:

```
$ systemctl list-timers | grep certbot
Wed 2026-10-07 23:44:35 UTC  1h 8min Wed 2026-10-07 08:23:44 UTC  14h ago certbot.timer  certbot.service
```

## Which ports are open

Azure's firewall blocks all inbound traffic unless an inbound port rule allows it.

- **443 (HTTPS), rule `Allow-HTTPS-443`:** open to anyone. This is the site itself, encrypted.
- **80 (HTTP), rule `Nginx`:** open to anyone. This port only redirects you to HTTPS, and it serves no pages. Let's Encrypt also uses it to check the domain each time it renews the certificate, and looks for the file Certbot placed there.
- **22 (SSH), rule `Allow-SSH-Laptop`:** open only to my laptop's IP address. This is how I log in to manage the server. Login is by SSH key only. Every other address on the internet is blocked before it reaches the VM.

## Where encryption starts and ends

- **It starts in your browser.** Your data is encrypted before it leaves your device.
- **It ends at nginx on my VM.** nginx holds the certificate's private key, which is stored on the VM. nginx decrypts the request there.
- **From nginx to the app, it isn't encrypted.** nginx sends the request on to the app at `http://127.0.0.1:8000` as plain HTTP. That's okay because the traffic never leaves the VM. `127.0.0.1` is the loopback address, so the request goes from one program to another inside the same machine and never crosses the network. Anyone who could read that traffic would already have control of the server.

The Azure firewall only filters by port and address. It doesn't decrypt anything.

## How you can check it yourself in Chrome

1. Go to `https://tristaninfo.me`.
2. Click the icon to the left of the domain in the address bar (the "site information" icon).
3. Click **Connection is secure**.
4. Click **Certificate is valid**.

## openssl output

This command connects to the live site the way a browser does, then prints the certificate the server presented:

```
azureuser@vm-career-platform:~$ openssl s_client -connect tristaninfo.me:443 -servername tristaninfo.me </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates
subject=CN = tristaninfo.me
issuer=C = US, O = Let's Encrypt, CN = YE1
notBefore=Oct  6 21:03:50 2026 GMT
notAfter=Jan  4 21:03:49 2027 GMT
```
