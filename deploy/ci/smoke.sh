#!/usr/bin/env bash
# Checks a deployed site from the outside: storefront, API through Caddy, sitemap.
set -euo pipefail
base="${1:?usage: smoke.sh https://site}"
for path in / /kulky /api/v1/catalog/tags /robots.txt /sitemap.xml; do
  for attempt in 1 2 3 4 5; do
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$base$path" || true)"
    [[ "$code" == 200 ]] && break
    sleep 6
  done
  echo "$code $path"
  [[ "$code" == 200 ]] || { echo "smoke test failed on $path" >&2; exit 1; }
done
