# Operate the VM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## The VM (found 2026-10-03 with read-only `az` commands)

| | |
|---|---|
| VM | `vm-career-platform`, resource group `RG-CAREER-PLATFORM`, North Central US |
| Size / OS | Standard_B2ats_v2, Ubuntu 24.04 (Linux) |
| Public IP | `20.221.247.215`: static, resource `vm-career-platform-ip`. Look it up with `az vm show -d -g RG-CAREER-PLATFORM -n vm-career-platform --query publicIps -o tsv` |
| Login | `azureuser`, key only (password login is off) |
| SSH | `ssh -i ~/.ssh/isba4775_azure azureuser@20.221.247.215` |
| Firewall (NSG `vm-career-platform-nsg`) | `Allow-SSH-Laptop` (300, port 22, one laptop IP); `Nginx` (310, port 80, source **Any**, which the user set on 2026-10-03). Nothing allows port 8000. |
| Power state on 2026-10-03 | **Deallocated** (stopped). It has to be started before anything else. |
| App on the VM | `~/career-platform`: code, `.venv` built by `uv sync`, `.env`, `career_platform.db` |

The VM's public IP is listed because the user supplied it on 2026-10-03, and visitors need it anyway. The laptop's IP is still left out, because the repo is public.

**Goal:** Visitors open `http://20.221.247.215` (no port) and get the site. It starts on boot, comes back after a crash, and isn't exposed on port 8000. The app runs as `azureuser`, not root.

**Architecture:** There are two pieces. **systemd** is the program that starts and supervises other programs on Ubuntu. It runs the app as a service called `career-platform`: two uvicorn worker processes listening only on `127.0.0.1:8000`, which is reachable from inside the VM only. **nginx** is a web server that listens on public port 80 and passes every request to `127.0.0.1:8000`, which makes it a "reverse proxy". The Azure firewall rule for port 80 lets visitors reach nginx. Nothing lets them reach port 8000 directly.

```
visitor ──80──▶ Azure NSG (rule `Nginx`) ──▶ nginx :80 ──▶ 127.0.0.1:8000 uvicorn (2 workers, user azureuser, run by systemd)
```

**Tech Stack:** Ubuntu systemd, nginx (apt), uvicorn 0.30.6 from the existing `.venv`, Azure portal (port 80 rule only).

**Spec:** The user's request in conversation, 2026-10-03. There is no separate spec file.

## Global Constraints

- Service name: `career-platform`. It runs as `User=azureuser` from `/home/azureuser/career-platform`.
- Reuse what's on the VM: the code, the `.venv`, `.env` and `career_platform.db` in `~/career-platform`. Don't change any repo file, run `uv sync`, or copy the db.
- The app listens on `127.0.0.1:8000` only. No NSG rule for port 8000.
- Port 80 is opened by the existing NSG rule `Nginx` (priority 310, source Any), which the user set in the portal on 2026-10-03. That replaces the planned `Allow-HTTP-80` rule (320). This plan doesn't touch the NSG.
- No new tests. Crash tests and reboot tests are left out on purpose, because the user will run those.
- Nothing runs until the user says to.
- Every task ends with an **Undo** block that says where it runs and how to check it. Undo in reverse order: Task 3, then 2, then 1, then 0. That way nothing is left pointing at a piece that's already gone. If you undo Task 1 while Task 2 is still in place, for example, nginx shows `502 Bad Gateway`.

## Review Focus

1. **The old hand-started uvicorn still holds port 8000.** The service would then fail with "address already in use" and keep retrying. The VM was deallocated, so the old process should be gone. Pinned by the port check in Task 0, Step 3.
2. **Relative paths break under systemd.** `.env`, `career_platform.db`, `static/` and `templates/` are all found relative to the folder the app starts in. Without `WorkingDirectory`, systemd starts the app in `/`. It could then fail, or quietly create an empty new database. Pinned by checking `"source": "database"` and the CSS file in Task 1, Step 4.
3. **nginx's own "Welcome to nginx!" page answers instead of the site.** Ubuntu turns on a default site on install. Pinned by removing it in Task 2 and checking for the site's `<title>` in Task 2, Step 4.
4. **Port 8000 is open to everyone.** That happens if the old `--host 0.0.0.0` habit carries over. Pinned by `--host 127.0.0.1` in the unit file, the `ss` check in Task 1, Step 3, and the external port 8000 check in Task 3, Step 2.
5. **The port 80 rule only lets your laptop in.** If the `Nginx` rule's source ever goes back to a single IP, every test from the laptop passes but visitors are blocked. It's `*` as of 2026-10-03. Pinned by the rule check in Task 3, Step 1 and the phone-on-cellular check in Task 3, Step 2.

---

### Task 0: Get onto the VM (laptop)

**Why:** The VM is stopped, so there's nothing to configure until it's running. You also have to be able to SSH in. The SSH rule allows only one laptop IP, and on 2026-10-03 the laptop's IP didn't match it.

- [x] **Step 1: Start the VM (laptop, Azure CLI).**

> **Done 2026-10-03:** ran only the check, `az vm show -d ... --query powerState`, which printed `VM running`. `az vm start` was **not** run, because the VM was already running. Azure wasn't changed.
 This changes Azure: it powers the VM on, and the VM uses credits while it runs.

```bash
az vm start -g RG-CAREER-PLATFORM -n vm-career-platform
az vm show -d -g RG-CAREER-PLATFORM -n vm-career-platform --query powerState -o tsv
```
Check: prints `VM running`.

> **Finding 2026-10-03:** the VM was already `VM running` when checked (started outside this plan), so this step may be a no-op. A read-only test from the laptop got **connection refused** on `http://20.221.247.215/` (the NSG let it through, but nothing listens on port 80; the old hand-started uvicorn died when the VM was deallocated) and a timeout on port 22 (the laptop's IP still doesn't match `Allow-SSH-Laptop`). Tasks 1 and 2 fix the first problem, and Step 2 below fixes the second. A domain pointed at the VM will only load over plain `http://`. HTTPS (port 443, certificate) is out of scope for this plan.

- [x] **Step 2: Make sure SSH is allowed from here (laptop).**

> **Done 2026-10-03:** the user updated `Allow-SSH-Laptop` in the portal. A re-check showed the source is now the laptop's current IP `/32`, port `22`, `Allow`, provisioning `Succeeded`, and it matches `api.ipify.org`. `ssh ... 'whoami'` printed `azureuser` (exit 0). The old source is in the session transcript, kept out of the repo, and is what Undo Task 0 would restore.

> **Blocked 2026-10-03:** `curl -s https://api.ipify.org` gave the laptop's current IP. `Allow-SSH-Laptop`'s source is a different `/32` (the old one, now recorded outside the repo, in this session's transcript). `ssh ... 'whoami'` with an 8-second timeout gave `connect to host 20.221.247.215 port 22: Operation timed out` (exit 255). The rule has to be updated to the laptop's current IP before Step 3 can run. That's a firewall change, so it's waiting on the user.


```bash
curl -s https://api.ipify.org; echo
az network nsg rule show -g RG-CAREER-PLATFORM --nsg-name vm-career-platform-nsg -n Allow-SSH-Laptop --query sourceAddressPrefix -o tsv
```
Check: the first IP, followed by `/32`, equals the second line. If they differ, write down the second line (the old source) somewhere outside the repo, so you can put it back. Then update `Allow-SSH-Laptop` to your current IP in the portal. Then:

```bash
ssh -i ~/.ssh/isba4775_azure azureuser@20.221.247.215 'whoami'
```
Check: prints `azureuser`.

- [x] **Step 3: Confirm port 8000 is free and the app files are in place (VM).**

> **Done 2026-10-03:** printed `port 8000 free`, and all three files are present: `.venv/bin/uvicorn`, `.env`, `career_platform.db`. No old uvicorn was running, so nothing was stopped, and the "restart old uvicorn" part of Undo Task 0 doesn't apply. **Task 0 complete.** Nothing on the VM was changed.

```bash
sudo ss -ltnp | grep ':8000' || echo "port 8000 free"
ls ~/career-platform/.venv/bin/uvicorn ~/career-platform/.env ~/career-platform/career_platform.db
```
Check: prints `port 8000 free`, and all three files are listed. If something is on 8000, it's an old hand-started uvicorn. Stop it with `pkill -f 'uvicorn app.main:app'` and check again. Note in this plan that you did, because the Undo below starts it again.

**Undo Task 0:**
- **Stop the VM (laptop).** This stops the credit charges. The public IP is static, so it stays the same.
  ```bash
  az vm deallocate -g RG-CAREER-PLATFORM -n vm-career-platform
  az vm show -d -g RG-CAREER-PLATFORM -n vm-career-platform --query powerState -o tsv
  ```
  Check: prints `VM deallocated`.
- **Only if you changed `Allow-SSH-Laptop` in Step 2 (portal, you):** set its source back to the old value you wrote down. Check (laptop): the `az network nsg rule show ... -n Allow-SSH-Laptop` command from Step 2 prints the old value.
- **Only if you stopped an old uvicorn in Step 3 (VM):** start it again by hand, the way the 2026-09-24 migration plan did:
  ```bash
  cd ~/career-platform && setsid -f nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 < /dev/null
  ```
  Check: `curl -s -o /dev/null -w '%{http_code}\n' localhost:8000/` prints `200`.

---

### Task 1: Run the app as a systemd service (VM)

**Why:** systemd is Ubuntu's built-in process manager. A *unit file* tells it what to run, as which user, from which folder, and what to do when it stops:
- `WantedBy=multi-user.target` plus `enable` means it **starts on boot**.
- `Restart=always` means that if the whole app dies, systemd **starts it again** 3 seconds later.
- `--workers 2` means uvicorn runs two app processes behind one supervisor process. If one worker crashes, the other keeps serving, and uvicorn starts a replacement (uvicorn 0.30 has this built in). **One crash doesn't take the site down.**
- `User=azureuser` means the app **isn't root**.
- `--host 127.0.0.1` means only programs on the VM itself (nginx) can reach it, so **port 8000 stays closed** to the Internet.
- `WorkingDirectory` makes the relative paths in `.env` (`career_platform.db`, `data/...`) and the `static`/`templates` folders resolve correctly.

**Files:** Create `/etc/systemd/system/career-platform.service` on the VM. This file is outside the repo.

- [x] **Step 1: Write the unit file (VM).**

> **Done 2026-10-03:** a pre-check confirmed no `career-platform.service` existed. The file was written exactly as below. `systemd-analyze verify` printed nothing (exit 0).

```bash
sudo tee /etc/systemd/system/career-platform.service > /dev/null <<'EOF'
[Unit]
Description=Career Platform website (FastAPI on uvicorn)
After=network.target

[Service]
User=azureuser
Group=azureuser
WorkingDirectory=/home/azureuser/career-platform
ExecStart=/home/azureuser/career-platform/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
```
Check: `systemd-analyze verify /etc/systemd/system/career-platform.service` prints nothing.

- [x] **Step 2: Load it, enable it on boot, and start it now (VM).**

> **Done 2026-10-03:** `enable --now` created the `multi-user.target.wants` symlink. The output was `enabled` and `active`. The journal shows `Uvicorn running on http://127.0.0.1:8000`, `Started parent process [1714]`, and two workers (1717, 1718), each reaching `Application startup complete`. No errors.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now career-platform
systemctl is-enabled career-platform; systemctl is-active career-platform
```
Check: prints `enabled` then `active`. If it says `failed` or `activating`, read `journalctl -u career-platform -n 50 --no-pager`.

- [x] **Step 3: Check the user, the workers and the address (VM).**

> **Done 2026-10-03:** supervisor PID 1714 (`.venv/bin/python .venv/bin/uvicorn ... --host 127.0.0.1 --port 8000 --workers 2`) and workers 1717 and 1718 (`multiprocessing.spawn`), as expected. There's also one extra child, 1716 (`multiprocessing.resource_tracker`). That's Python's own helper process, it serves no requests, and it isn't a problem. `ps` cut the owner name off at `azureus+`, so a second check (`ps -o user:12= --ppid <MainPID> -p <MainPID>`) confirmed all four are owned by `azureuser` and none by `root`. `ss` shows `LISTEN 127.0.0.1:8000`, held by 1714, 1717 and 1718. It isn't listening on `0.0.0.0`. (The `pgrep` line also matched the check's own `bash -c` command, which is a side effect of the check and not part of the service.)

```bash
ps -o user=,pid=,args= -p "$(pgrep -d, -f career-platform/.venv)"
sudo ss -ltnp | grep ':8000'
```
Check: one `.venv/bin/uvicorn ...` line (the supervisor) and two `.venv/bin/python ... multiprocessing.spawn ...` lines (the workers; uvicorn starts them as fresh Python processes). Every line is owned by `azureuser`, none by `root`. The listen address is `127.0.0.1:8000`, not `0.0.0.0:8000`.

- [x] **Step 4: Check that it serves the real data (VM).**

> **Done 2026-10-03:** `/api/profile` → `"source":"database"`, `/static/css/site.css` → `200`, and `/` → `200` (an extra check). **Task 1 complete.** The app runs as the `career-platform` service, but it isn't reachable from outside yet, because nothing on port 80 forwards to it. That's Task 2.

```bash
curl -s localhost:8000/api/profile | grep -o '"source":"[a-z]*"'
curl -s -o /dev/null -w '%{http_code}\n' localhost:8000/static/css/site.css
```
Check: `"source":"database"` and `200`. A `"source":"fallback"` result means the database wasn't found, so check `WorkingDirectory`.

**Undo Task 1 (VM):** stop the service, take it off the boot list, delete the unit file, and tell systemd the file is gone. The repo, the `.venv`, `.env` and the database aren't touched.
```bash
sudo systemctl disable --now career-platform
sudo rm /etc/systemd/system/career-platform.service
sudo systemctl daemon-reload
systemctl status career-platform --no-pager; sudo ss -ltnp | grep ':8000' || echo "port 8000 free"
```
Check: `Unit career-platform.service could not be found.` and `port 8000 free`. After this, the site only runs if someone starts it by hand, the way it did before this plan.

---

### Task 2: Put nginx in front on port 80 (VM)

**Why:** Port 80 is the port browsers use when you type `http://` with no port number. Programs need root to open ports below 1024. Instead of running the app as root, nginx opens port 80 (its master process is root, and its workers run as the unprivileged user `www-data`) and forwards each request to the app on `127.0.0.1:8000`. The `proxy_set_header` lines pass along the visitor's real address and the hostname they typed.

**Files:** Create `/etc/nginx/sites-available/career-platform`, link it into `sites-enabled`, and remove the `default` link. All of these are on the VM, outside the repo.

- [x] **Step 1: Install nginx (VM).** If it's already installed, this does nothing.

> **Done 2026-10-03:** `dpkg -s nginx` beforehand found nothing, so **nginx was installed fresh by this plan**. Undo Task 2 therefore includes the `apt-get remove` part. The install exited 0, and `nginx -v` printed `nginx/1.24.0 (Ubuntu)`. `sites-enabled/` held only `default`. On install, nginx immediately started on `0.0.0.0:80` and `[::]:80`, showing its welcome page, until Step 3 replaced it a few seconds later.

```bash
sudo DEBIAN_FRONTEND=noninteractive apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nginx
nginx -v
ls -l /etc/nginx/sites-enabled/
```
Check: `nginx -v` prints a version. Write down whether apt said `nginx is already the newest version` (it was already installed) or installed it fresh. The Undo depends on which. The listing should show only `default`. If something else is there, stop and ask before going on.

- [x] **Step 2: Write the site config (VM).**

> **Done 2026-10-03:** a pre-check confirmed the file didn't exist. It was written exactly as below, and a read-back showed the `listen 80`, `listen [::]:80`, `proxy_pass http://127.0.0.1:8000` and `Host $host` lines.

```bash
sudo tee /etc/nginx/sites-available/career-platform > /dev/null <<'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
```

- [x] **Step 3: Turn on this site, turn off the default one, and reload (VM).**

> **Done 2026-10-03:** `sites-enabled/` now holds only `career-platform -> /etc/nginx/sites-available/career-platform`. `nginx -t` gave `syntax is ok` and `test is successful`, the reload succeeded, and the service shows `enabled` and `active`. `sites-available/` still holds both `career-platform` and `default`, so the undo works.

```bash
sudo ln -sf /etc/nginx/sites-available/career-platform /etc/nginx/sites-enabled/career-platform
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
systemctl is-enabled nginx; systemctl is-active nginx
```
Check: `nginx -t` says `syntax is ok` and `test is successful`, followed by `enabled` and `active`. nginx comes with its own systemd service, so it also starts on boot and restarts itself.

Only the link in `sites-enabled` is removed. `/etc/nginx/sites-available/default` stays, so the change can be undone.

- [x] **Step 4: Check the site through nginx (VM).**

> **Done 2026-10-03:** the output was `HTTP/1.1 200 OK`, `Server: nginx/1.24.0 (Ubuntu)` and `<title>Home</title>`. The home page's title is `Home`, not `Career Platform`, which the plan's "or your page's title" allows for. "Welcome to nginx" appeared 0 times. Extra checks through port 80: `/api/profile` → `"source":"database"`, and `/static/css/site.css` → `200`. **Task 2 complete.** Next is the user's `curl -I http://localhost` pause, which isn't run here. It will show `405 Method Not Allowed`, because FastAPI doesn't answer header-only (HEAD) requests. That still proves nginx passed the request to uvicorn.

```bash
curl -s -i localhost/ | grep -E '^HTTP|^Server|<title>'
```
Check: `HTTP/1.1 200 OK`, `Server: nginx/...`, and `<title>Career Platform</title>`, or your page's title. It must not say "Welcome to nginx!".

**Undo Task 2 (VM):** turn off our site, turn the default site back on, and delete our config.
```bash
sudo rm /etc/nginx/sites-enabled/career-platform
sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
sudo rm /etc/nginx/sites-available/career-platform
sudo nginx -t && sudo systemctl reload nginx
curl -s localhost/ | grep -o '<title>[^<]*</title>'
```
Check: `<title>Welcome to nginx!</title>`. Port 80 now shows nginx's own page instead of the site.

**Only if Step 1 installed nginx fresh:** remove it too. Don't remove it if it was already there, because this plan didn't install it.
```bash
sudo DEBIAN_FRONTEND=noninteractive apt-get remove -y nginx
systemctl is-active nginx; sudo ss -ltnp | grep ':80 ' || echo "port 80 free"
```
Check: `inactive` (or `unknown`) and `port 80 free`. `apt-get remove` keeps nginx's config files in `/etc/nginx`. Use `apt-get purge` instead only if you want those gone too.

---

### Task 3: Open port 80 and check from outside (portal, then laptop and phone)

**Why:** Azure's firewall (the NSG) blocks inbound traffic unless a rule allows it. Until a port 80 rule allows everyone, nginx is running but strangers can't reach it.

- [x] **Step 1: Open port 80 to everyone (Azure portal, you).**

> **Done 2026-10-03 (by the user):** instead of adding `Allow-HTTP-80` (320), the user changed the existing `Nginx` rule (310, port 80) to source **Any**. A read-only `az` check confirmed `Nginx | 310 | 80 | * | Allow`. Don't add a rule for 8000.

Check (laptop): `az network nsg rule show -g RG-CAREER-PLATFORM --nsg-name vm-career-platform-nsg -n Nginx --query "{p:priority,port:destinationPortRange,src:sourceAddressPrefix,access:access}" -o table` shows `310 | 80 | * | Allow`. Re-run this right before Step 2 in case the rule was changed.

> **Re-checked 2026-10-03, before Step 2:** `310 | 80 | * | Allow`, unchanged. No NSG rule names port `8000` or `*`.


- [x] **Step 2: Check from the Internet (laptop, then phone).**

> **Laptop part done 2026-10-03:** `/` → `200`, `/projects` → `200`, and `:8000` → `000` / `8000 closed` (curl exit 28, a 5-second timeout), all as expected. Extra checks from the laptop: the page title is `<title>Home</title>` and `/api/profile` → `"source":"database"`. **Phone done 2026-10-03 (user):** the site loads over both Wi-Fi and cellular data using an explicit `http://` address. **Task 3 complete.** Found along the way: `tristaninfo.me` and `www.tristaninfo.me` (Cloudflare DNS, "DNS only") both point to `20.221.247.215` and return `200` over `http://`. `https://` times out, because there's no port 443 rule and no certificate. HTTPS is out of scope here and deferred by the user.

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://20.221.247.215/
curl -s -o /dev/null -w '%{http_code}\n' http://20.221.247.215/projects
curl -s --max-time 5 -o /dev/null -w '%{http_code}\n' http://20.221.247.215:8000/ || echo "8000 closed"
```
Check: `200`, `200`, then `000` / `8000 closed`. Port 8000 is blocked twice: the NSG has no rule for it, and the app only listens on 127.0.0.1.

Then turn off Wi-Fi on your phone and open `http://20.221.247.215` over cellular. Check: the site loads. This proves the rule works for visitors, not just for your laptop.

**Undo Task 3 (portal, you):** Step 2 only reads, so there's nothing to undo there. Step 1 was your portal change. To close the site to the public again, go to `vm-career-platform-nsg` → Inbound security rules → `Nginx`, and set its source back to your laptop's IP (`My IP address` in the portal fills it in). Alternatively, delete the rule to close port 80 completely.

Check (laptop): the Step 1 `az network nsg rule show ... -n Nginx` command shows a `/32` source instead of `*`, or `ResourceNotFound` if you deleted it. Then open `http://20.221.247.215` on the phone over cellular. It should time out.

---

### Done when

- [x] `http://20.221.247.215` loads from the phone over cellular. (User, 2026-10-03.)
- [x] `career-platform` and `nginx` both report `enabled` and `active`. (Task 1 Step 2 and Task 2 Step 3, 2026-10-03.)
- [x] The uvicorn processes are owned by `azureuser`, listen on `127.0.0.1:8000`, and port 8000 is unreachable from outside. (Task 1 Step 3, and the laptop part of Task 3 Step 2, 2026-10-03.)

Left for you: the crash test (`sudo kill -9` one worker, then the supervisor) and the reboot test (`sudo reboot`, then reload the site). When you're done for the day, run `az vm deallocate -g RG-CAREER-PLATFORM -n vm-career-platform` to stop paying for the VM. Both services come back by themselves at the next start.
