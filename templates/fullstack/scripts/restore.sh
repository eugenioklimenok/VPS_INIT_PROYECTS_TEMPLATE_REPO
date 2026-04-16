#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-dev}"
BACKUP_FILE="${2:-}"
TARGET="${3:-app}"
ENV_FILE="env/.env.${ENVIRONMENT}"

test -f "$ENV_FILE" || { echo "Missing env file: $ENV_FILE" >&2; exit 1; }
test -n "$BACKUP_FILE" || { echo "Usage: ./scripts/restore.sh <env> <backup-file> [app|n8n]" >&2; exit 1; }
test -f "$BACKUP_FILE" || { echo "Missing backup file: $BACKUP_FILE" >&2; exit 1; }

set -a
source "$ENV_FILE"
set +a

case "$TARGET" in
  app)
    DB_USER="$APP_DB_USER"
    DB_NAME="$APP_DB_NAME"
    ;;
  n8n)
    DB_USER="$N8N_DB_USER"
    DB_NAME="$N8N_DB_NAME"
    ;;
  *)
    echo "Invalid target '$TARGET'. Use app or n8n." >&2
    exit 1
    ;;
esac

gunzip -c "$BACKUP_FILE" | docker compose --env-file "$ENV_FILE" exec -T db \
  psql -U "$DB_USER" -d "$DB_NAME"

echo "Restore completed from: $BACKUP_FILE (target: $TARGET)"
