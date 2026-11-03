#!/usr/bin/env bash
# Deploy one environment from images already built by CI.
#
#   deploy/deploy.sh <production|staging> <image-tag>
#
# Steps: Caddy up -> pull images -> database up -> migrations -> new containers
# (waits for healthchecks) -> on failure, back to the previous tag.
# Rollback by hand: deploy/deploy.sh production <older-tag>
set -euo pipefail

ENVIRONMENT="${1:?usage: deploy.sh <production|staging> <image-tag>}"
TAG="${2:?usage: deploy.sh <production|staging> <image-tag>}"
case "$ENVIRONMENT" in production | staging) ;; *) echo "unknown environment: $ENVIRONMENT" >&2; exit 2 ;; esac

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$DEPLOY_DIR")"
ENV_FILE="$ROOT/env/$ENVIRONMENT.env"
EDGE_ENV="$ROOT/env/edge.env"
STATE_FILE="$ROOT/state/$ENVIRONMENT.tag"
for f in "$ENV_FILE" "$EDGE_ENV"; do
  [[ -f "$f" ]] || { echo "missing $f (copy it from deploy/env/*.example)" >&2; exit 2; }
done
mkdir -p "$ROOT/state"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }

app() {
  IMAGE_TAG="$1" docker compose -p "ups-kulka-$ENVIRONMENT" \
    -f "$DEPLOY_DIR/compose.prod.yml" --env-file "$ENV_FILE" "${@:2}"
}

edge_up() {
  docker network inspect edge >/dev/null 2>&1 || docker network create edge >/dev/null
  # shellcheck disable=SC1090
  EDGE_SITES="$(set -a; . "$EDGE_ENV"; echo "${EDGE_SITES:-production}")"
  rm -rf "$DEPLOY_DIR/edge/sites" && mkdir -p "$DEPLOY_DIR/edge/sites"
  for site in $EDGE_SITES; do
    cp "$DEPLOY_DIR/edge/sites-available/$site.caddy" "$DEPLOY_DIR/edge/sites/"
  done
  local edge=(docker compose -p ups-kulka-edge -f "$DEPLOY_DIR/edge/compose.yml" --env-file "$EDGE_ENV")
  "${edge[@]}" up -d --wait
  "${edge[@]}" exec -T caddy caddy reload --config /etc/caddy/Caddyfile
}

prepare_dirs() {
  local data_dir
  # shellcheck disable=SC1090
  data_dir="$(set -a; . "$ENV_FILE"; echo "${DATA_DIR:?DATA_DIR is not set in $ENV_FILE}")"
  # Through Docker, so the deploy user needs no sudo; the API runs as uid 10001.
  docker run --rm -v "$data_dir:/d" alpine:3.22 \
    sh -c 'mkdir -p /d/media /d/backups && chown 10001:10001 /d/media'
}

# Every step checks its own result: errexit does not apply inside a function used in `if`.
release() {
  local tag="$1"
  log "pull $tag"
  app "$tag" pull web api migrate || return 1
  app "$tag" up -d --wait db || return 1
  log "migrations"
  app "$tag" run --rm migrate || return 1
  log "start containers"
  app "$tag" up -d --wait --wait-timeout 180 --remove-orphans web api db backup || return 1
}

log "deploy $ENVIRONMENT $TAG"
prepare_dirs
edge_up
PREVIOUS="$(cat "$STATE_FILE" 2>/dev/null || true)"

if release "$TAG"; then
  echo "$TAG" >"$STATE_FILE"
  docker image prune -f >/dev/null
  log "done: $ENVIRONMENT is on $TAG"
  exit 0
fi

log "deploy of $TAG failed"
app "$TAG" logs --tail 80 api web || true
if [[ -n "$PREVIOUS" && "$PREVIOUS" != "$TAG" ]]; then
  # Migrations only add things (AGENTS.md section 5), so the previous code runs on the new schema.
  log "rolling back to $PREVIOUS"
  app "$PREVIOUS" up -d --wait --wait-timeout 180 web api && log "rolled back to $PREVIOUS"
fi
exit 1
