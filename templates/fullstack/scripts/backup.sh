#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-dev}"
ENV_FILE="env/.env.${ENVIRONMENT}"

test -f "$ENV_FILE" || { echo "Missing env file: $ENV_FILE" >&2; exit 1; }

set -a
source "$ENV_FILE"
set +a

TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
APP_BACKUP_FILE="backups/${PROJECT_NAME}_app_pg_${TIMESTAMP}.sql.gz"
N8N_BACKUP_FILE="backups/${PROJECT_NAME}_n8n_pg_${TIMESTAMP}.sql.gz"

mkdir -p backups

docker compose --env-file "$ENV_FILE" exec -T db \
  pg_dump -U "$APP_DB_USER" -d "$APP_DB_NAME" | gzip > "$APP_BACKUP_FILE"

docker compose --env-file "$ENV_FILE" exec -T db \
  pg_dump -U "$N8N_DB_USER" -d "$N8N_DB_NAME" | gzip > "$N8N_BACKUP_FILE"

echo "Backup created: $APP_BACKUP_FILE"
echo "Backup created: $N8N_BACKUP_FILE"
