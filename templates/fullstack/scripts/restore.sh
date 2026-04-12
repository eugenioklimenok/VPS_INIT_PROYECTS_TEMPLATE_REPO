#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-dev}"
BACKUP_FILE="${2:-}"
ENV_FILE="env/.env.${ENVIRONMENT}"

test -f "$ENV_FILE" || { echo "Missing env file: $ENV_FILE" >&2; exit 1; }
test -n "$BACKUP_FILE" || { echo "Usage: ./scripts/restore.sh <env> <backup-file>" >&2; exit 1; }
test -f "$BACKUP_FILE" || { echo "Missing backup file: $BACKUP_FILE" >&2; exit 1; }

set -a
source "$ENV_FILE"
set +a

gunzip -c "$BACKUP_FILE" | docker compose --env-file "$ENV_FILE" exec -T db \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo "Restore completed from: $BACKUP_FILE"
