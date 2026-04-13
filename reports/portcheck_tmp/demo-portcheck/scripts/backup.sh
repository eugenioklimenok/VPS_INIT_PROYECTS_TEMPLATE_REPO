#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-dev}"
ENV_FILE="env/.env.${ENVIRONMENT}"

test -f "$ENV_FILE" || { echo "Missing env file: $ENV_FILE" >&2; exit 1; }

set -a
source "$ENV_FILE"
set +a

TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
BACKUP_FILE="backups/${PROJECT_NAME}_pg_${TIMESTAMP}.sql.gz"

mkdir -p backups

docker compose --env-file "$ENV_FILE" exec -T db \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" | gzip > "$BACKUP_FILE"

echo "Backup created: $BACKUP_FILE"
