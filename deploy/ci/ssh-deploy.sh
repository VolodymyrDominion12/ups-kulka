#!/usr/bin/env bash
# Copies deploy/ to the VPS and runs deploy/deploy.sh there (called from .github/workflows/deploy.yml).
# Env: SSH_HOST SSH_USER SSH_PORT SSH_PRIVATE_KEY SSH_KNOWN_HOSTS DEPLOY_ENV IMAGE_TAG
#      GHCR_USER GHCR_TOKEN (short-lived GITHUB_TOKEN, used for docker pull and then logged out)
set -euo pipefail

install -m 700 -d ~/.ssh
printf '%s\n' "$SSH_PRIVATE_KEY" >~/.ssh/deploy_key && chmod 600 ~/.ssh/deploy_key
printf '%s\n' "$SSH_KNOWN_HOSTS" >~/.ssh/known_hosts
ssh_cmd=(ssh -i ~/.ssh/deploy_key -p "${SSH_PORT:-22}" -o BatchMode=yes "$SSH_USER@$SSH_HOST")

tar -czf - deploy | "${ssh_cmd[@]}" "mkdir -p /opt/ups-kulka && tar -xzf - -C /opt/ups-kulka"

printf '%s' "$GHCR_TOKEN" | "${ssh_cmd[@]}" \
  "docker login ghcr.io -u '$GHCR_USER' --password-stdin >/dev/null \
   && /opt/ups-kulka/deploy/deploy.sh '$DEPLOY_ENV' '$IMAGE_TAG'; \
   rc=\$?; docker logout ghcr.io >/dev/null; exit \$rc"
