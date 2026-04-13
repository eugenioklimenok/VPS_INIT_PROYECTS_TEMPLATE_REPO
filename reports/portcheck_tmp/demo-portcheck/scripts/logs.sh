#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-dev}"
ENV_FILE="env/.env.${ENVIRONMENT}"

test -f "$ENV_FILE" || { echo "Missing env file: $ENV_FILE" >&2; exit 1; }

docker compose --env-file "$ENV_FILE" logs -f --tail=200
