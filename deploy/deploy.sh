#!/usr/bin/env bash
# Deploy the checked-out branch on the EC2 server: pull, install, restart, and
# fail unless the app is reading from the database again.
set -euo pipefail

cd "$(dirname "$0")/.."

git pull --ff-only
.venv/bin/pip install --quiet -r requirements.txt
sudo systemctl restart career-platform

for _ in $(seq 30); do
    if curl -s http://127.0.0.1:8000/api/profile | grep -q '"source":"database"'; then
        echo "Deployed $(git rev-parse --short HEAD); the app is reading the database."
        exit 0
    fi
    sleep 1
done

echo "The app isn't reading the database 30 s after restart. Check: journalctl -u career-platform -n 50" >&2
exit 1
