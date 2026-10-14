#!/usr/bin/env bash
# Updates the portfolio on the server: pulls the latest commit, and only if the Caddy
# block changed, validates the whole Caddy config and reloads it (no downtime for TaskFlow).
# An invalid block is rolled back instead of loaded. Finally checks the site over HTTPS.
# Usage (on the server):   bash ~/caddy-sites/portfolio/deploy/update.sh
set -euo pipefail

cd "$(dirname "$0")/.."

CADDY=(docker exec gorevtakip-caddy-1 caddy)
CONFIG=(--config /etc/caddy/Caddyfile --adapter caddyfile)

before="$(git rev-parse HEAD)"
echo "==> Pulling the latest version"
git pull --ff-only

if git diff --quiet "$before" HEAD -- deploy/portfolio.caddy; then
  echo "==> Caddy block unchanged, no reload needed"
else
  echo "==> Caddy block changed: validating"
  if ! "${CADDY[@]}" validate "${CONFIG[@]}"; then
    # Keep only a known-good block on disk: Caddy rereads it on every restart, and a
    # broken block would then stop TaskFlow too.
    git reset -q --hard "$before"
    echo "✗ The new Caddy block is invalid (see above). Rolled back to $(git log -1 --format='%h %s')." >&2
    echo "  Nothing was reloaded; the site and TaskFlow keep running. Fix the block, push, run again." >&2
    exit 1
  fi
  echo "==> Reloading Caddy"
  "${CADDY[@]}" reload "${CONFIG[@]}"
fi

# First site address in the block, e.g. "example.com" from "example.com, www.example.com {"
host="$(sed -n 's/^\([a-z0-9][^ ,{]*\)[ ,].*{$/\1/p' deploy/portfolio.caddy | head -n1)"
echo "==> Waiting for https://$host/"
for attempt in $(seq 1 30); do
  code="$(curl -sS -o /dev/null -w '%{http_code}' -m 5 "https://$host/" 2>/dev/null || true)"
  if [[ "$code" == "200" ]]; then
    echo "✓ Live: https://$host/  ($(git log -1 --format='%h %s'))"
    exit 0
  fi
  sleep 2
done

echo "✗ https://$host/ did not answer with 200 within 60 seconds (last: ${code:-none})." >&2
echo "  Caddy log:  docker logs --tail 30 gorevtakip-caddy-1" >&2
exit 1
