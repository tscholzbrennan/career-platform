# Azure VM Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the career-platform FastAPI/SQLite app from the laptop to the already-provisioned Azure VM (`vm-career-platform`, resource group `rg-career-platform`), running and reachable with the user's real data.

**Architecture:** Clone the existing GitHub repo onto the VM, install Python dependencies with `uv`, restore config (`.env`) and data (`career_platform.db`) that git intentionally doesn't carry (or, for the db, carries a stale copy of), then run `uvicorn` bound to all interfaces and confirm the site answers both locally on the VM and from the laptop over the public IP.

**Tech Stack:** Azure VM (Ubuntu, apt), OpenSSH/scp, git, `uv` (Python package/venv manager), FastAPI + uvicorn, SQLite.

**Status (2026-09-29):** all 8 sections were executed and all 19 steps (including the added 1b) are ticked. The site is live at `http://<VM_PUBLIC_IP>:8000`, reachable only from `<LAPTOP_PUBLIC_IP>`, and serves from the database (`source: database`). Still open: the database content is mostly seed placeholders (see Step 14); the server runs under `nohup`, not a service, so it won't restart if the VM reboots (see Step 16); and the VM costs credits while it runs (see Step 1b to deallocate). All five Review Focus risks actually came up and were checked. #2 turned out not to apply, because the cloned db was already current.

**Spec:** User-supplied migration plan (conversation, 2026-09-24) — categories: Server, Packages, Code, Python, Config, Data, Processes, Verify. No separate spec file exists; this plan is the spec's only written form. Repo state inspected at commit `f3d9803` on `main`.

## Global Constraints

- The VM (`vm-career-platform` / `rg-career-platform`) already exists — this plan never creates, resizes, or deletes Azure compute resources.
- All VM access uses `ssh -i ~/.ssh/isba4775_azure azureuser@<VM_PUBLIC_IP>` — no other user or key.
- IP addresses are left out of this public document on purpose. `<VM_PUBLIC_IP>` is the VM's static public IP (resource `vm-career-platform-ip`); look it up with `az vm show -d -g rg-career-platform -n vm-career-platform --query publicIps -o tsv`.
- `<LAPTOP_PUBLIC_IP>` is the laptop's current public IP; look it up with `curl -s https://api.ipify.org`. NSG `vm-career-platform-nsg` rule `Allow-SSH-Laptop` (priority 300) allows port 22 only from that address. If the laptop's IP changes, SSH will time out until that rule is updated.
- The VM may be deallocated between sessions (it was on 2026-09-29) — Step 1b starts it.
- `.env` and `career_platform.db` must never be `git add`ed — `.env` is already gitignored; `career_platform.db` currently is *not* gitignored (see Review Focus #2) but this plan does not change that, only works around it.
- Nothing in this document is to be executed until the user explicitly says to run it — this is a write-up, not an action.

## Review Focus

- uvicorn defaults to binding `127.0.0.1`, which would make the VM's app unreachable from outside even with the firewall open and the process "running fine" per its own logs — pinned by requiring `--host 0.0.0.0` explicitly (Processes step) and a two-stage local-then-external check (Verify steps).
- `career_platform.db` is already committed to git (`git ls-files` confirms it), so `git clone` on the VM produces a stale/seed copy *before* the scp step overwrites it — pinned by calling this out explicitly in Code/Data and checksumming after the copy.
- An SSH private key with loose permissions (e.g. `644`, common after copying a key file) is silently rejected by OpenSSH with a permissions error that doesn't mention the real cause — pinned by an explicit `chmod 600` + connectivity test before anything else.
- Azure NSGs deny inbound traffic by default except rules you add; SSH working does not imply port 8000 works — pinned by an explicit NSG rule step and an external curl/browser check in Verify, not just a local one.
- A foreground `uvicorn` process dies (SIGHUP) the moment the SSH session that launched it closes, so "it worked when I checked" silently stops being true later — pinned by running it detached (`nohup ... & disown`) instead of foreground-only.

---

### Server

- [x] **Step 1: Fix SSH key permissions (laptop)**

> **Done 2026-09-29:** `ls -l` shows `-rw-------`.

Where it runs: laptop.

What to run:
```bash
chmod 600 ~/.ssh/isba4775_azure
```

Why: OpenSSH refuses to use a private key that's group/world-readable, and fails with a permissions error rather than a clear one.

How we check it worked:
```bash
ls -l ~/.ssh/isba4775_azure
```
Expect `-rw-------` (600) as the mode.

How we undo it: N/A — tightening permissions has no downside to reverse.

- [x] **Step 1b: Make sure the VM is running (laptop)**

> **Done 2026-09-29:** added mid-run, after the first SSH attempt timed out. The VM was `VM deallocated`; `az vm start` changed it to `VM running`. The VM now uses Azure credits until it's deallocated again.

Where it runs: laptop (Azure CLI), or portal → `vm-career-platform` → **Start**.

What to run:
```bash
az vm show -d -g rg-career-platform -n vm-career-platform --query powerState -o tsv
az vm start -g rg-career-platform -n vm-career-platform   # only if not "VM running"
```

Why: a deallocated VM doesn't answer on any port, so SSH times out, the same symptom as a firewall block. It also isn't billed for compute while deallocated, which is why it may be stopped between sessions.

How we check it worked: the `az vm show` query prints `VM running`.

How we undo it: `az vm deallocate -g rg-career-platform -n vm-career-platform` (stops compute billing; the static public IP and disk are kept).

- [x] **Step 2: Test SSH connectivity to the VM (laptop)**

> **Done 2026-09-29:** the first attempt timed out for two reasons: the plan had the laptop's IP (<LAPTOP_PUBLIC_IP>) instead of the VM's (<VM_PUBLIC_IP>), and the VM was deallocated. After both were fixed, SSH printed `connected`, `azureuser`, and `Ubuntu 24.04.4 LTS (noble)`. The first run used `-o StrictHostKeyChecking=accept-new`, which saved the VM's host key to `~/.ssh/known_hosts`.

Where it runs: laptop.

What to run:
```bash
ssh -i ~/.ssh/isba4775_azure azureuser@<VM_PUBLIC_IP> "echo connected && whoami && lsb_release -a"
```

Why: confirms the VM is up, the key/user pair is accepted, and shows the exact OS/version before any package step assumes an Ubuntu apt layout.

How we check it worked: output includes `connected`, `azureuser`, and a `lsb_release` block (e.g. `Ubuntu 22.04` or `24.04`).

How we undo it: N/A — read-only.

- [x] **Step 3: Open inbound port 8000 for the app (laptop, Azure CLI)**

> **Done 2026-09-29:** created from the Azure CLI instead of the portal, and limited to the laptop's IP (`<LAPTOP_PUBLIC_IP>/32`) instead of `Any`. Provisioning state was `Succeeded`. The NSG now has `Allow-SSH-Laptop` (300, port 22) and `Allow-Uvicorn-8000` (320, port 8000), both allowing only that source. If other people need to reach the site later, widen this rule's source.

Where it runs: laptop (Azure CLI). The portal equivalent: `vm-career-platform` → **Networking** → **Inbound port rules** → **Add**, with the same values.

What to run:
```bash
az network nsg rule create -g rg-career-platform --nsg-name vm-career-platform-nsg \
  -n Allow-Uvicorn-8000 --priority 320 --direction Inbound --access Allow --protocol Tcp \
  --source-address-prefixes <LAPTOP_PUBLIC_IP>/32 --destination-port-ranges 8000
```

Why: `uvicorn` will listen on `0.0.0.0:8000`, but Azure blocks all inbound traffic by default except rules that exist explicitly. Port 22 already works because a rule for it exists (you can SSH in); port 8000 needs its own rule or the Verify step will time out even though the app is running correctly.

How we check it worked:
```bash
az network nsg rule list -g rg-career-platform --nsg-name vm-career-platform-nsg -o table
```
`Allow-Uvicorn-8000` is listed with Access `Allow`, port `8000`, source `<LAPTOP_PUBLIC_IP>/32`.

How we undo it: `az network nsg rule delete -g rg-career-platform --nsg-name vm-career-platform-nsg -n Allow-Uvicorn-8000`

### Packages

- [x] **Step 4: Refresh the apt package index (VM)**

> **Done 2026-09-29:** exited 0 and fetched 37.3 MB from `azure.archive.ubuntu.com`; the last line was `Reading package lists...`.

Where it runs: VM (via SSH).

What to run:
```bash
sudo apt-get update
```

Why: ensures `apt-get install` in the next step pulls current package metadata instead of a stale cache, avoiding a "package not found" failure on a fresh VM image.

How we check it worked: command exits with status 0; last lines look like `Reading package lists... Done`.

How we undo it: N/A — refreshing metadata has no lasting state to revert.

- [x] **Step 5: Install git and sqlite3 (VM)**

> **Done 2026-09-29:** exited 0. git was **already installed** on the Ubuntu 24.04 image (`git is already the newest version (1:2.43.0-1ubuntu7.3)`), so only `sqlite3` 3.45.1 was new, and `libsqlite3-0` was upgraded alongside it. Checks: `git version 2.43.0`, `sqlite3 3.45.1`. Ran with `DEBIAN_FRONTEND=noninteractive` so no prompt could stall a non-interactive SSH session. The undo below now removes only sqlite3.

Where it runs: VM.

What to run:
```bash
sudo apt-get install -y git sqlite3
```

Why: `git` is needed to clone the repo (Code section); the `sqlite3` CLI is needed to independently inspect the `.db` file once it's copied over (Verify section), separate from whatever the app itself reports.

How we check it worked:
```bash
git --version && sqlite3 --version
```
Both print version numbers with no "command not found" error.

How we undo it: `sudo apt-get remove -y sqlite3`. Don't remove git: it came with the image and wasn't installed by this step. Leaving sqlite3 installed is harmless.

### Code

- [x] **Step 6: Clone the repo onto the VM (VM)**

> **Done 2026-09-29:** exited 0, and `~/career-platform` did not exist beforehand. The VM is at `f3d9803 Merge feature/career-platform-implementation`, the same commit as the laptop, and `ls` shows `README.md app career_platform.db data docs requirements.txt static templates tests`. The public repo cloned over HTTPS without credentials (`GIT_TERMINAL_PROMPT=0`, so it would have failed rather than hung if it had needed them).
>
> **Finding:** the cloned `career_platform.db` (65536 bytes) is **byte-identical** to the laptop's copy. Both SHA-256 hashes are `b37b70f5…c49543fad9`, and `git status` on the laptop shows no local changes to it. Contrary to the Note below and Review Focus #2, the clone already carries the current data. Step 14 (scp) is kept because it's in the original plan and is a harmless explicit copy, but today it would copy an identical file.

Where it runs: VM.

What to run:
```bash
git clone https://github.com/tscholzbrennan/career-platform.git ~/career-platform
```

Why: pulls the application code (FastAPI app, templates, `requirements.txt`, etc.) onto the VM. Note: this also pulls `career_platform.db`, because it's currently tracked in git (see Review Focus) — that copy is stale/seed data and gets overwritten in the Data section below, so don't treat its presence here as "data migration done."

How we check it worked:
```bash
ls ~/career-platform
```
Shows `app/`, `requirements.txt`, `README.md`, `templates/`, `static/`, `career_platform.db`, etc.

How we undo it: `rm -rf ~/career-platform`.

### Python

- [x] **Step 7: Install uv (laptop)**

> **Done 2026-09-29:** installed `uv 0.12.21` at `~/.local/bin/uv` (plus `uvx`). The installer also **edited shell startup files**: it added `. "$HOME/.local/bin/env"` at `~/.zshrc` line 5 and `~/.profile` line 2. The undo below covers those lines too.

Where it runs: laptop.

What to run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

Why: the repo has no `pyproject.toml`/`uv.lock` yet — only `requirements.txt` — so `uv sync` (the migration plan's stated Python step) has nothing to sync from. This step and the next two build that lock file on the laptop first, since it needs to exist in the repo before the VM can `uv sync` from it.

How we check it worked:
```bash
uv --version
```
Prints a version string.

How we undo it: `rm ~/.local/bin/uv ~/.local/bin/uvx ~/.local/bin/env ~/.local/bin/env.fish`, then delete the `. "$HOME/.local/bin/env"` line from `~/.zshrc` and `~/.profile`. Optionally run `rm -rf ~/.local/share/uv ~/.cache/uv`, which removes uv-managed Pythons such as 3.12.14 from Step 8, plus uv's download cache.

- [x] **Step 8: Create the uv project files from requirements.txt (laptop)**

> **Done 2026-09-29, with a Python pin added.** The laptop's default Python is 3.14.7 (Homebrew), but the VM has 3.12.3. `pydantic==2.9.2` requires `pydantic-core==2.23.4`, which I believe has no prebuilt package for 3.14, so building on 3.14 would mean compiling it from source and would likely fail. The commands below therefore add `--python 3.12` and `uv python pin 3.12`. The pin downloaded a uv-managed CPython 3.12.14 to the laptop and created a **`.python-version`** file (`3.12`), which Step 9 must commit too. Results: `pyproject.toml` has `requires-python = ">=3.12"` and the 9 pinned deps; `uv.lock` was written; the import check printed `ok 3.12.14`.
>
> **Extra check (not in the original plan):** `uv run python -m pytest -q` → `10 passed`. Plain `uv run pytest` fails at collection with `ModuleNotFoundError: No module named 'app'`. That's already true of the repo, not something uv caused: plain `pytest` doesn't add the repo root to `sys.path`, but `python -m pytest` does. Run the tests with `python -m pytest`.

Where it runs: laptop.

What to run:
```bash
cd career-platform   # the repo root on the laptop
uv init --bare --vcs none --no-readme --name career-platform --python 3.12
uv python pin 3.12
uv add -r requirements.txt
```

Why: `uv init --bare --vcs none --no-readme` creates just a `pyproject.toml` (no extra README/`.git`/`hello.py`, since this is already a git repo with its own README). `uv add -r requirements.txt` then reads the existing pinned versions, adds them as `uv`-managed dependencies, resolves the dependency graph, and writes `uv.lock` — the file the VM's `uv sync` will consume.

How we check it worked:
```bash
cat pyproject.toml
uv run python -c "import fastapi, uvicorn, sqlalchemy, jinja2, dotenv, pydantic, pydantic_settings, pytest, httpx; print('ok')"
```
`pyproject.toml` shows a `[project]` table named `career-platform`; the Python check prints `ok` with no `ImportError`.

How we undo it: `rm pyproject.toml uv.lock .python-version` and `rm -rf .venv`.

- [x] **Step 9: Commit and push the new project files (laptop)**

> **Done 2026-09-29:** the user OK'd the push to `main` and asked to include this plan. It went as two commits pushed together: this plan (`docs:`), then `pyproject.toml` + `uv.lock` + `.python-version` (`chore:`). Local `main` matched `origin/main` before the push. `.DS_Store` was left out. Commits: `27fae04` (plan) and `46d9925` (uv files); the push was `f3d9803..46d9925 main -> main`.

Where it runs: laptop.

What to run:
```bash
git add pyproject.toml uv.lock .python-version
git commit -m "chore: add uv project files for VM deployment"
git push origin main
```

Why: the VM already cloned the repo in the Code section, before these files existed — pushing now is what makes them available to `git pull` on the VM next.

How we check it worked:
```bash
git log -1 --oneline
```
Shows the new commit; the GitHub repo page lists `pyproject.toml` and `uv.lock`.

How we undo it: since this is already pushed to the shared remote, use `git revert <commit-sha>` followed by `git push origin main` rather than rewriting history.

- [x] **Step 10: Pull the new files onto the VM (VM)**

> **Done 2026-09-29:** a fast-forward pull (4 files, 914 insertions) moved the VM to `46d9925`. `pyproject.toml`, `uv.lock`, and `.python-version` are present; this plan also arrived at `docs/superpowers/plans/`. The undo's `<previous-commit-sha>` is `f3d9803`.

Where it runs: VM.

What to run:
```bash
cd ~/career-platform && git pull origin main
```

Why: brings the just-pushed `pyproject.toml` and `uv.lock` onto the VM so `uv sync` has something to read.

How we check it worked:
```bash
ls pyproject.toml uv.lock
```
Both files exist.

How we undo it: `git checkout <previous-commit-sha> -- pyproject.toml uv.lock` (or delete both files) — check `git log` on the VM for `<previous-commit-sha>`.

- [x] **Step 11: Install uv on the VM (VM)**

> **Done 2026-09-29:** installed `uv 0.12.21 (x86_64-unknown-linux-gnu)` at `/home/azureuser/.local/bin/uv`. As on the laptop, the installer added `. "$HOME/.local/bin/env"` to `~/.bashrc` line 119 and `~/.profile` line 29, and the undo below covers those lines. SSH commands that aren't interactive login shells need `source $HOME/.local/bin/env` first to find `uv`; Steps 12, 15 and 16 do that.

Where it runs: VM.

What to run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

Why: `uv` isn't in Ubuntu's apt repositories; the official installer script is the supported install path (same as Step 7 on the laptop).

How we check it worked:
```bash
uv --version
```
Prints a version string.

How we undo it: `rm ~/.local/bin/uv ~/.local/bin/uvx ~/.local/bin/env ~/.local/bin/env.fish`, then delete the `. "$HOME/.local/bin/env"` line from `~/.bashrc` and `~/.profile`.

- [x] **Step 12: Install the exact locked dependencies (VM)**

> **Done 2026-09-29:** `uv sync --frozen` exited 0. It used the VM's system `CPython 3.12.3` at `/usr/bin/python3.12`, so no Python download was needed, and created `~/career-platform/.venv`. The check printed `0.115.0 3.12.3 /home/azureuser/career-platform/.venv/bin/python`. **Extra check:** `uv run python -m pytest -q` → `10 passed` on the VM. Afterwards `career_platform.db` still had SHA-256 `b37b70f5…c49543fad9` and `git status` was clean, so the tests don't modify the database.

Where it runs: VM.

What to run:
```bash
cd ~/career-platform && uv sync --frozen
```

Why: `--frozen` installs exactly the versions recorded in `uv.lock` without re-resolving, so the VM runs the identical dependency set that was verified on the laptop in Step 8. This also creates a `.venv` on the VM.

How we check it worked:
```bash
uv run python -c "import fastapi; print(fastapi.__version__)"
```
Prints `0.115.0`.

How we undo it: `rm -rf .venv`.

### Config

- [x] **Step 13: Create .env from .env.example (VM)**

> **Done 2026-09-29:** a pre-check confirmed no `.env` existed. I ran `cp -n` (no-clobber) instead of plain `cp` so an existing file could never be overwritten; on this `cp`, `-n` prints a harmless portability warning. Results: `diff .env.example .env` shows identical files; `git check-ignore` confirms `.env` is ignored (`.gitignore:151`); `app.config.settings` loads `Career Platform | career_platform.db | data/fallback-profile.json`. **Caveat:** these values are the same as the defaults in `app/config.py`, so this check can't tell whether the app read `.env` or used its defaults. The result is identical either way. It will only matter if `.env` is changed to non-default values later.

Where it runs: VM.

What to run:
```bash
cd ~/career-platform && cp .env.example .env
```

Why: `app/config.py` reads `APP_NAME`, `SQLITE_DB_PATH`, and `FALLBACK_PROFILE_PATH` from a `.env` file; `.env` is gitignored (correctly, since it can hold secrets in general), so it never arrives via `git clone` and must be recreated on the VM.

How we check it worked:
```bash
cat .env
```
Shows the three keys with the same values as `.env.example` (`APP_NAME`, `SQLITE_DB_PATH="career_platform.db"`, `FALLBACK_PROFILE_PATH="data/fallback-profile.json"`).

How we undo it: `rm .env`.

### Data

- [x] **Step 14: Copy the SQLite database to the VM (laptop)**

> **Done 2026-09-29:** re-checked the hashes first. The laptop and VM copies were already identical (`b37b70f5…c49543fad9`). Ran the scp anyway, as planned, and it exited 0. The VM hash afterwards was the same, the file size was 65536 bytes, and `git status` on the VM was clean. **Extra checks:** `PRAGMA integrity_check` → `ok`. Tables and row counts: `profiles` 1, `experiences` 1, `projects` 2, `education` / `skills` / `media` / `fallback_profile_snapshots` 0.
>
> **Finding, content:** the database holds **mostly the seed placeholders from `app/seed.py`**. Projects are `Demand Forecasting Dashboard` and `AI Research Briefing Tool`; the experience is `Data Analyst` at `Example Company`; the email is `hello@example.com`. The only non-seed value is the profile headline, `Updated headline`. The migration copied this exactly. Whether this is the content the user wants live is the user's decision. Steps 17–19 below were rewritten to check for these actual values, instead of treating the seed titles as a sign the copy failed.
>
> **Finding, plan defect:** the table is `profiles`, not `profile`. Step 19's query has been fixed.

> **Heads-up (found in Step 6, 2026-09-29):** the VM's cloned db already matches the laptop's (SHA-256 `b37b70f5…c49543fad9`). This copy only matters if the laptop db changes before this step runs. Re-check with `shasum -a 256 career_platform.db` on the laptop before copying.

Where it runs: laptop.

What to run:
```bash
scp -i ~/.ssh/isba4775_azure ./career_platform.db azureuser@<VM_PUBLIC_IP>:~/career-platform/career_platform.db
```

Why: overwrites the stale/seed copy of `career_platform.db` that came through `git clone` (Step 6) with the real, current data from the laptop. `SQLITE_DB_PATH="career_platform.db"` in `.env` is a relative path, so it must land at exactly `~/career-platform/career_platform.db` for the app to pick it up.

How we check it worked:
```bash
# laptop
shasum -a 256 career_platform.db
# VM
sha256sum ~/career-platform/career_platform.db
```
The two hashes match.

How we undo it: on the VM, `cd ~/career-platform && git checkout -- career_platform.db` restores the git-tracked version. As of 2026-09-29 that version is identical, so this undo changes nothing.

### Processes

- [x] **Step 15: Start uvicorn bound to all interfaces (VM)**

> **Done 2026-09-29:** a pre-check showed port 8000 free and no uvicorn running. Over non-interactive SSH there's no terminal to `Ctrl+C`, so I ran it as `timeout 10 uv run uvicorn ...`. The output was `Started server process` → `Application startup complete.` → `Uvicorn running on http://0.0.0.0:8000`, with no traceback, then a clean shutdown when the timeout fired (exit 124, as expected).

Where it runs: VM.

What to run:
```bash
cd ~/career-platform && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Why: `--host 0.0.0.0` is required — uvicorn's default of `127.0.0.1` only accepts connections from inside the VM itself, which would make the NSG rule from Step 3 pointless. `uv run` executes inside the `.venv` that `uv sync` built, not any system Python.

How we check it worked: terminal output shows `Uvicorn running on http://0.0.0.0:8000` with no traceback. Leave this running for now — the next step makes it survive disconnecting.

How we undo it: `Ctrl+C` in the foreground terminal.

- [x] **Step 16: Re-run it detached so it survives closing the SSH session (VM)**

> **Done 2026-09-29:** launched with the command below plus `< /dev/null`. uvicorn came up at PID 2878 (its `uv run` parent is 2875), listening on `0.0.0.0:8000`, and `curl localhost:8000/api/profile` → `HTTP 200`. **Survival test:** the launching SSH session was forcibly closed. A fresh session afterwards still found uvicorn running and still got `HTTP 200`. The db hash was unchanged (`b37b70f5…c49543fad9`), and `git status` was clean because `uvicorn.log` is gitignored.
>
> **Quirk:** the launching `ssh` command never returned by itself. Its `bash -c` wrapper (PID 2873) stays alive, reparented to PID 1, as the parent of `uv run`, and the local ssh client waited on it until it was stopped manually. For future non-interactive launches, use `ssh -n ... 'setsid -f nohup uv run uvicorn ... > uvicorn.log 2>&1 < /dev/null'` so the server is fully detached and ssh returns straight away. The current server was left running rather than restarted, since it works.

Where it runs: VM.

What to run (stop the foreground one from Step 15 with `Ctrl+C` first, then):
```bash
cd ~/career-platform
nohup uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
disown
```

Why: a foreground process launched over SSH receives `SIGHUP` and dies the moment that SSH session closes. Without this, the Verify section below would only pass while the SSH terminal from Step 15 stays open.

How we check it worked:
```bash
ps aux | grep uvicorn
curl -s http://localhost:8000/api/profile
```
`ps` shows a running `uvicorn` process; `curl` returns JSON, not "connection refused".

How we undo it: `pkill -f "uvicorn app.main:app"`. This also kills the leftover `bash -c` wrapper, because its command line contains the same text. Confirm with `ss -ltn | grep :8000`, which should print nothing.

### Verify

- [x] **Step 17: Confirm the app answers locally on the VM (VM)**

> **Done 2026-09-29:** `HTTP 200` with `"headline":"Updated headline"`, `"summary":"Updated summary"`, `"email":"hello@example.com"`, and the two expected `featured_projects`. The response also reports **`"source":"database"`** and **`"degraded_mode":false`**, which confirms directly that the app is serving from SQLite and not the fallback JSON.

Where it runs: VM.

What to run:
```bash
curl -s http://localhost:8000/api/profile
```

Why: isolates "is the app itself broken" from "is the network/NSG broken" by checking the shortest possible path first.

How we check it worked: a JSON response with profile fields (`headline`, `summary`, `email`, etc.; see `app/models.py`). Per Step 14, expect `"headline": "Updated headline"` and `"email": "hello@example.com"`. If `headline` is instead the original seed text ("Data & AI Engineer building practical analytics products"), the app isn't reading the copied `career_platform.db`, for example because it started in a different directory. Two other outcomes also mean it isn't reading the database: an empty database that got freshly seeded, or the fallback JSON from `data/fallback-profile.json`.

How we undo it: N/A — read-only.

- [x] **Step 18: Confirm external reachability and real data (laptop)**

> **Done 2026-09-29:** run from the laptop, whose public IP was confirmed as `<LAPTOP_PUBLIC_IP>`. `http://<VM_PUBLIC_IP>:8000/api/profile` → `HTTP 200` with the same values as Step 17 (`source: database`, `degraded_mode: False`). **Extra checks:** every route in `app/main.py` returned 200: `/` (2382 B), `/about`, `/experience`, `/projects`, `/projects/demand-forecasting-dashboard`, `/resume`, `/contact`. The homepage contains `Updated headline` and both project titles. Its stylesheet `/static/css/site.css` → `200 text/css`, 3341 B. `/static/` on its own → 404, which is expected. **Not tested:** that other IPs are blocked. Only one network was available, so Step 3's restriction was verified by reading the firewall rules, not by trying to connect from a different address.

Where it runs: laptop.

What to run:
```bash
curl -s http://<VM_PUBLIC_IP>:8000/api/profile
```
Or open `http://<VM_PUBLIC_IP>:8000` in a browser.

Why: this is the end-to-end check — it only passes if the NSG rule (Step 3), the `--host 0.0.0.0` bind (Step 15), and the VM's own OS firewall (if any) all line up simultaneously. A pass here is what "the site answers on the VM" actually means, as opposed to Step 17's VM-local check.

How we check it worked: the homepage renders, or `curl` returns the same JSON as Step 17 (`"headline": "Updated headline"`). The projects page lists `Demand Forecasting Dashboard` and `AI Research Briefing Tool`. Per Step 14 these are the database's actual contents, so seeing them here is expected, not a failure. Only works from the laptop's IP `<LAPTOP_PUBLIC_IP>`, because of Step 3's source restriction.

How we undo it: N/A — read-only. If you want to close external access again afterward, use the NSG rule's undo from Step 3.

- [x] **Step 19: Confirm the on-disk data independently of the app (VM)**

> **Done 2026-09-29:** with the corrected table name, `select headline, email from profiles;` → `Updated headline|hello@example.com`. Extra: `summary` → `Updated summary`; `projects` → `Demand Forecasting Dashboard` and `AI Research Briefing Tool`. These match the app's JSON from Steps 17–18 exactly, so what the site shows is what's in the file.

Where it runs: VM.

What to run:
```bash
sqlite3 ~/career-platform/career_platform.db "select headline, email from profiles;"
```

Why: this is what `sqlite3` was installed for in Step 5 — it reads the actual database rows directly, bypassing the app layer entirely. The README notes the app serves a cached fallback JSON snapshot (`data/fallback-profile.json`) when the database is unavailable, so a passing browser check alone doesn't fully rule out "you're looking at the fallback, not the real database."

How we check it worked: output is `Updated headline|hello@example.com`, matching Step 14's reading and Step 17's JSON. If the file's rows and the app's JSON disagree, the app is serving something other than this file.

How we undo it: N/A — read-only.

---
