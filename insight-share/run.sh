#!/usr/bin/env bash
# Single-click launcher for the insight-unified container image.
# Usage:  ./run.sh            (start; idempotent)
#         ./run.sh down       (stop + remove)
#         ./run.sh logs       (tail logs)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

IMAGE_TAG="insight-unified:local-build"

export INSIGHT_UNIFIED_IMAGE="$IMAGE_TAG"
export DASHBOARD_MOCK_AUTH="${DASHBOARD_MOCK_AUTH:-0}"
export AUTH_BASE_URL="${AUTH_BASE_URL:-http://127.0.0.1:8101}"
export TP_AUTHENTICATION_SESSION_URL="${TP_AUTHENTICATION_SESSION_URL:-http://127.0.0.1:8101/api/auth/session}"
export TP_TRUSTED_INTERNAL_ORIGINS="${TP_TRUSTED_INTERNAL_ORIGINS:-http://127.0.0.1:8080,http://127.0.0.1:8101}"
export TP_BN_MANAGER_URL="${TP_BN_MANAGER_URL:-http://127.0.0.1:8108}"
export TP_ENV="${TP_ENV:-development}"
export INSIGHT_SECRETS_DIR="${INSIGHT_SECRETS_DIR:-$HERE/secrets-empty}"

case "${1:-up}" in
  up)
    if ! docker image inspect "$IMAGE_TAG" >/dev/null 2>&1; then
      echo "Image $IMAGE_TAG not found. Loading from insight-unified.image.tar..."
      docker load -i insight-unified.image.tar
    fi
    if [ -z "${AUTH_JWT_SECRET:-}" ] && [ ! -f .env ]; then
      SECRET="$(tr -dc 'A-Za-z0-9_-' < /dev/urandom 2>/dev/null | head -c 48 || true)"
      if [ -z "$SECRET" ]; then
        SECRET="local-jwt-secret-${IMAGE_TAG##*:}-$(date +%s)-change-for-production"
      fi
      umask 077
      printf 'AUTH_JWT_SECRET=%s\n' "$SECRET" > .env
    fi
    docker compose -f docker-compose.yaml up -d --wait --wait-timeout 120
    echo
    echo "=== insight-unified is starting ==="
    echo "Dashboard : http://127.0.0.1:8080/dashboard/"
    echo "Login     : http://127.0.0.1:8080/modules/authentication  (Admin / Admin)"
    echo "Readiness : http://127.0.0.1:8080/readyz"
    echo
    echo "Default admin: username=Admin password=Admin (CHANGE AFTER FIRST LOGIN)"
    echo "Container healthy. Run './run.sh logs' to follow logs."
    ;;
  down)
    docker compose -f docker-compose.yaml down
    ;;
  logs)
    docker compose -f docker-compose.yaml logs --tail=100 -f
    ;;
  *)
    echo "usage: $0 [up|down|logs]" >&2
    exit 2
    ;;
esac
